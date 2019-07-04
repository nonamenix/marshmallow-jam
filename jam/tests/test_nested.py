import typing
from dataclasses import dataclass

from jam import Base


def test_nested_dataclass():
    @dataclass
    class Bar(Base):
        baz: str

    @dataclass
    class Foo(Base):
        bar: Bar

    assert Foo.load({"bar": {"baz": "aaa"}}) == Foo(bar=Bar(baz="aaa"))


def test_nested_many():
    @dataclass
    class Bar(Base):
        baz: str

    @dataclass
    class Foo(Base):
        bar: typing.List[Bar]

    assert Foo.load({"bar": [{"baz": "aaa"}]}) == Foo(bar=[Bar(baz="aaa")])
