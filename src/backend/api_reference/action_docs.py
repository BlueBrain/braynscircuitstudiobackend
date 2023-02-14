from typing import Type, Optional

from marshmallow import Schema, fields
from marshmallow.fields import Field

from backend.jsonrpc.actions import Action
from backend.main_websocket_handler import ActionFinder
from version import VERSION


class ActionReferenceSchema(Schema):
    name = fields.String()
    description = fields.String(
        required=False,
        default="",
        allow_none=True,
    )
    request_params = fields.Dict(
        required=False,
        allow_none=True,
    )
    response_data = fields.Dict(
        required=False,
        allow_none=True,
    )


class ActionDocsSchema(Schema):
    action_reference = fields.List(
        cls_or_instance=fields.Nested(
            nested=ActionReferenceSchema(),
        ),
    )
    version = fields.String()


def _get_field_doc(field: Field):
    return {
        "meta": field.metadata,
        "required": field.required,
    }


def _get_schema_docs(schema_class: Type[Schema]):
    schema: Schema = schema_class()
    schema_fields = schema.fields
    result = {}
    for field_name, field in schema_fields.items():
        result[field_name] = _get_field_doc(field)
    return result


def _get_request_params(action: Type[Action]):
    schema_class: Optional[Type[Schema]] = action.request_schema
    if schema_class is None:
        return None
    return _get_schema_docs(schema_class)


def _get_response_data(action: Type[Action]):
    schema_class: Optional[Type[Schema]] = action.response_schema
    if schema_class is None:
        return None
    return _get_schema_docs(schema_class)


def get_action_docs(action: Type[Action]):

    return {
        "name": action.name,
        "description": action.__doc__,
        "request_params": _get_request_params(action),
        "response_data": _get_response_data(action),
    }


def get_action_reference():
    actions = [
        ActionFinder.get_action(action_name)
        for action_name in ActionFinder.get_available_action_names()
    ]
    action_reference = []
    for action in actions:
        action_reference.append(get_action_docs(action))
    return action_reference


def get_api_reference_json():
    data = {
        "action_reference": get_action_reference(),
        "version": VERSION,
    }
    schema = ActionDocsSchema().load(data=data)
    return schema
