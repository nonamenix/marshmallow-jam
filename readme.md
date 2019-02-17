Marshmallow Jam
---------------

Some extra sweets for marshmallow. 


Use annotations for schema description.
=======================================

    class Response(Schema):
        a: float
        b: Optional[dt.datetime]
        

When annotations not enough
===========================

    class Response(Schema):
        c: str = fields.Email()


And IDE autocomplete cause now your data is instances of relevant classes
=========================================================================
    
    class User(Schema):
        name: str 

    class Response(Schema):
        user: User
        
    response = Response.schema().load({"user": {"name": "Vasya Pupkin"}})
    response.user.name
