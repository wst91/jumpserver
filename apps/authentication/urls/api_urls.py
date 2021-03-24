# coding:utf-8
#
from django.urls import path
from rest_framework.routers import DefaultRouter

from .. import api

app_name = 'authentication'
router = DefaultRouter()
router.register('access-keys', api.AccessKeyViewSet, 'access-key')
router.register('sso', api.SSOViewSet, 'sso')
router.register('connection-token', api.UserConnectionTokenViewSet, 'connection-token')


urlpatterns = [
    # path('token/', api.UserToken.as_view(), name='user-token'),
    path('wecom/qr/bind/', api.WeComQRBindApi.as_view(), name='wecom-qr-bind'),
    path('wecom/qr/login/', api.WeComQRLoginApi.as_view(), name='wecom-qr-login'),
    path('wecom/qr/bind/<uuid:user_id>/callback/', api.WeComQRBindCallbackApi.as_view(), name='wecom-qr-bind-callback'),
    path('wecom/qr/login/callback/', api.WeComQRLoginCallbackApi.as_view(), name='wecom-qr-login-callback'),

    path('auth/', api.TokenCreateApi.as_view(), name='user-auth'),
    path('tokens/', api.TokenCreateApi.as_view(), name='auth-token'),
    path('mfa/challenge/', api.MFAChallengeApi.as_view(), name='mfa-challenge'),
    path('otp/verify/', api.UserOtpVerifyApi.as_view(), name='user-otp-verify'),
    path('login-confirm-ticket/status/', api.TicketStatusApi.as_view(), name='login-confirm-ticket-status'),
    path('login-confirm-settings/<uuid:user_id>/', api.LoginConfirmSettingUpdateApi.as_view(), name='login-confirm-setting-update')
]

urlpatterns += router.urls
