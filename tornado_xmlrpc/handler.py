# encoding: utf-8
import logging
from tornado.gen import coroutine, maybe_future
from tornado.web import RequestHandler, HTTPError
from lxml import etree
from .common import get_schema, xml2py, py2xml


log = logging.getLogger(__name__)


class XMLRPCHandler(RequestHandler):
    METHOD_PREFIX = "rpc_"
    DEBUG = False

    @coroutine
    def post(self, *args, **kwargs):
        if 'xml' not in self.request.headers.get('Content-Type', ''):
            raise HTTPError(400)

        try:
            xml_request = self._parse_xml(self.request.body)
        except etree.XMLSyntaxError:
            raise HTTPError(400)

        method_name = xml_request.xpath('//methodName[1]')[0].text
        method = getattr(self, "{0}{1}".format(self.METHOD_PREFIX, method_name), None)

        if not callable(method):
            log.warning("Can't find method %s%s in ",
                        self.METHOD_PREFIX,
                        method_name,
                        self.__class__.__name__)

            raise HTTPError(404)

        log.info("RPC Call: %s => %s.%s.%s",
                 method_name,
                 method.__module__,
                 method.__class__.__name__,
                 method.__name__)

        args = list(map(
            xml2py,
            xml_request.xpath('//params/param/value/*')
        ))

        if args and isinstance(args[-1], dict):
            kwargs = args.pop(-1)
        else:
            kwargs = {}

        try:
            root = etree.Element("methodResponse")
            el_params = etree.Element("params")
            el_param = etree.Element("param")
            el_value = etree.Element("value")
            el_param.append(el_value)
            el_params.append(el_param)
            root.append(el_params)

            result = yield maybe_future(method(*args, **kwargs))

            el_value.append(py2xml(result))
        except Exception as e:
            root = etree.Element('methodResponse')
            xml_fault = etree.Element('fault')
            xml_value = etree.Element('value')

            root.append(xml_fault)
            xml_fault.append(xml_value)

            xml_value.append(py2xml({
                "faultCode": getattr(e, 'code', -32500),
                "faultString": repr(e),
            }))

            log.exception(e)

        self.set_header("Content-Type", "text/xml; charset=utf-8")
        xml = self._build_xml(root)

        if self.DEBUG:
            log.debug("Sending response:\n%s", xml)

        self.finish(xml)

    @staticmethod
    def _parse_xml(xml_string):
        return etree.fromstring(xml_string, get_schema())

    @classmethod
    def _build_xml(cls, tree):
        return etree.tostring(
            tree,
            xml_declaration=True,
            encoding="utf-8",
            pretty_print=cls.DEBUG
        )
