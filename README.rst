Marshmallow Jam
===============

Some extra sweets for marshmallow.

|version| |pipeline status| |coverage report| |python_version|

.. |pipeline status| image:: https://img.shields.io/travis/nonamenix/marshmallow-jam.svg
   :target: https://travis-ci.org/nonamenix/marshmallow-jam
.. |coverage report| image:: https://coveralls.io/repos/github/nonamenix/marshmallow-jam/badge.svg?branch=master
   :target: https://coveralls.io/github/nonamenix/marshmallow-jam?branch=master
.. |version| image:: https://badge.fury.io/py/marshmallow-jam.svg
   :target: https://badge.fury.io/py/marshmallow-jam
.. |python_version| image:: https://img.shields.io/badge/python-3.7-blue.svg
   :target: https://docs.python.org/3/whatsnew/3.7.html

Examples
--------

Use annotations for schema description.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   from jam import Schema

   class Bar(Schema):
       baz: str

   class Foo(Schema):
       bar: Bar

   foo: Foo = Foo().load({"bar": {"baz": "quux"}})

   assert foo.bar.baz == "quux"


When annotations not enough
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

   class Foo(Schema):
       bar: str = fields.Email()


Mapping rules
-------------

Basic Types
~~~~~~~~~~~

=================== ====================
annotation          marshmallow field
=================== ====================
``str``             ``fields.String``
``float``           ``fields.Float``
``bool``            ``fields.Boolean``
``int``             ``fields.Integer``
``uuid.UUID``       ``fields.UUID``
``decimal.Decimal`` ``fields.Decimal``
``dt.datetime``     ``fields.DateTime``
``dt.time``         ``fields.Time``
``dt.date``         ``fields.Date``
``dt.timedelta``    ``fields.TimeDelta``
=================== ====================

All fields will be ``required`` for make it optional use
``typing.Optional[X]``

Many
~~~~

====================== ===============================
annotation             marshmallow field
====================== ===============================
``list``               ``fields.Raw(many=True)``
``typing.List[float]`` ``fields.List(fields.Float())``
====================== ===============================

Nested
~~~~~~

================================= =========================================================
annotation                        marshmallow field
================================= =========================================================
``NestedSchema``                  ``fields.Nested(NestedSchema, required=True)``
``typing.Optional[NestedSchema]`` ``fields.Nested(NestedSchema, required=True)``
``typing.List[NestedSchema]``     ``fields.Nested(NestedSchema, required=True, many=True)``
================================= =========================================================
