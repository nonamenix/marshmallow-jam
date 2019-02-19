import typing

import pytest

from jam import Schema


@pytest.mark.skip
def test_sum_of_attrs():
    class Bar(Schema):
        quex: str

    class Response(Schema):
        foo: int
        bar: Bar
        bars: typing.List[Bar]

    response: Response = Response().load({"foo": "42343", "bar": "abc"})

    # IDE should highlight this string as error
    with pytest.raises(TypeError):
        response.bar.quex + response.foo
        response.bars[0].quex + response.foo
