import typing as t
import datetime as dt
import uuid
import decimal

import pytest

from marshmallow import fields
from jam import Schema


@pytest.mark.parametrize(
    "attr_type,field,data,loaded",
    [
        (int, fields.Integer(required=True), 5, 5),
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
            uuid.UUID,
            fields.UUID(required=True),
            "ec367d2b-53ac-44cc-9db1-45b81cf3b78b",
            uuid.UUID("ec367d2b-53ac-44cc-9db1-45b81cf3b78b"),
        ),
        (dt.time, fields.Time(required=True), "00:00:00", dt.time(0, 0)),
        (dt.date, fields.Date(required=True), "2019-02-15", dt.date(2019, 2, 15)),
        (
            dt.timedelta,
            fields.TimeDelta(precision="seconds", required=True),
            5,
            dt.timedelta(seconds=5),
        ),
        (decimal.Decimal, fields.Decimal(required=True), 5.0, decimal.Decimal("5.0")),
    ],
)
def test_basic_typing(attr_type, field, data, loaded):
    class Response(Schema):
        foo: attr_type

    assert repr(Response().declared_fields["foo"]) == repr(field)
    assert Response().load({"foo": data}).foo == loaded


def test_required_field():
    class Response(Schema):
        required_field: int

    assert repr(Response().declared_fields["required_field"]) == repr(
        fields.Integer(required=True)
    )


def test_optional():
    class Response(Schema):
        optional_field: t.Optional[int] = None

    assert repr(Response().declared_fields["optional_field"]) == repr(fields.Integer())


def test_strict_marshmallow_field():
    class Response(Schema):
        basic_field: int
        email_field: str = fields.Email(required=True)

    assert repr(Response().declared_fields["basic_field"]) == repr(fields.Integer(required=True))
    assert repr(Response().declared_fields["email_field"]) == repr(fields.Email(required=True))
