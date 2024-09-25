import json
import threading

import six

__version__ = '1.0.2'


class Decoder(object):
    def __init__(self, *args, **kwargs):
        pass

    def encode(self):
        raise NotImplementedError

    @classmethod
    def decode(cls, value):
        raise NotImplementedError


def decode(f_type, value):
    if issubclass(f_type, Decoder):
        return f_type.decode(value)

    if not isinstance(value, f_type):
        raise TypeError("value's type is not %s" % f_type)

    return value


def encode(value):
    if isinstance(value, Decoder):
        return value.encode()

    return value


def loads(decoder, s, *args, **kwargs):
    d = json.loads(s, *args, **kwargs)
    return decode(decoder, d)


def dumps(obj, *args, **kwargs):
    d = encode(obj)
    return json.dumps(d, *args, **kwargs)


def load(decoder, fp, *args, **kwargs):
    d = json.load(fp, *args, **kwargs)
    return decode(decoder, d)


def dump(obj, fp, *args, **kwargs):
    d = encode(obj)
    json.dump(d, fp, *args, **kwargs)


if six.PY2:
    String = basestring  # noqa: F821
else:
    String = str


class BaseList(list, Decoder):
    item_type = None

    def __init__(self, *args):
        for arg in args:
            if not isinstance(arg, self.item_type):
                raise TypeError("item %s is not a %s" % self.item_type.__name__)
        super(BaseList, self).__init__(args)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and super(BaseList, self).__eq__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def append(self, item):
        if not isinstance(item, self.item_type):
            raise TypeError("item must be a %s" % self.item_type.__name__)
        super(BaseList, self).append(item)

    def copy(self):
        # list has no attribute 'copy' in py2
        if six.PY2:
            raise NotImplementedError
        return self.__class__(*super(BaseList, self).copy())

    def extend(self, vec):
        if not isinstance(vec, self.__class__):
            raise TypeError("vec must be %s" % self.__class__.__name__)
        super(BaseList, self).extend(vec)

    def insert(self, index, item):
        if not isinstance(item, self.item_type):
            raise TypeError("item must be a %s" % self.item_type.__name__)
        super(BaseList, self).insert(index, item)

    def encode(self):
        return [encode(item) for item in self]

    @classmethod
    def decode(cls, vec):
        if isinstance(vec, cls):
            return vec
        if not (isinstance(vec, list) or isinstance(vec, tuple) or isinstance(vec, set)):
            raise TypeError("vec must be a list/tuple/set")
        return cls(*[decode(cls.item_type, item) for item in vec])

    def __add__(self, other):
        if not isinstance(other, self.__class__):
            raise TypeError("other must be %s" % self.item_type.__name__)
        return self.__class__(*super(BaseList, self).__add__(other))


class ListMaker(object):
    def __init__(self):
        self.lock = threading.Lock()
        self.list_class_store = {}

    def __call__(self, item_type):
        type_id = id(item_type)
        if type_id in self.list_class_store:
            return self.list_class_store[type_id]

        try:
            self.lock.acquire()
            if type_id in self.list_class_store:
                return self.list_class_store[type_id]
            list_class = type("List%s" % item_type.__name__, (BaseList,), {"item_type": item_type})
            self.list_class_store[type_id] = list_class
            return list_class
        finally:
            self.lock.release()


List = ListMaker()


class Field(object):
    def __init__(self, key, f_type, required=True):
        """ define field's attribute for an Object

        :param key: key-name of the dict which be encoded from an Object
        :param f_type: type of field in the Object
        :param required: field in the Object is required or not
        """
        self.key = key
        self.type = f_type
        self.required = required


class ObjectMeta(type):
    def __new__(cls, name, bases, attrs):
        if name == 'Object':
            return type.__new__(cls, name, bases, attrs)

        fields = {}
        pop_attrs = []
        for attr_name, field in attrs.items():
            if not isinstance(field, Field):
                continue
            fields[attr_name] = field
            pop_attrs.append(attr_name)
        for attr_name in pop_attrs:
            attrs.pop(attr_name)
        attrs['__fields__'] = fields
        return type.__new__(cls, name, bases, attrs)


@six.add_metaclass(ObjectMeta)
class Object(Decoder):
    def __init__(self, **kwargs):
        super(Object, self).__init__(**kwargs)
        fields = getattr(self, '__fields__', {})
        for attr_name, field in fields.items():
            if attr_name in kwargs:
                value = kwargs[attr_name]
                setattr(self, attr_name, value)
                continue
            if not field.required:
                continue
            raise ValueError('field %s is required' % attr_name)

    def __setattr__(self, attr_name, value):
        fields = getattr(self, '__fields__', {})
        field = fields.get(attr_name, None)
        if field is None:
            raise AttributeError('%s.%s is not allowed' % (self.__class__.__name__, attr_name))
        if not isinstance(value, field.type):
            raise TypeError("value must be a %s" % field.type.__name__)
        self.__dict__[attr_name] = value

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)

    def encode(self):
        fields = getattr(self, '__fields__', {})
        out = {}
        for attr_name, attr_value in self.__dict__.items():
            field = fields[attr_name]
            out[field.key] = encode(attr_value)
        return out

    @classmethod
    def decode(cls, kv):
        if isinstance(kv, cls):
            return kv
        fields = getattr(cls, '__fields__', {})
        kwargs = {}
        for attr_name, field in fields.items():
            if field.key not in kv:
                continue
            kwargs[attr_name] = decode(field.type, kv[field.key])
        return cls(**kwargs)
