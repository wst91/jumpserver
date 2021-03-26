import urllib

from django.contrib.auth import login
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.models import User
from common.exceptions import JMSObjectDoesNotExist
from common.utils import get_logger
from common.utils.django import reverse, get_object_or_none
from common.message.backends.wecom import URL
from common.message.backends.wecom import WeCom
from authentication.errors import WeComCodeInvalid, WeComBindAlready

logger = get_logger(__file__)


class WeComQRBaseApi(APIView):
    def get(self, request: Request):
        redirect_uri = self.get_redirect_uri()

        params = {
            'appid': 'ww918354e3468dc0cc',
            'agentid': '1000002',
            'redirect_uri': redirect_uri
        }
        url = URL.QR_CONNECT + '?' + urllib.parse.urlencode(params)
        return Response({'url': url})

    def get_redirect_uri(self):
        raise NotImplementedError


class WeComQRBindApi(WeComQRBaseApi):
    permission_classes = (IsAuthenticated,)

    def get_redirect_uri(self):
        user = self.request.user
        redirect_uri = reverse('api-auth:wecom-qr-bind-callback', kwargs={'user_id': user.id}, external=True)
        return redirect_uri


class WeComQRLoginApi(WeComQRBaseApi):
    def get_redirect_uri(self):
        redirect_uri = reverse('api-auth:wecom-qr-login-callback', external=True)
        return redirect_uri


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


class WeComQRBindCallbackApi(APIView):
    def get(self, request: Request, user_id):
        code = request.query_params.get('code')
        state = request.query_params.get('state')

        user = get_object_or_none(User, id=user_id)
        if user is None:
            logger.error(f'WeComQR bind callback error, user_id invalid: user_id={user_id}')
            raise JMSObjectDoesNotExist(code='user_not_exist')

        if user.wecom_id:
            raise WeComBindAlready

        wecom = WeCom(
            corpid=settings.WECOM_CORPID,
            corpsecret=settings.WECOM_CORPSECRET,
            agentid=settings.WECOM_AGENTID
        )
        wecom_userid, _ = wecom.get_user_id_by_code(code)
        if not wecom_userid:
            raise WeComCodeInvalid

        user.wecom_id = wecom_userid
        user.save()

        return Response()


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
