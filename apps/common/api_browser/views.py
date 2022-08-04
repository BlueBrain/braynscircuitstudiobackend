from django.views.generic import TemplateView

from common.api_browser.utils import get_menu


class APIBrowserTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(APIBrowserTemplateView, self).get_context_data(**kwargs)
        context.update(
            {
                "menu": get_menu(),
            }
        )
        return context


class IndexView(APIBrowserTemplateView):
    template_name = "api_browser/index.html"
