#!/usr/bin/env python
# encoding: utf-8
import pickle
from datetime import datetime
from lxml import etree
from . import common


TYPES_CASES = (
    (common.Binary("you can't read this!"), '<base64>eW91IGNhbid0IHJlYWQgdGhpcyE=</base64>'),
    (-12.53, "<double>-12.53</double>"),
    (u"Hello world!", u"<string>Hello world!</string>"),
    (
        datetime(year=1998, month=7, day=17, hour=14, minute=8, second=55),
        "<dateTime.iso8601>19980717T14:08:55</dateTime.iso8601>"
    ),
    (42, "<i4>42</i4>"),
    (True, "<boolean>1</boolean>"),
    (False, "<boolean>0</boolean>"),
    (None, "<nil/>"),
    (
        [1404, u'Something here', 1],
        (
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
        (
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


def check_xml(element, xml_data):
    return etree.tostring(element) == xml_data


def check_python(data, result):
    return pickle.dumps(data) == pickle.dumps(result)


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
        raise RuntimeError("No way!!!")