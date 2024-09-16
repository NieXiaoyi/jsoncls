import json
import logging
import time
import typing
import unittest
from pydantic import BaseModel

from jsoncls import Field, List, Object
from jsoncls import loads, dumps

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AddressModel(BaseModel):
    street: str
    city: str
    zip_code: str


class UserModel(BaseModel):
    name: str
    age: int
    hobbies: typing.List[str]
    address: AddressModel


class AddressObject(Object):
    street = Field("street", str)
    city = Field("city", str)
    zip_code = Field("zip_code", str)


class UserObject(Object):
    name = Field("name", str)
    age = Field("age", int)
    hobbies = Field("hobbies", List(str))
    address = Field("address", AddressObject)


class TestBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_json = json.dumps({
            'name': 'Alice',
            'age': 30,
            'hobbies': ['swimming', 'running'],
            'address': {
                'street': '123 Main St',
                'city': 'New York',
                'zip_code': '10001'
            }
        })

    def test_loads(self):
        logger.info("start to benchmark loads")

        start_time = time.time()
        for i in range(10000):
            _ = UserModel.model_validate_json(self.test_json)
        end_time = time.time()
        load_dict_use = end_time - start_time
        logger.info("load json with pydantic, time use: %.2fs", load_dict_use)

        start_time = time.time()
        for i in range(10000):
            _ = loads(UserObject, self.test_json)
        end_time = time.time()
        load_obj_use = end_time - start_time
        logger.info("load json with jsoncls, time use: %.2fs", load_obj_use)

    def test_dumps(self):
        logger.info("start to benchmark dumps")

        um = UserModel.model_validate_json(self.test_json)
        start_time = time.time()
        for i in range(10000):
            _ = um.model_dump_json()
        end_time = time.time()
        load_dict_use = end_time - start_time
        logger.info("dump json with pydantic, time use: %.2fs", load_dict_use)

        uo = loads(UserObject, self.test_json)
        start_time = time.time()
        for i in range(10000):
            _ = dumps(uo)
        end_time = time.time()
        load_obj_use = end_time - start_time
        logger.info("dump json with jsoncls, time use: %.2fs", load_obj_use)
