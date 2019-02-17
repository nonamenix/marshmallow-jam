from typing import Dict, List, Optional
import logging

import inspect
from collections import ChainMap
from pprint import pprint

from marshmallow import fields, Schema as MarshMallowSchema, post_load
from marshmallow.schema import SchemaMeta as BaseSchemaMeta, BaseSchema, with_metaclass

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


def merge_dicts(*dicts):
    merged = dict(dicts[0])

    for d in dicts[1:]:
        for key, value in d.items():
            merged[key] = value

    return merged


def get_field(attr_type):
    return TYPE_MAPPING.get(attr_type)


def get_fields_from_annotations(annotations):
    mapped_fields = [
        (attr_name, get_field(attr_type))
        for attr_name, attr_type in annotations.items()
    ]

    return {
        attr_name: attr_field
        for attr_name, attr_field in mapped_fields
        if attr_field is not None
    }


class SchemaMeta(BaseSchemaMeta):
    def __new__(mcs, name, bases, attrs):
        klass = super().__new__(
            mcs,
            name,
            bases,
            merge_dicts(
                attrs, get_fields_from_annotations(attrs.get("__annotations__", {}))
            ),
        )
        return klass


class Schema(with_metaclass(SchemaMeta, BaseSchema)):
    __doc__ = BaseSchema.__doc__

    @post_load
    def make_object(self, data):
        self.__dict__ = merge_dicts(self.__dict__, data)
        return self
