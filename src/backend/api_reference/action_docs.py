import logging
from typing import Optional

from marshmallow import Schema, fields, post_load
from marshmallow.fields import Field

from backend.jsonrpc.actions import Action
from backend.main_websocket_handler import ActionFinder
from version import VERSION

logger = logging.getLogger(__name__)


class FieldtypeSchema(Schema):
    required = fields.Boolean()
    meta = fields.Dict(
        allow_none=True,
        required=False,
    )

    @post_load
    def remove_skip_values(self, data, *args, **kwargs):
        def should_skip(value):
            result = value is None or (isinstance(value, dict) and not value)
            logger.debug(f"should_skip {value=} {result=}")
            return result

        return {key: value for key, value in data.items() if not should_skip(value)}


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
        keys=fields.String(),
        values=fields.Nested(FieldtypeSchema()),
    )
    response_data = fields.Dict(
        required=False,
        allow_none=True,
        keys=fields.String(),
        values=fields.Nested(FieldtypeSchema()),
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


def _get_schema_docs(schema_class: type[Schema]):
    schema: Schema = schema_class()
    schema_fields = schema.fields
    result = {}
    for field_name, field in schema_fields.items():
        result[field_name] = _get_field_doc(field)
    return result


def _get_request_params(action: type[Action]):
    schema_class: Optional[type[Schema]] = action.request_schema
    if schema_class is None:
        return None
    return _get_schema_docs(schema_class)


def _get_response_data(action: type[Action]):
    schema_class: Optional[type[Schema]] = action.response_schema
    if schema_class is None:
        return None
    return _get_schema_docs(schema_class)


def get_action_docs(action: type[Action]):

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
