#!/usr/bin/env python
# encoding: utf-8
import base64
import logging
import os
from datetime import datetime
from lxml import etree


CURRENT_DIR = os.path.abspath(os.path.dirname(__file__))
log = logging.getLogger(__name__)


try:
    unicode
except NameError:
    unicode = str

try:
    bytes
except NameError:
    bytes = str

try:
    from types import NoneType
except ImportError:
    NoneType = type(None)


class Binary(bytes):
    pass


TIME_FORMAT = "%Y%m%dT%H:%M:%S"
PY2XML_TYPES = {}
XML2PY_TYPES = {}


def get_schema():
    return etree.XMLParser(
        schema=etree.XMLSchema(
            file=os.path.join(CURRENT_DIR, 'xmlrpc.xsd')
        )
    )


def py2xml(result):
    func = PY2XML_TYPES.get(type(result))
    if not func:
        raise RuntimeError("Can't serialise type: %s", type(result))

    return func(result)


def xml_string(x):
    el = etree.Element('string')
    el.text = unicode(x)
    return el


def xml_float(x):
    el = etree.Element('double')
    el.text = unicode(x)
    return el


def xml_datetime(x):
    el = etree.Element('dateTime.iso8601')
    el.text = x.strftime(TIME_FORMAT)
    return el


def xml_int(x):
    el = etree.Element('i4')
    el.text = unicode(x)
    return el


def xml_binary(x):
    el = etree.Element('base64')
    el.text = base64.b64encode(x)
    return el


def xml_bool(x):
    el = etree.Element('boolean')
    el.text = "1" if x else "0"
    return el


def xml_none(x):
    return etree.Element('nil')


def xml_list(x):
    array = etree.Element('array')
    data = etree.Element('data')
    array.append(data)

    for i in x:
        el = etree.Element('value')
        el.append(py2xml(i))
        data.append(el)

    return array


def xml_dict(x):
    struct = etree.Element('struct')

    for key, value in x.items():
        member = etree.Element('member')
        struct.append(member)

        key_el = etree.Element('name')
        key_el.text = unicode(key)
        member.append(key_el)

        value_el = etree.Element('value')
        value_el.append(py2xml(value))
        member.append(value_el)

    return struct


PY2XML_TYPES.update({
    str: xml_string,
    unicode: xml_string,
    tuple: xml_list,
    list: xml_list,
    int: xml_int,
    float: xml_float,
    datetime: xml_datetime,
    Binary: xml_binary,
    bool: xml_bool,
    NoneType: xml_none,
    dict: xml_dict
})


def xml2py(value):
    return XML2PY_TYPES.get(value.tag)(value)


def from_struct(p):
    return dict(
        map(
            lambda x: (x[0].text, x[1]),
            zip(
                p.xpath(".//member/name"),
                map(xml2py, p.xpath(".//member/value/*"))
            )
        )
    )


def from_array(p):
    return list(map(xml2py, p.xpath(".//data/value/*")))


XML2PY_TYPES.update({
    'string': lambda x: unicode(x.text),
    'struct': from_struct,
    'array': from_array,
    'base64': lambda x: Binary(base64.b64decode(x.text)),
    'boolean': lambda x: bool(int(x.text)),
    'dateTime.iso8601': lambda x: datetime.strptime(x.text, TIME_FORMAT),
    'double': lambda x: float(x.text),
    'integer': lambda x: int(x.text),
    'int': lambda x: int(x.text),
    'i4': lambda x: int(x.text),
    'nil': lambda x: None,
})


__all__ = ('py2xml', 'xml2py', 'get_schema')
