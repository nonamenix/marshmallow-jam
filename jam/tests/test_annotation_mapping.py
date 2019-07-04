import datetime as dt
import decimal
import typing as t
import uuid
from dataclasses import dataclass

import pytest
from marshmallow import fields

from jam import Base, VALIDATION_SCHEMA_FIELD


def get_dataclass_schema_field_repr(cls: type, field_name: str) -> str:
    schema = getattr(cls, VALIDATION_SCHEMA_FIELD)
    repr_str = repr(schema.declared_fields[field_name])
    return repr_str.replace("Identity", "")


@pytest.mark.parametrize(
    "attr_type,field,data,loaded",
    [
        (int, fields.Integer(required=True), 5, 5),
        (int, fields.Integer(required=True), "5", 5),
        (str, fields.String(required=True), "string", "string"),
        (float, fields.Float(required=True), 5.0, 5.0),
        (bool, fields.Boolean(required=True), "true", True),
        (
            dt.datetime,
            fields.DateTime(required=True),
            "2019-02-15T12:03:14",
            dt.datetime(2019, 2, 15, 12, 3, 14),
        ),
        (
            dt.datetime,
            fields.DateTime(required=True),
            dt.datetime(2019, 2, 15, 12, 3, 14),
            dt.datetime(2019, 2, 15, 12, 3, 14),
        ),
        (
            uuid.UUID,
            fields.UUID(required=True),
            "ec367d2b-53ac-44cc-9db1-45b81cf3b78b",
            uuid.UUID("ec367d2b-53ac-44cc-9db1-45b81cf3b78b"),
        ),
        (
            uuid.UUID,
            fields.UUID(required=True),
            uuid.UUID("ec367d2b-53ac-44cc-9db1-45b81cf3b78b"),
            uuid.UUID("ec367d2b-53ac-44cc-9db1-45b81cf3b78b"),
        ),
        (dt.time, fields.Time(required=True), "00:00:00", dt.time(0, 0)),
        (dt.time, fields.Time(required=True), dt.time(0, 0), dt.time(0, 0)),
        (dt.date, fields.Date(required=True), "2019-02-15", dt.date(2019, 2, 15)),
        (
            dt.date,
            fields.Date(required=True),
            dt.date(2019, 2, 15),
            dt.date(2019, 2, 15),
        ),
        (
            dt.timedelta,
            fields.TimeDelta(precision="seconds", required=True),
            5,
            dt.timedelta(seconds=5),
        ),
        (
            dt.timedelta,
            fields.TimeDelta(precision="seconds", required=True),
            dt.timedelta(seconds=5),
            dt.timedelta(seconds=5),
        ),
        (decimal.Decimal, fields.Decimal(required=True), 5.0, decimal.Decimal("5.0")),
        (decimal.Decimal, fields.Decimal(required=True), "5.0", decimal.Decimal("5.0")),
        (
            decimal.Decimal,
            fields.Decimal(required=True),
            decimal.Decimal("5.0"),
            decimal.Decimal("5.0"),
        ),
    ],
)
def test_basic_typing(attr_type, field, data, loaded):
    @dataclass
    class Response(Base):
        foo: attr_type

    assert get_dataclass_schema_field_repr(Response, "foo") == repr(field)
    assert Response.load({"foo": data}).foo == loaded


def test_required_field():
    @dataclass
    class Response(Base):
        foo: int

    assert get_dataclass_schema_field_repr(Response, "foo") == repr(
        fields.Integer(required=True)
    )


def test_optional():
    @dataclass
    class Response(Base):
        foo: t.Optional[int] = None

    assert get_dataclass_schema_field_repr(Response, "foo") == repr(
        fields.Integer(missing=None)
    )
