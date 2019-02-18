import typing as typing
import logging


from marshmallow import fields, post_load
from marshmallow.schema import SchemaMeta as BaseSchemaMeta, BaseSchema, with_metaclass

import datetime as dt
import uuid
import decimal


logger = logging.getLogger(__name__)


TYPE_MAPPING = {
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
    # tuple: fields.Raw,
    # list: fields.List,
    # List: fields.List,
    # set: fields.Raw,
}

NoneType = type(None)
UnionType = type(typing.Union)


class JamException(Exception):
    pass


class NotValidAnnotation(JamException):
    pass


def validate_annotation(annotation: typing.Type) -> None:
    if False:
        raise NotValidAnnotation()


# todo: flat_sequence? set, tuple, etc
def is_list(annotation: typing.Type) -> bool:
    return False


def is_optional(annotation: typing.Type) -> bool:
    return (
        hasattr(annotation, "__origin__")
        and annotation.__origin__ is typing.Union
        and len(annotation.__args__) == 2
        and NoneType in annotation.__args__
    )


def unpack_optional_type(annotation: typing.Union) -> typing.Type:
    """Optional[Type] -> Type"""
    return [t for t in annotation.__args__ if t is not NoneType][0]


def get_marshmallow_field(annotation):
    validate_annotation(annotation)

    opts = {}

    if is_optional(annotation):
        annotation = unpack_optional_type(annotation)
    else:
        opts["required"] = True

    return TYPE_MAPPING.get(annotation)(**opts)


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


class SchemaMeta(BaseSchemaMeta):
    def __new__(mcs, name, bases, attrs):
        new_class = super().__new__(
            mcs,
            name,
            bases,
            {**attrs, **get_fields_from_annotations(attrs.get("__annotations__", {}))},
        )
        return new_class


class Schema(with_metaclass(SchemaMeta, BaseSchema)):
    __doc__ = BaseSchema.__doc__

    @post_load
    def make_object(self, data):
        self.__dict__ = {**self.__dict__, **data}
        return self
