import pytest

from jam import is_optional, unpack_optional_type
import typing as typing


@pytest.mark.parametrize(
    "annotation,expected",
    [
        (typing.Optional[int], True),
        (int, False),
        (typing.Union[int, float], False),
        (typing.Union[None, int], True),
        (typing.Union[None], False),
    ],
)
def test_is_optional(annotation, expected):
    assert is_optional(annotation) == expected


@pytest.mark.parametrize(
    "annotation,expected",
    [(typing.Optional[int], int), (typing.Optional[typing.List], typing.List)],
)
def test_unpack_optional_type(annotation, expected):
    assert unpack_optional_type(annotation) == expected
