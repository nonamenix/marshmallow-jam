import pytest

from jam import is_optional, unpack_optional_type
import typing as types


@pytest.mark.parametrize(
    "annotation,expected",
    [
        (types.Optional[int], True),
        (int, False),
        (types.Union[int, float], False),
        (types.Union[None, int], True),
        (types.Union[None], False),
    ],
)
def test_is_optional(annotation, expected):
    assert is_optional(annotation) == expected


@pytest.mark.parametrize(
    "annotation,expected",
    [(types.Optional[int], int), (types.Optional[types.List], types.List)],
)
def test_unpack_optional_type(annotation, expected):
    assert unpack_optional_type(annotation) == expected
