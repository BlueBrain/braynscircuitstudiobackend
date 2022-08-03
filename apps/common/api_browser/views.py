from django.views.generic import TemplateView

from common.api_browser.utils import get_menu_items


class APIBrowserTemplateView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super(APIBrowserTemplateView, self).get_context_data(**kwargs)
        context.update(
            {
                "menu_items": get_menu_items(),
            }
        )
        return context


class IndexView(APIBrowserTemplateView):
    template_name = "api_browser/index.html"


class MethodView(APIBrowserTemplateView):
    template_name = "api_browser/method.html"

    def get_context_data(self, **kwargs):
        context = super(MethodView, self).get_context_data(**kwargs)
        context.update(self.retrieve_method_context_data())
        return context

    def retrieve_method_context_data(self):
        return {
            # fixme this should be generic (retrieve from websocket_urlpatterns?)
            "method": CircuitStudioConsumer.get_method(self.kwargs.get("method_name")),
        }
