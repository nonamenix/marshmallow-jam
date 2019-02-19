Marshmallow Jam
===============

Some extra sweets for marshmallow. 

## Examples 

### Use annotations for schema description.


```python
class Response(Schema):
    a: float
    b: Optional[dt.datetime]
```
        

### When annotations not enough

```python
class Response(Schema):
    c: str = fields.Email()
```

### And IDE autocomplete cause now your data is instances of relevant classes

```python
class User(Schema):
    name: str 

class Response(Schema):
    user: User

response: Response = Response.load({"user": {"name": "Vasya Pupkin"}})
response.user.name
```

## Mapping rules  

### Basic Types


| annotation | marshmallow field |
|--------------|-------------------| 
| `str` | `fields.String` | 
| `float` | `fields.Float` | 
| `bool` | ` fields.Boolean` |
| `int` | ` fields.Integer` |
| `uuid.UUID` | ` fields.UUID` |
| `decimal.Decimal` | ` fields.Decimal` |
| `dt.datetime` | ` fields.DateTime` |
| `dt.time` | ` fields.Time` |
| `dt.date` | ` fields.Date` |
| `dt.timedelta` | ` fields.TimeDelta` |
 
All fields will be `required` for make it optional use `typing.Optional[X]`
 

### Many
 
| annotation | marshmallow field |
|--------------|-------------------| 
| `list` | `fields.Raw(many=True)` | 
| `typing.List[float]` | `fields.List(fields.Float())` | 
 

### Nested 
  
| annotation | marshmallow field |
|--------------|-------------------| 
| `NestedSchema` | `fields.Nested(NestedSchema, required=True)` |
| `typing.Optional[NestedSchema]` | `fields.Nested(NestedSchema, required=True)` |
| `typing.List[NestedSchema]` | `fields.Nested(NestedSchema, required=True, many=True)` |
 