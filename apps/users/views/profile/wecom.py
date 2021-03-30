import urllib

from django.urls import reverse

from .password import UserVerifyPasswordView


class WeComEnableStartView(UserVerifyPasswordView):

    def get_success_url(self):
        referer = self.request.META.get('HTTP_REFERER')
        next_url = self.request.GET.get("next")

        success_url = reverse('api-auth:wecom-qr-bind')

        success_url += '?' + urllib.parse.urlencode({
            'redirect_url': next_url or referer
        })

        return success_url
