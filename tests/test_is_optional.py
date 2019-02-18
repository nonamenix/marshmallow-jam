import pytest

from jam import is_optional, unwrap_optional_type, NotValidAnnotation
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
def test_unwrap_optional_type(annotation, expected):
    assert unwrap_optional_type(annotation) == expected


def test_unwrap_optional_type_from_union_with_several_type():
    with pytest.raises(NotValidAnnotation):
        unwrap_optional_type(types.Union[type(None), int, float])
