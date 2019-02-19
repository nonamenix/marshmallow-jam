import typing

import pytest

from jam import is_many


@pytest.mark.parametrize(
    "annotation,expected", [(typing.List[int], True), (int, False), (list, True)]
)
def test_is_many(annotation, expected):
    assert is_many(annotation) == expected
