import datetime as dt
import decimal
import logging
import typing as typing
import uuid
from inspect import getmembers

from dataclasses import is_dataclass, dataclass
from marshmallow import fields, RAISE, post_load
from marshmallow.schema import Schema as MarshmallowSchema, BaseSchema, SchemaMeta as BaseSchemaMeta

logger = logging.getLogger(__name__)

sentinel = object()

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
    return (
        hasattr(annotation, "__origin__")
        and (annotation.__origin__ is list or annotation.__origin__ is typing.List)
        or annotation in (list, tuple)
    )


def unpack_many(annotation: typing.Type) -> typing.Optional[bool]:
    return hasattr(annotation, "__args__") and annotation.__args__[0] or None


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


def get_marshmallow_field(member, annotation):
    field_fabric = None
    field_type = annotation

    opts = {}
    if is_optional(field_type):
        field_type = unpack_optional_type(field_type)
        if member is not sentinel:
            opts["missing"] = member
    else:
        opts["required"] = True

    if is_many(field_type):
        field_fabric = fields.List
        field_type = unpack_many(field_type)

    if is_dataclass(field_type):
        field_type = get_class_schema(field_type)
        field_fabric = fields.Nested

    field_type = field_type and BASIC_TYPES_MAPPING.get(field_type) or None
    if field_fabric is not None:
        if field_type is None:
            field_type = fields.Raw
        field = field_fabric(field_type(), **opts)
    elif field_type is not None:
        field = field_type(**opts)
    else:
        field = None
    return field


def get_fields_from_annotations(members, annotations):
    mapped_fields = {}
    for attr_name, attr_type in annotations.items():
        member = members.get(attr_name, sentinel)
        field = get_marshmallow_field(member, attr_type)
        if field is not None:
            mapped_fields[attr_name] = field

    return mapped_fields


def _get_class_fields(cls):
    annotations = _get_class_annotations(cls)
    members = dict(getmembers(cls))
    return get_fields_from_annotations(members, annotations)


def _get_class_annotations(cls):
    annotations = {}
    for base_class in cls.__mro__:
        # TODO: raise if duplicate annotations found?
        annotations.update(base_class.__dict__.get("__annotations__", {}))
    return annotations


def get_class_schema(cls):
    # TODO: allow to parametrize Meta
    class _SchemaMeta:
        unknown = RAISE

    fields = _get_class_fields(cls)
    schema_cls = type(f"{cls.__name__}ValidationSchema", (MarshmallowSchema,), {**fields, "Meta": _SchemaMeta})
    return schema_cls


def _skip_fields_from_annotations(annotations, attrs):
    return {
        attr_name: attr_value
        for attr_name, attr_value in attrs.items()
        if attr_name not in annotations or attr_value is not None
    }


class SchemaMeta(BaseSchemaMeta):
    def __new__(mcs, name, bases, attrs):
        annotations = attrs.get("__annotations__", {})
        class_fields = get_fields_from_annotations(attrs, annotations)
        attrs = {**class_fields, **_skip_fields_from_annotations(annotations, attrs)}
        new_class = super().__new__(mcs, name, bases, attrs)

        setattr(new_class, "_dataclass", dataclass(type(name, (), attrs)))  # noqa: B010
        return new_class


class Schema(BaseSchema, metaclass=SchemaMeta):
    __doc__ = BaseSchema.__doc__

    @post_load
    def make_object(self, data, **kwargs):
        return self._dataclass(**data)
