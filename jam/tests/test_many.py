import typing
from dataclasses import dataclass

import pytest

from jam import is_many, unpack_many, Base


@pytest.mark.parametrize(
    "annotation,expected",
    [
        (typing.List[int], True),
        (int, False),
        # edge case
        (list, True),
    ],
)
def test_is_many(annotation, expected):
    assert is_many(annotation) == expected


@pytest.mark.parametrize("annotation,expected", [(typing.List[int], int)])
def test_unpack_many(annotation, expected):
    assert unpack_many(annotation) == expected


def test_list_with_dict():
    @dataclass
    class Response(Base):
        foo: list

    response: Response = Response.load({"foo": [{"a": 1}, {"a": 1}]})
    assert response.foo
