Marshmallow Jam
===============

Some extra sweets for marshmallow. 


Use annotations for schema description.
---------------------------------------

```python
class Response(Schema):
    a: float
    b: Optional[dt.datetime]
```
        

When annotations not enough
---------------------------

```python
class Response(Schema):
    c: str = fields.Email()
```

And IDE autocomplete cause now your data is instances of relevant classes
-------------------------------------------------------------------------

```python
class User(Schema):
    name: str 

class Response(Schema):
    user: User

response = Response.load({"user": {"name": "Vasya Pupkin"}})
response.user.name
```
