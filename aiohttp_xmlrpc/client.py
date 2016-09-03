# encoding: utf-8
import asyncio
import aiohttp.client
from lxml import etree
from . import __version__, __pyversion__
from .common import py2xml, xml2py, schema


class RemoteServerException(Exception):
    def __init__(self, message, code=-32500):
        Exception.__init__(self, message)
        self.code = code


class InvalidResponse(Exception):
    pass


class ServerProxy(object):
    __slots__ = 'client', 'url', 'loop'

    USER_AGENT = u'aiohttp XML-RPC client (Python: {0}, version: {1})'.format(__pyversion__, __version__)

    def __init__(self, url, client=None, loop=None):
        self.url = str(url)
        self.loop = loop or asyncio.get_event_loop()
        self.client = client or aiohttp.client.ClientSession(loop=self.loop)

    @staticmethod
    def _make_request(method_name, *args, **kwargs):
        root = etree.Element('methodCall')
        method_el = etree.Element('methodName')
        method_el.text = method_name

        root.append(method_el)

        params_el = etree.Element('params')
        root.append(params_el)

        for arg in args:
            param = etree.Element('param')
            val = etree.Element('value')
            param.append(val)
            params_el.append(param)
            val.append(py2xml(arg))

        if kwargs:
            param = etree.Element('param')
            val = etree.Element('value')
            param.append(val)
            params_el.append(param)
            val.append(py2xml(kwargs))

        return root

    @staticmethod
    def _parse_response(body, method_name):
        try:
            response = etree.fromstring(body, schema())
        except etree.XMLSyntaxError as e:
            raise ValueError("Invalid body")

        result = response.xpath('//params/param/value/*')
        if result:
            return xml2py(result[0])

        fault = response.xpath('//fault/value/*')
        if fault:
            err = xml2py(fault[0])
            raise RemoteServerException(err.get('faultString'), err.get('faultCode'))

        raise InvalidResponse('Respond body of method "%s" not contains any response.', method_name)

    @asyncio.coroutine
    def __remote_call(self, method_name, *args, **kwargs):
        response = yield from self.client.post(
            str(self.url),
            data=etree.tostring(
                self._make_request(
                    method_name, *args, **kwargs
                ), xml_declaration=True
            ),
            headers={
                'Content-Type': u'text/xml',
                'User-Agent': self.USER_AGENT
            }
        )

        return self._parse_response((yield from response.read()), method_name)

    def __getattr__(self, method_name):
        return self[method_name]

    def __getitem__(self, method_name):
        def method(*args, **kwargs):
            return self.__remote_call(method_name, *args, **kwargs)

        return method
