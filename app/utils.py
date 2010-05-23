# coding: utf-8
import os
import sys
from xml.dom import minidom

from django.utils.datastructures import MultiValueDict

def patch_paths():
    sys.path = [
        os.path.join(os.path.dirname(os.path.dirname(__file__)), 'compat')
    ] + sys.path

patch_paths()


class XmlDict(MultiValueDict):
    r'''
    Example usage:

    >>> from xml.dom import minidom
    >>> xml = minidom.parseString(
    ...     '<a b=" blah"><c id="1">World </c><c id="2"><d>Hello</d><e /></c></a>'
    ... )
    >>> XmlDict.fromelement(xml.firstChild)
    <XmlDict: {u'@b': [u'blah'], u'c': [<XmlDict: {u'#text': [u'World'], u'@id': [u'1']}>, <XmlDict: {u'@id': [u'2'], u'd': [u'Hello']}>]}>

    Проверяем пустой __text__
    >>> xml = minidom.parseString('<a b=" blah"><c id="1"> </c></a>')
    >>> XmlDict.fromelement(xml.firstChild)
    <XmlDict: {u'@b': [u'blah'], u'c': [<XmlDict: {u'@id': [u'1']}>]}>

    Проверяем фильтры
    >>> xml = minidom.parseString('<a b="!blah!"><c id="1">!World!</c></a>')
    >>> XmlDict.fromelement(xml.firstChild, [lambda t: t.strip('!')])
    <XmlDict: {u'@b': [u'blah'], u'c': [<XmlDict: {u'#text': [u'World'], u'@id': [u'1']}>]}>

    Convert to raw dict
    >>> xml = minidom.parseString('<a b=" blah"><c id="1"></c><c id="2">foo</c></a>')
    >>> d = XmlDict.fromelement(xml.firstChild)
    >>> d.to_raw_dict()
    {u'@b': u'blah', u'c': [{u'@id': u'1'}, {u'#text': u'foo', u'@id': u'2'}]}
    '''

    text_attr_name = u'#text'

    @classmethod
    def fromelement(cls, parent, filters=None):
        if filters is None:
            filters = [lambda text: text.strip(' \n\t')]

        def apply_filters(text):
            for f in filters:
                text = f(text)
            return text

        self = cls()

        if parent.attributes and parent.attributes.length: # атрибуты c префиксом @
            for i in range(parent.attributes.length):
                attr = parent.attributes.item(i)
                self.update({u'@%s' % attr.name: apply_filters(attr.value)})

        for node in parent.childNodes:
            if isinstance(node, minidom.Text):
                # тест со специальным именем
                if self.text_attr_name not in self:
                    self[self.text_attr_name] = ''
                self[self.text_attr_name] += node.data
            else:
                sub_element = XmlDict.fromelement(node, filters)

                if len(sub_element) == 1 and self.text_attr_name in sub_element:
                    sub_element = sub_element[self.text_attr_name]

                if sub_element:
                    self.update({node.nodeName: sub_element})

        if self.text_attr_name in self:
            text = apply_filters(self[self.text_attr_name])
            if text:
                self[self.text_attr_name] = text
            else:
                del self[self.text_attr_name]

        return self

    def __repr__(self):
        return "<%s: %s>" % (self.__class__.__name__,
                             super(MultiValueDict, self).__repr__())

    def to_raw_dict(self):
        d = {}
        for key, value in self.lists():
            for i, v in enumerate(value[:]):
                if isinstance(v, self.__class__):
                    v = v.to_raw_dict()
                value[i] = v

            if len(value) == 1:
                value = value[0]

            d[key] = value
        return d



