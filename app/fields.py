from app import utils

import types
import logging

import simplejson as json

from google.appengine.ext import db
from google.appengine.api.datastore_errors import BadValueError


log = logging.getLogger(__name__)


class JSONProperty(db.TextProperty):
    accept_types = (
        int, long, float, basestring, list, tuple, dict, types.NoneType, bool
    )

    def get_value_for_datastore(self, model_instance):
        value = super(JSONProperty,
                     self).get_value_for_datastore(model_instance)
        return self.data_type(json.dumps(value))

    def make_value_from_datastore(self, value):
        if value is None:
            return self.get_one_data_type()()

        return json.loads(value)

    def validate(self, value):
        if value is not None and not isinstance(value, self.accept_types):
            raise BadValueError('Property %s must be %s not %s' %
                                (self.name, '/'.join(map(str, self.accept_types)), value))
        return value

    def empty(self, value):
        return not value


class ObjectProperty(JSONProperty):
    r"""
    >>> from webob.multidict import MultiDict
    >>> class Entry(db.Model):
    ...     obj = ObjectProperty(dict)

    >>> e = Entry(obj={'foo': 'bar'}, key_name='foobar')
    >>> key = e.put()
    >>> e.obj
    {'foo': 'bar'}
    >>> isinstance(e.obj, dict)
    True
    >>> e = Entry.get_by_key_name('foobar')
    >>> e.obj
    {u'foo': u'bar'}
    >>> isinstance(e.obj, dict)
    True
    """
    def __init__(self, klass, load=None, dump=None, *args, **kwargs):
        self.klass = klass
        self.load = load or (lambda v: self.klass(v))
        self.dump = dump or (lambda v: v)

        super(ObjectProperty, self).__init__(*args, **kwargs)

    def validate(self, value):
        if value is not None:
            if not isinstance(value, self.klass):
                value = self.load(super(ObjectProperty, self).validate(value))

        return value

    def get_value_for_datastore(self, model_instance):
        value = super(JSONProperty, self).get_value_for_datastore(model_instance)
        return self.data_type(json.dumps(self.dump(value)))
