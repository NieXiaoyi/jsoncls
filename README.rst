jsoncls
=======

jsoncls, a library that supports both of python2 and python3, can load a
json as an object, and also can dump an object to a json

A Simple Example
----------------

declare an object and load json as it

.. code:: python

   import json
   from numbers import Number
   from jsoncls import Field, String, List, Object
   from jsoncls import decode, loads


   class Address(Object):
       country = Field("Country", String)
       province = Field("Province", String)
       city = Field("City", String)


   class Education(Object):
       primary = Field("PrimarySchool", String)
       middle = Field("MiddleSchool", String)
       high = Field("HighSchool", String)
       university = Field("University", String)


   class Person(Object):
       name = Field("Name", String)
       age = Field("Age", Number)
       nationality = Field("Nationality", String)
       married = Field("Married", bool)
       education = Field("Education", Education, required=False)
       addresses = Field("Addresses", List(Address))
       hobbies = Field("Hobbies", List(String), required=False)


   if __name__ == '__main__':
       person_dict = {
           "Name": "ZhangSan",
           "Age": 20,
           "Nationality": "Korean",
           "Married": False,
           "Hobbies": ["swimming", "running"],
           "Education": {
               "PrimarySchool": "First",
               "MiddleSchool": "Second",
               "HighSchool": "Third",
               "University": "Fourth"
           },
           "Addresses": [{
               "Country": "China",
               "Province": "ZheJiang",
               "City": "HangZhou"
           }, {
               "Country": "China",
               "Province": "JiangXi",
               "City": "NanChang"
           }]
       }
       # decode the dict as an object
       person = decode(Person, person_dict)
       # the value is HangZhou
       print(person.addresses[0].city)

       person_str = json.dumps(person_dict)
       # load the json as an object
       person = loads(Person, person_str)
       # the value is China
       print(person.addresses[1].country)
