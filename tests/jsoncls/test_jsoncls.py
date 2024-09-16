import json
from numbers import Number
import os
import unittest

import six

from jsoncls import Field, String, List, Object
from jsoncls import decode, encode, loads, dumps, dump, load


class TestList(unittest.TestCase):
    def test_new_class(self):
        l1 = List(Number)
        l2 = List(String)
        l3 = List(String)
        self.assertIsNot(l1, l2)
        self.assertIs(l2, l3)
        l4 = List(List(float))
        l5 = List(List(float))
        self.assertIs(l4, l5)

    def test_init(self):
        l_str = List(String)("1", "2", "3")
        self.assertEqual(l_str[0], "1")
        self.assertTrue(isinstance(l_str[0], String))
        self.assertRaises(TypeError, List(String), [1])

        l_empty = List(String)()
        self.assertEqual(len(l_empty), 0)

    def test_equal(self):
        self.assertNotEqual(List(String)("1"), ["1"])
        self.assertEqual(List(String)("1"), List(String)("1"))

    def test_append(self):
        l_int = List(Number)(1, 2, 3)
        l_int.append(4)
        self.assertEqual(len(l_int), 4)
        self.assertEqual(l_int[3], 4)
        self.assertRaises(TypeError, l_int.append, "5")
        self.assertRaises(TypeError, l_int.append, ["5"])
        ll_int = List(List(Number))(List(Number)(1, 2), List(Number)(3, 4))
        self.assertRaises(TypeError, ll_int.append, 1)

        class Student(Object):
            name = Field("name", String)
            age = Field("age", Number)

        l_obj = List(Student)(Student(name="xiaoming", age=12))
        xiaohua = Student(name="xiaohua", age=15)
        l_obj.append(xiaohua)
        self.assertIs(l_obj[1], xiaohua)

    def test_copy(self):
        l = List(Number)(1, 2, 3)
        if six.PY2:
            self.assertRaises(NotImplementedError, l.copy)
        else:
            l2 = l.copy()
            self.assertEqual(len(l2), 3)
            self.assertEqual(l, l2)

    def test_extend(self):
        l_float = List(Number)(1, 2, 3)
        l_float.extend(List(Number)(4, 5, 6))
        self.assertEqual(len(l_float), 6)
        self.assertEqual(l_float[3], 4)
        self.assertRaises(TypeError, l_float.extend, List(String)("7", "8", "9"))
        self.assertRaises(TypeError, l_float.extend, 7)

    def test_insert(self):
        l_int = List(Number)(1, 2, 3)
        l_int.insert(0, 0)
        self.assertEqual(len(l_int), 4)
        self.assertEqual(l_int[0], 0)
        self.assertRaises(TypeError, l_int.insert, 0, "5")
        self.assertRaises(TypeError, l_int.insert, 1, List(Number)(5))

    def test_decode_encode(self):
        ll_str = decode(List(List(String)), [["1", "2"], ["3", "4"]])
        self.assertEqual(ll_str[0][0], "1")
        self.assertEqual(encode(ll_str), [["1", "2"], ["3", "4"]])
        self.assertRaises(TypeError, decode, List(List(String)), ["1", "2"])
        self.assertRaises(TypeError, decode, List(List(String)), [[1, 2], [3, 4]])

    def test_clear(self):
        if six.PY2:
            return
        l = List(Number)(1, 2, 3)
        self.assertEqual(len(l), 3)
        l.clear()
        self.assertEqual(len(l), 0)

    def test_count(self):
        l = List(Number)(1, 2, 3)
        self.assertEqual(l.count(1), 1)
        self.assertEqual(l.count(4), 0)

    def test_index(self):
        l = List(Number)(1, 2, 3)
        self.assertEqual(l.index(3), 2)
        self.assertRaises(ValueError, l.index, 5)

    def test_pop(self):
        l = List(Number)(1, 2, 3)
        self.assertRaises(IndexError, l.pop, 4)
        self.assertEqual(l.pop(1), 2)
        self.assertEqual(l, List(Number)(1, 3))

    def test_remove(self):
        l = List(Number)(1, 2, 2, 3)
        self.assertRaises(ValueError, l.remove, 4)
        l.remove(2)
        self.assertEqual(l, List(Number)(1, 2, 3))

    def test_reverse(self):
        l = List(Number)(1, 2, 3)
        l.reverse()
        self.assertEqual(l, List(Number)(3, 2, 1))

    def test_sort(self):
        l = List(Number)(3, 5, 2, 4, 1)
        l.sort()
        self.assertEqual(l, List(Number)(1, 2, 3, 4, 5))

    def test_add(self):
        l = List(Number)(1, 2, 3)
        l2 = List(Number)(4, 5)
        self.assertEqual(l + l2, List(Number)(1, 2, 3, 4, 5))
        l += l2
        self.assertEqual(l, List(Number)(1, 2, 3, 4, 5))

    def test_contains(self):
        l = List(Number)(1, 2, 3)
        self.assertTrue(1 in l)

    def test_del(self):
        l = List(Number)(1, 2, 3)
        del l[0]
        self.assertEqual(l, List(Number)(2, 3))
        l = List(Number)(1, 2, 3)
        del l[0:2]
        self.assertEqual(l, List(Number)(3))

    def test_set(self):
        l = List(Number)(1, 2, 3)
        l[0] = 4
        self.assertEqual(l, List(Number)(4, 2, 3))


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


class TestObject(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.dict_completed = {
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

        cls.dict_uncompleted = {
            "Name": "LiSi",
            "Age": 30,
            "Nationality": "Han",
            "Married": True,
            "Addresses": [{
                "Country": "China",
                "Province": "ZheJiang",
                "City": "HangZhou"
            }]
        }

    def test_completed_fields_encode(self):
        person = Person(name="ZhangSan", age=20, nationality="Korean", married=False,
                        education=Education(primary="First", middle="Second", high="Third", university="Fourth"),
                        addresses=List(Address)(Address(country="China", province="ZheJiang", city="HangZhou"),
                                                Address(country="China", province="JiangXi", city="NanChang")),
                        hobbies=List(String)("swimming", "running"))
        ret = encode(person)
        self.assertEqual(ret, self.dict_completed)

    def test_completed_fields_decode(self):
        person = decode(Person, self.dict_completed)
        self.assertEqual(person.name, "ZhangSan")
        self.assertEqual(person.age, 20)
        self.assertEqual(person.married, False)
        self.assertEqual(person.nationality, "Korean")
        self.assertEqual(person.education.primary, "First")
        self.assertEqual(person.addresses[0].city, "HangZhou")
        self.assertEqual(person.addresses[1].province, "JiangXi")

    def test_uncompleted_fields_encode(self):
        person = Person(name="LiSi", age=30, nationality="Han", married=True,
                        addresses=List(Address)(Address(country="China", province="ZheJiang", city="HangZhou")))
        ret = encode(person)
        self.assertEqual(ret, self.dict_uncompleted)

    def test_uncompleted_fields_decode(self):
        person = decode(Person, self.dict_uncompleted)
        self.assertEqual(person.name, "LiSi")
        self.assertEqual(person.age, 30)
        self.assertEqual(person.married, True)
        self.assertEqual(person.nationality, "Han")
        self.assertFalse(hasattr(person, "education"))
        self.assertEqual(person.addresses[0].city, "HangZhou")
        self.assertFalse(hasattr(person, "hobbies"))

    def test_equal(self):
        person1 = decode(Person, self.dict_completed)
        person2 = decode(Person, self.dict_completed)
        self.assertIsNot(person1, person2)
        self.assertEqual(person1, person2)

    def test_required_default(self):
        person = decode(Person, self.dict_uncompleted)
        self.assertEqual(person.nationality, "Han")
        with self.assertRaises(AttributeError):
            _ = person.hobbies

    def test_setattr(self):
        person = decode(Person, self.dict_uncompleted)
        with self.assertRaises(TypeError):
            person.hobbies = "basketball"
        with self.assertRaises(TypeError):
            person.hobbies = ["basketball"]
        person.hobbies = List(String)("basketball")
        self.assertEqual(person.hobbies[0], "basketball")

    def test_loads(self):
        s = json.dumps(self.dict_completed)
        p = loads(Person, s)
        self.assertEqual(p.addresses[1].city, "NanChang")

    def test_dumps(self):
        obj = decode(Person, self.dict_completed)
        s = dumps(obj)
        se = json.dumps(self.dict_completed)
        self.assertEqual(json.loads(s), json.loads(se))

    def test_dump(self):
        test_file = os.path.join(os.path.dirname(__file__), "test_dump.json")
        try:
            person = decode(Person, self.dict_completed)
            with open(test_file, "w") as f:
                dump(person, f)
            with open(test_file, "r") as f:
                d = json.load(f)
            self.assertEqual(d, self.dict_completed)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)

    def test_load(self):
        test_file = os.path.join(os.path.dirname(__file__), "test_load.json")
        try:
            with open(test_file, "w") as f:
                json.dump(self.dict_completed, f)
            with open(test_file, "r") as f:
                person = load(Person, f)
            self.assertEqual(encode(person), self.dict_completed)
        finally:
            if os.path.exists(test_file):
                os.remove(test_file)
