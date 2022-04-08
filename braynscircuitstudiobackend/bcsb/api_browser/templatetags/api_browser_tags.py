from django import template

from bcsb.consumers import CircuitStudioConsumer

register = template.Library()


@register.inclusion_tag("api_browser/templatetags/render_method_doc_entry.html")
def render_method_doc_entry(method_name):
    method = CircuitStudioConsumer.get_method(method_name)
    return {"method": method}


@register.inclusion_tag("api_browser/templatetags/render_schema_fields_docs.html")
def render_schema_fields_docs(fields_docs):
    return {"fields_docs": fields_docs}
