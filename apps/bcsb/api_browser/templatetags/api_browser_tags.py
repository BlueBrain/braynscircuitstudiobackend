from django import template

from common.jsonrpc.jsonrpc_method import JSONRPCMethod

register = template.Library()


@register.inclusion_tag("api_browser/templatetags/render_method_doc_entry.html")
def render_method_doc_entry(method: JSONRPCMethod):
    return {
        "method": method,
    }


@register.inclusion_tag("api_browser/templatetags/render_schema_fields_docs.html")
def render_schema_fields_docs(fields_docs):
    return {
        "fields_docs": fields_docs,
    }
