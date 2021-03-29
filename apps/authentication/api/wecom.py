import urllib

from django.conf import settings
from django.http.response import HttpResponseRedirect
from django.utils.translation import gettext_lazy as _
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.utils import is_auth_password_time_valid
from users.models import User
from common.exceptions import JMSObjectDoesNotExist
from common.utils import get_logger
from common.utils.django import reverse, get_object_or_none
from common.message.backends.wecom import URL
from common.message.backends.wecom import WeCom
from authentication.errors import WeComCodeInvalid, WeComBindAlready

logger = get_logger(__file__)


class WeComQRMixin:
    def get_qr_url(self, redirect_uri):
        params = {
            'appid': 'ww918354e3468dc0cc',
            'agentid': '1000002',
            'redirect_uri': redirect_uri
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


class WeComQRBindApi(WeComQRMixin, APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request):
        user = request.user
        referer = request.query_params.get('referer')

        # if user.wecom_id:
        #     raise WeComBindAlready

        if not is_auth_password_time_valid(request.session):
            bind_start = reverse('authentication:wecom-bind-start')
            bind_start += '?' + urllib.parse.urlencode({
                'next': referer
            })
            return HttpResponseRedirect(bind_start)

        redirect_uri = reverse('api-auth:wecom-qr-bind-callback', kwargs={'user_id': user.id}, external=True)
        redirect_uri += '?' + urllib.parse.urlencode({'referer': referer})

        url = self.get_qr_url(redirect_uri)
        return HttpResponseRedirect(url)


class WeComQRLoginApi(WeComQRMixin, APIView):

    def get(self,  request: Request):
        redirect_uri = reverse('api-auth:wecom-qr-login-callback', external=True)
        response = self.get_qr_url_response(redirect_uri)
        return response


class WeComQRLoginCallbackApi(APIView):
    def get(self, request: Request):
        code = request.query_params.get('code')
        state = request.query_params.get('state')

        wecom = WeCom(
            corpid=settings.WECOM_CORPID,
            corpsecret=settings.WECOM_CORPSECRET,
            agentid=settings.WECOM_AGENTID
        )
        wecom_userid, _ = wecom.get_user_id_by_code(code)
        if not wecom_userid:
            raise WeComCodeInvalid

        user = get_object_or_none(User, wecom_id=wecom_userid)
        if user is None:
            logger.error(f'WeComQR bind callback error, wecom_id invalid: wecom_id={wecom_userid}')
            raise JMSObjectDoesNotExist(code='user_not_exist')

        logger(user)

        return Response()


class WeComQRBindCallbackApi(WeComQRMixin, APIView):

    def get(self, request: Request, user_id):
        code = request.query_params.get('code')
        state = request.query_params.get('state')
        referer = request.query_params.get('referer')

        user = get_object_or_none(User, id=user_id)
        if user is None:
            logger.error(f'WeComQR bind callback error, user_id invalid: user_id={user_id}')
            msg = _('Invalid user_id')
            response = self.get_failed_reponse(referer, msg, msg)
            return response

        if user.wecom_id:
            msg = _('WeCom is already bound')
            response = self.get_failed_reponse(referer, msg, msg)
            return response

        wecom = WeCom(
            corpid=settings.WECOM_CORPID,
            corpsecret=settings.WECOM_CORPSECRET,
            agentid=settings.WECOM_AGENTID
        )
        wecom_userid, __ = wecom.get_user_id_by_code(code)
        if not wecom_userid:
            msg = _('WeCom query user failed')
            response = self.get_failed_reponse(referer, msg, msg)
            return response

        user.wecom_id = wecom_userid
        user.save()

        msg = _('Binding WeCom successfully')
        response = self.get_success_reponse(referer, msg, msg)
        return response


def init(corpsecret):
    from settings.models import Setting

    value = {
        'corpid': 'ww918354e3468dc0cc',
        'agentid': '1000002',
        'corpsecret': corpsecret
    }
    Setting.update_or_create('WECOM_CORPID', value='ww918354e3468dc0cc', encrypted=False)
    Setting.update_or_create('WECOM_AGENTID', value='1000002', encrypted=False)
    Setting.update_or_create('WECOM_CORPSECRET', value=corpsecret, encrypted=True)
