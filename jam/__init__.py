import datetime as dt
import decimal
import logging
import typing as typing
import uuid
from dataclasses import is_dataclass, dataclass
from functools import partial
from inspect import getmembers

from marshmallow import Schema
from marshmallow.fields import String, Float, Boolean, Integer, UUID, Decimal, List, Nested, Raw

from jam.fields import DateTimeIdentity, TimeIdentity, DateIdentity, TimeDeltaIdentity

logger = logging.getLogger(__name__)

sentinel = object()

VALIDATION_SCHEMA_FIELD = "__jam_validation_schema__"
SCHEMA_DATACLASS_FIELD = "__jam_schema_dataclass__"


BASIC_TYPES_MAPPING = {
    str: String,
    float: Float,
    bool: Boolean,
    int: Integer,
    uuid.UUID: UUID,
    decimal.Decimal: Decimal,
    dt.datetime: DateTimeIdentity,
    dt.time: TimeIdentity,
    dt.date: DateIdentity,
    dt.timedelta: TimeDeltaIdentity,
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
        field_fabric = List
        field_type = unpack_many(field_type)

    if is_dataclass(field_type):
        data_cls = field_type
        dataclass_schema = get_dataclass_schema(data_cls)
        field_type = partial(Nested, dataclass_schema())

    if field_type in BASIC_TYPES_MAPPING:
        field_type = BASIC_TYPES_MAPPING[field_type]

    if field_fabric is not None:
        if field_type is None:
            field_type = Raw
        field = field_fabric(field_type(), **opts)
    elif field_type is not None:
        field = field_type(**opts)
    else:
        field = None
    return field


def _get_fields_from_annotations(members, annotations):
    mapped_fields = {}
    for attr_name, attr_type in annotations.items():
        member = members.get(attr_name, sentinel)
        field = get_marshmallow_field(member, attr_type)
        if field is not None:
            mapped_fields[attr_name] = field

    return mapped_fields


def _get_class_annotations(cls):
    annotations = {}
    for base_class in cls.__mro__:
        annotations.update(base_class.__dict__.get("__annotations__", {}))
    return annotations


def _get_class_fields(cls):
    annotations = _get_class_annotations(cls)
    members = dict(getmembers(cls))
    return _get_fields_from_annotations(members, annotations)


class BaseSchema(Schema):
    def load(self, data, *, many=None, partial=None, unknown=None):
        result = super().load(data, many=many, partial=partial, unknown=unknown)
        data_cls = getattr(self, SCHEMA_DATACLASS_FIELD)
        return data_cls(**result)


def get_dataclass_schema(cls: type, meta: type = None):
    class_fields = _get_class_fields(cls)
    attrs = class_fields
    if meta is not None:
        attrs["Meta"] = meta
    schema_cls = type(f"{cls.__name__}ValidationSchema", (BaseSchema,), {**class_fields, "Meta": meta, SCHEMA_DATACLASS_FIELD: cls})
    return schema_cls


class WithSchemaMeta(type):
    def __new__(mcs, name, bases, attrs):
        meta = attrs.pop("Meta", None)
        new_class = super().__new__(mcs, name, bases, attrs)
        schema_cls = get_dataclass_schema(new_class, meta)
        setattr(new_class, VALIDATION_SCHEMA_FIELD, schema_cls())
        return new_class


@dataclass
class Base(metaclass=WithSchemaMeta):

    # def __post_init__(self):
    #     self.load(asdict(self))

    @classmethod
    def load(cls, data, *, many=None, partial=None, unknown=None):
        schema = getattr(cls, VALIDATION_SCHEMA_FIELD)
        return schema.load(data, many=many, partial=partial, unknown=unknown)
