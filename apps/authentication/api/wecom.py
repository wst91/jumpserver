import urllib

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.models import User
from common.utils.django import reverse
from common.message.backends.wecom import URL


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
        user_id = request.kwargs['user_id']
        code = request.query_params.get('code')
        state = request.query_params.get('state')

        print(f'wecom test {code} {state}')
        return Response()


class WeComQRBindCallbackApi(APIView):
    def get(self, request: Request):
        user_id = request.kwargs['user_id']
        code = request.query_params.get('code')
        state = request.query_params.get('state')

        user = User.objects.get(id=user_id)
        print(f'wecom test {code} {state}')
        return Response()
