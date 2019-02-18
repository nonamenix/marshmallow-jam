import typing

import pytest

from jam import is_list


@pytest.mark.parametrize(
    "annotation,expected",
    [
        (typing.List[int], True),
        (int, False),
    ],
)
def test_is_list(annotation, expected):
    assert is_list(annotation) == expected
