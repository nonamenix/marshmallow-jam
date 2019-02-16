from typing import Dict, List, Optional
import logging

import inspect
from collections import ChainMap
from pprint import pprint

from marshmallow import fields, Schema as MarshMallowSchema

import datetime as dt
import uuid
import decimal


logger = logging.getLogger(__name__)


TYPE_MAPPING = {
    str: fields.String(required=True),
    float: fields.Float(required=True),
    bool: fields.Boolean(required=True),
    int: fields.Integer(required=True),
    uuid.UUID: fields.UUID(required=True),
    decimal.Decimal: fields.Decimal(required=True),
    dt.datetime: fields.DateTime(required=True),
    dt.time: fields.Time(required=True),
    dt.date: fields.Date(required=True),
    dt.timedelta: fields.TimeDelta(required=True),
    Optional[int]: fields.Integer()
    # tuple: fields.Raw,
    # list: fields.List,
    # List: fields.List,
    # set: fields.Raw,
}


def get_field(attr_type):
    return TYPE_MAPPING.get(attr_type)


def merge_dicts(*dicts):
    merged = dict(dicts[0])

    for d in dicts[1:]:
        for key, value in d.items():
            merged[key] = value

    return merged


def get_class_fields(cls):
    return merge_dicts(get_fields_from_annotations(cls), get_fields_from_values(cls))


def get_fields_from_annotations(cls):
    annotations = dict(inspect.getmembers(cls)).get("__annotations__", {}).items()

    mapped_fields = [
        (attr_name, get_field(attr_type)) for attr_name, attr_type in annotations
    ]

    return {
        attr_name: attr_field
        for attr_name, attr_field in mapped_fields
        if attr_field is not None
    }


def get_fields_from_values(cls):
    return {
        attr_name: attr_type
        for attr_name, attr_type in dict(inspect.getmembers(cls))["__dict__"].items()
        if isinstance(attr_type, fields.Field)
    }


class MetaSchema(type):
    def __new__(cls, clsname, bases, dct):
        newclass = super().__new__(cls, clsname, bases, dct)
        setattr(
            newclass,
            "schema",
            type(f"{clsname}Schema", (MarshMallowSchema,), get_class_fields(newclass)),
        )
        return newclass


class Schema(metaclass=MetaSchema):
    schema: Optional[MarshMallowSchema]
