import pytest

from jam import Schema


@pytest.mark.skip
def test_sum_of_attrs():
    class Response(Schema):
        foo: int
        bar: str

    response: Response = Response().load({"foo": "42343", "bar": "abc"})

    # IDE should highlight this string as error
    with pytest.raises(TypeError):
        response.bar + response.foo

