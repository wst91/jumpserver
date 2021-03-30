import urllib

from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from users.utils import is_auth_password_time_valid
from users.models import User
from common.utils import get_logger
from common.utils.random import random_string
from common.utils.django import reverse, get_object_or_none
from common.message.backends.wecom import URL
from common.message.backends.wecom import WeCom
from authentication import errors
from authentication.mixins import AuthMixin

logger = get_logger(__file__)


WECOM_STATE_SESSION_KEY = '_wecom_state'


class WeComQRMixin(APIView):
    def verify_state(self):
        state = self.request.query_params.get('state')
        session_state = self.request.session.get(WECOM_STATE_SESSION_KEY)
        if state != session_state:
            return False
        return True

    def get_verify_state_failed_response(self, redirect_uri):
        msg = _("You've been hacked")
        return self.get_failed_reponse(redirect_uri, msg, msg)

    def get_qr_url(self, redirect_uri):
        state = random_string(16)
        self.request.session[WECOM_STATE_SESSION_KEY] = state

        params = {
            'appid': settings.WECOM_CORPID,
            'agentid': settings.WECOM_AGENTID,
            'state': state,
            'redirect_uri': redirect_uri,
        }
        url = URL.QR_CONNECT + '?' + urllib.parse.urlencode(params)
        return url

    def get_qr_url_response(self, redirect_uri):
        url = self.get_qr_url(redirect_uri)
        return Response({'url': url})

    def get_success_reponse(self, redirect_url, title, msg):
        ok_flash_msg_url = reverse('authentication:wecom-bind-success-flash-msg')
        ok_flash_msg_url += '?' + urllib.parse.urlencode({
            'redirect_url': redirect_url,
            'title': title,
            'msg': msg
        })
        return HttpResponseRedirect(ok_flash_msg_url)

    def get_failed_reponse(self, redirect_url, title, msg):
        failed_flash_msg_url = reverse('authentication:wecom-bind-failed-flash-msg')
        failed_flash_msg_url += '?' + urllib.parse.urlencode({
            'redirect_url': redirect_url,
            'title': title,
            'msg': msg
        })
        return HttpResponseRedirect(failed_flash_msg_url)

    def get_already_bound_response(self, redirect_url):
        msg = _('WeCom is already bound')
        response = self.get_failed_reponse(redirect_url, msg, msg)
        return response


class WeComQRBindApi(WeComQRMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        user = request.user
        redirect_url = request.query_params.get('redirect_url')

        if not is_auth_password_time_valid(request.session):
            bind_start = reverse('authentication:wecom-bind-start')
            bind_start += '?' + urllib.parse.urlencode({
                'next': redirect_url
            })
            return HttpResponseRedirect(bind_start)

        redirect_uri = reverse('api-auth:wecom-qr-bind-callback', kwargs={'user_id': user.id}, external=True)
        redirect_uri += '?' + urllib.parse.urlencode({'redirect_url': redirect_url})

        url = self.get_qr_url(redirect_uri)
        return HttpResponseRedirect(url)


class WeComQRLoginApi(WeComQRMixin, APIView):
    permission_classes = (AllowAny,)

    def get(self,  request: Request):
        referer = request.query_params.get('referer')

        redirect_uri = reverse('api-auth:wecom-qr-login-callback', external=True)
        redirect_uri += '?' + urllib.parse.urlencode({'referer': referer})

        url = self.get_qr_url(redirect_uri)
        return HttpResponseRedirect(url)


class WeComQRLoginCallbackApi(AuthMixin, WeComQRMixin, APIView):
    permission_classes = (AllowAny,)

    def get(self, request: Request):
        code = request.query_params.get('code')
        redirect_url = request.query_params.get('redirect_url')
        login_url = reverse('authentication:login')

        if not self.verify_state():
            return self.get_verify_state_failed_response(redirect_url)

        wecom = WeCom(
            corpid=settings.WECOM_CORPID,
            corpsecret=settings.WECOM_CORPSECRET,
            agentid=settings.WECOM_AGENTID
        )
        wecom_userid, _ = wecom.get_user_id_by_code(code)
        if not wecom_userid:
            # 正常流程不会出这个错误，hack 行为
            msg = _('Failed to get user from WeCom')
            response = self.get_failed_reponse(login_url, title=msg, msg=msg)
            return response

        user = get_object_or_none(User, wecom_id=wecom_userid)
        if user is None:
            title = _('WeCom has no bound user')
            msg = _('Please login with a password and then bind the WoCom')
            response = self.get_failed_reponse(login_url, title=title, msg=msg)
            return response

        try:
            self.check_wecom_auth(user)
        except errors.AuthFailedError as e:
            self.set_login_failed_mark()
            msg = e.msg
            response = self.get_failed_reponse(login_url, title=msg, msg=msg)
            return response

        return self.redirect_to_guard_view()


class WeComQRBindCallbackApi(WeComQRMixin, APIView):

    def get(self, request: Request, user_id):
        code = request.query_params.get('code')
        redirect_url = request.query_params.get('redirect_url')

        if not self.verify_state():
            return self.get_verify_state_failed_response(redirect_url)

        user = get_object_or_none(User, id=user_id)
        if user is None:
            logger.error(f'WeComQR bind callback error, user_id invalid: user_id={user_id}')
            msg = _('Invalid user_id')
            response = self.get_failed_reponse(redirect_url, msg, msg)
            return response

        if user.wecom_id:
            response = self.get_already_bound_response(redirect_url)
            return response

        wecom = WeCom(
            corpid=settings.WECOM_CORPID,
            corpsecret=settings.WECOM_CORPSECRET,
            agentid=settings.WECOM_AGENTID
        )
        wecom_userid, __ = wecom.get_user_id_by_code(code)
        if not wecom_userid:
            msg = _('WeCom query user failed')
            response = self.get_failed_reponse(redirect_url, msg, msg)
            return response

        user.wecom_id = wecom_userid
        user.save()

        msg = _('Binding WeCom successfully')
        response = self.get_success_reponse(redirect_url, msg, msg)
        return response
