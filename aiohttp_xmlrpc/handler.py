# encoding: utf-8
import logging
import asyncio
from aiohttp.web import View, Response, HTTPBadRequest, HTTPError
from lxml import etree
from . import exceptions
from .common import schema, xml2py, py2xml


log = logging.getLogger(__name__)


class XMLRPCView(View):
    METHOD_PREFIX = "rpc_"
    DEBUG = False

    @asyncio.coroutine
    def post(self, *args, **kwargs):
        try:
            root = yield from self._handle()
        except HTTPError:
            raise
        except Exception as e:
            root = self.__format_error(e)
            log.exception(e)

        response = Response()
        response.headers["Content-Type"] = "text/xml; charset=utf-8"

        xml = self._build_xml(root)

        log.debug("Sending response:\n%s", xml)

        response.body = xml
        return response

    def _parse_body(self, body):
        try:
            return self._parse_xml(body)
        except etree.XMLSyntaxError:
            raise HTTPBadRequest

    def _lookup_method(self, method_name):
        method = getattr(self, "{0}{1}".format(self.METHOD_PREFIX, method_name), None)

        if not callable(method):
            log.warning(
                "Can't find method %s%s in %r",
                self.METHOD_PREFIX,
                method_name,
                self.__class__.__name__
            )

            raise exceptions.ApplicationError('Method %r not found' % method_name)
        return method

    @asyncio.coroutine
    def _handle(self):
        if 'xml' not in self.request.headers.get('Content-Type', ''):
            raise HTTPBadRequest

        body = yield from self.request.read()
        xml_request = self._parse_body(body)

        method_name = xml_request.xpath('//methodName[1]')[0].text
        method = self._lookup_method(method_name)

        log.info(
            "RPC Call: %s => %s.%s.%s",
            method_name,
            method.__module__,
            method.__class__.__name__,
            method.__name__
        )

        args = list(
            map(
                xml2py,
                xml_request.xpath('//params/param/value/*')
            )
        )

        if args and isinstance(args[-1], dict):
            kwargs = args.pop(-1)
        else:
            kwargs = {}

        root = etree.Element("methodResponse")
        el_params = etree.Element("params")
        el_param = etree.Element("param")
        el_value = etree.Element("value")
        el_param.append(el_value)
        el_params.append(el_param)
        root.append(el_params)

        result = yield from asyncio.coroutine(method)(*args, **kwargs)

        el_value.append(py2xml(result))

        return root

    def __format_error(self, exception: Exception):
        root = etree.Element('methodResponse')
        xml_fault = etree.Element('fault')
        xml_value = etree.Element('value')

        root.append(xml_fault)

        xml_fault.append(xml_value)
        xml_value.append(py2xml(exception))

        return root

    @staticmethod
    def _parse_xml(xml_string):
        return etree.fromstring(xml_string, schema())

    @classmethod
    def _build_xml(cls, tree):
        return etree.tostring(
            tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=cls.DEBUG
        )
