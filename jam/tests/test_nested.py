import typing

import pytest

from jam import Schema


@pytest.mark.skip("Delete this functionality?")
def test_nested_schema():
    class Bar(Schema):
        baz: str

    class Foo(Schema):
        bar: Bar

    foo = Foo().load({"bar": {"baz": "quux"}})
    assert foo.bar.baz == "quux"


@pytest.mark.skip("Delete this functionality?")
def test_nested_many_schema():
    class Bar(Schema):
        baz: str

    class Foo(Schema):
        bar: typing.List[Bar]

    foo: Foo = Foo().load({"bar": [{"baz": "quux"}]})

    assert foo.bar[0].baz == "quux"
