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
            xml_response = yield from self._handle()
        except HTTPError:
            raise
        except Exception as e:
            xml_response = self._format_error(e)
            log.exception(e)

        return self._make_response(xml_response)

    @classmethod
    def _make_response(cls, xml_response, status=200, reason=None):
        response = Response(status=status, reason=reason)
        response.headers["Content-Type"] = "text/xml; charset=utf-8"

        xml_data = cls._build_xml(xml_response)

        log.debug("Sending response:\n%s", xml_data)

        response.body = xml_data
        return response

    def _parse_body(self, body):
        try:
            return self._parse_xml(body)
        except etree.DocumentInvalid:
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

    def _check_request(self):
        if 'xml' not in self.request.headers.get('Content-Type', ''):
            raise HTTPBadRequest

    @asyncio.coroutine
    def _handle(self):
        self._check_request()

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
                xml_request.xpath(
                    '//params/param/value/* | //params/param/value[not(*)]/text()'
                )
            )
        )

        if args and isinstance(args[-1], dict):
            kwargs = args.pop(-1)
        else:
            kwargs = {}

        result = yield from asyncio.coroutine(method)(*args, **kwargs)
        return self._format_success(result)

    @staticmethod
    def _format_success(result):
        xml_response = etree.Element("methodResponse")
        xml_params = etree.Element("params")
        xml_param = etree.Element("param")
        xml_value = etree.Element("value")

        xml_value.append(py2xml(result))
        xml_param.append(xml_value)
        xml_params.append(xml_param)
        xml_response.append(xml_params)
        return xml_response

    @staticmethod
    def _format_error(exception: Exception):
        xml_response = etree.Element('methodResponse')
        xml_fault = etree.Element('fault')
        xml_value = etree.Element('value')

        xml_value.append(py2xml(exception))
        xml_fault.append(xml_value)
        xml_response.append(xml_fault)
        return xml_response

    @staticmethod
    def _parse_xml(xml_string):
        parser = etree.XMLParser(resolve_entities=False)
        root = etree.fromstring(xml_string, parser)
        schema.assertValid(root)
        return root

    @classmethod
    def _build_xml(cls, tree):
        return etree.tostring(
            tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=cls.DEBUG
        )
