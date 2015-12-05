#!/usr/bin/env python
# encoding: utf-8
import xmltodict
from datetime import datetime
from lxml import etree
from tornado_xmlrpc import PY2
from . import common


if PY2:
    def b(s):
        return s

    def u(s):
        return unicode(s.replace(r'\\', r'\\\\'), "unicode_escape")
else:
    def b(s):
        return s.encode("latin-1")

    def u(s):
        return s

try:
    unicode
except NameError:
    unicode = str


TYPES_CASES = (
    (common.Binary(b("you can't read this!")), unicode('<base64>eW91IGNhbid0IHJlYWQgdGhpcyE=</base64>')),
    (-12.53, unicode("<double>-12.53</double>")),
    (unicode("Hello world!"), unicode("<string>Hello world!</string>")),
    (
        datetime(year=1998, month=7, day=17, hour=14, minute=8, second=55),
        unicode("<dateTime.iso8601>19980717T14:08:55</dateTime.iso8601>")
    ),
    (42, unicode("<i4>42</i4>")),
    (True, unicode("<boolean>1</boolean>")),
    (False, unicode("<boolean>0</boolean>")),
    (None, unicode("<nil/>")),
    (
        [1404, unicode("Something here"), 1],
        unicode(
            "<array>"
                "<data>"
                    "<value>"
                        "<i4>1404</i4>"
                    "</value>"
                    "<value>"
                        "<string>Something here</string>"
                    "</value>"
                    "<value>"
                        "<i4>1</i4>"
                    "</value>"
                "</data>"
            "</array>"
        )
    ),
    (
        {'foo': 1, 'bar': 2},
        unicode(
            "<struct>"
              "<member>"
                "<name>foo</name>"
                "<value><i4>1</i4></value>"
              "</member>"
              "<member>"
                "<name>bar</name>"
                "<value><i4>2</i4></value>"
              "</member>"
            "</struct>"
        )
    ),
)


def normalise_dict(d):
    """
    Recursively convert dict-like object (eg OrderedDict) into plain dict.
    Sorts list values.
    """
    out = {}
    for k, v in dict(d).items():
        if hasattr(v, 'iteritems'):
            out[k] = normalise_dict(v)
        elif isinstance(v, list):
            out[k] = []
            for item in sorted(v):
                if hasattr(item, 'iteritems'):
                    out[k].append(normalise_dict(item))
                else:
                    out[k].append(item)
        else:
            out[k] = v
    return out


def check_xml(a, b):
    """
    Compares two XML documents (as string or etree)

    Does not care about element order
    """

    if not isinstance(a, (str, unicode)):
        a = etree.tostring(a)
    if not isinstance(b, (str, unicode)):
        b = etree.tostring(b)

    a = normalise_dict(xmltodict.parse(a))
    b = normalise_dict(xmltodict.parse(b))
    return a == b


def check_python(data, result):
    return (str(data), repr(data)) == (str(result), repr(result))


def checker(func, chk, data, result):
    assert chk(func(data), result)


def test_py2xml_gen():
    for data, result in TYPES_CASES:
        yield checker, common.PY2XML_TYPES[type(data)], check_xml, data, result


def test_xml2py_gen():
    for result, data in TYPES_CASES:
        data = etree.fromstring(data)
        yield checker, common.XML2PY_TYPES[data.tag], check_python, data, result


def test_py2xml_error():
    try:
        common.py2xml(Exception)
    except RuntimeError:
        pass
    else:
        raise RuntimeError(unicode("No way!!!"))