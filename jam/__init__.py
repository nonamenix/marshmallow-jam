import typing as typing
import logging
from dataclasses import dataclass

from marshmallow import fields, post_load
from marshmallow.schema import SchemaMeta as BaseSchemaMeta, BaseSchema, with_metaclass

import datetime as dt
import uuid
import decimal


logger = logging.getLogger(__name__)


BASIC_TYPES_MAPPING = {
    str: fields.String,
    float: fields.Float,
    bool: fields.Boolean,
    int: fields.Integer,
    uuid.UUID: fields.UUID,
    decimal.Decimal: fields.Decimal,
    dt.datetime: fields.DateTime,
    dt.time: fields.Time,
    dt.date: fields.Date,
    dt.timedelta: fields.TimeDelta,
}


NoneType = type(None)
UnionType = type(typing.Union)


class JamException(Exception):
    pass


class NotValidAnnotation(JamException):
    pass


# todo: flat_sequence? set, tuple, etc
def is_many(annotation: typing.Type) -> bool:
    return hasattr(annotation, "__origin__") and annotation.__origin__ is list


def unpack_many(annotation: typing.Type) -> bool:
    return annotation.__args__[0]


def is_optional(annotation: typing.Type) -> bool:
    return (
        hasattr(annotation, "__origin__")
        and annotation.__origin__ is typing.Union
        and len(annotation.__args__) == 2
        and NoneType in annotation.__args__
    )


def unpack_optional_type(annotation: typing.Union) -> typing.Type:
    """Optional[Type] -> Type"""
    return next(t for t in annotation.__args__ if t is not NoneType)


def get_marshmallow_field(annotation):
    field = None

    opts = {}
    args = []
    if is_optional(annotation):
        annotation = unpack_optional_type(annotation)
    else:
        opts["required"] = True

    if is_many(annotation):
        opts["many"] = True
        annotation = unpack_many(annotation)

    if annotation is list:
        field = fields.Raw
        opts["many"] = True

    if isinstance(annotation, SchemaMeta):
        args.append(annotation)
        field = fields.Nested

    field = field or BASIC_TYPES_MAPPING.get(annotation)

    return field(*args, **opts)


def get_fields_from_annotations(annotations):
    mapped_fields = [
        (attr_name, get_marshmallow_field(attr_type))
        for attr_name, attr_type in annotations.items()
    ]

    return {
        attr_name: attr_field
        for attr_name, attr_field in mapped_fields
        if attr_field is not None
    }


def _skip_fields_from_annotations(annotations, attrs):
    return {attr_name: attr_value for attr_name, attr_value in attrs.items()
            if attr_name not in annotations or attr_value is not None}


class SchemaMeta(BaseSchemaMeta):
    def __new__(mcs, name, bases, attrs):
        annotations = attrs.get("__annotations__", {})

        attrs = _skip_fields_from_annotations(annotations, attrs)
        attrs = {**get_fields_from_annotations(annotations), **attrs}

        new_class = super().__new__(mcs, name, bases, attrs)
        setattr(new_class, "_dataclass", dataclass(type(name, (), attrs)))  # noqa: B010
        return new_class


class Schema(with_metaclass(SchemaMeta, BaseSchema)):
    __doc__ = BaseSchema.__doc__

    @post_load
    def make_object(self, data):
        return self._dataclass(**data)
