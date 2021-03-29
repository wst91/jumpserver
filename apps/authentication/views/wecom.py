from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.decorators.cache import never_cache
from django.views.generic.base import TemplateView, RedirectView


@method_decorator(never_cache, name='dispatch')
class FlashWeComBindSucceedMsgView(TemplateView):
    template_name = 'flash_message_standalone.html'

    def get(self, request, *args, **kwargs):
        title = request.GET.get('title')
        msg = request.GET.get('msg')

        context = {
            'title': title or _('Binding WeCom successfully'),
            'messages': msg or _('Binding WeCom successfully'),
            'interval': 5,
            'redirect_url': request.GET.get('redirect_url'),
            'auto_redirect': True,
        }
        return self.render_to_response(context)


@method_decorator(never_cache, name='dispatch')
class FlashWeComBindFailedMsgView(TemplateView):
    template_name = 'flash_message_standalone.html'

    def get(self, request, *args, **kwargs):
        title = request.GET.get('title')
        msg = request.GET.get('msg')

        context = {
            'title': title or _('Binding WeCom failed'),
            'messages': msg or _('Binding WeCom failed'),
            'interval': 5,
            'redirect_url': request.GET.get('redirect_url'),
            'auto_redirect': True,
        }
        return self.render_to_response(context)
