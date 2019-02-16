Marshmallow schemas with annotations
------------------------------------

    class Response(Schema):
        a: float
        b = None
        c = fields.Integer()

    response = Response.schema().load({"a": 5.0, "c": 5})
    response.a
