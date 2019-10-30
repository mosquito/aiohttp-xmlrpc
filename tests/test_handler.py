import asyncio
import datetime

import pytest
from aiohttp import web
from aiohttp_xmlrpc import handler
from aiohttp_xmlrpc.exceptions import ApplicationError
from lxml import etree
from lxml.builder import E

pytest_plugins = (
    'aiohttp.pytest_plugin',
    'aiohttp_xmlrpc.pytest_plugin',
)


class XMLRPCMain(handler.XMLRPCView):
    def rpc_test(self):
        return None

    def rpc_args(self, *args):
        return len(args)

    def rpc_kwargs(self, **kwargs):
        return len(kwargs)

    def rpc_args_kwargs(self, *args, **kwargs):
        return len(args) + len(kwargs)

    def rpc_exception(self):
        raise Exception("YEEEEEE!!!")

    def rpc_strings(self, s1, s2):
        return s1 == s2

    def rpc_datetime(self, test_datetime_1, test_datetime_2):
        return test_datetime_1, test_datetime_2


def create_app(loop):
    app = web.Application(loop=loop)
    app.router.add_route('*', '/', XMLRPCMain)
    return app


@pytest.fixture
def client(loop, test_rpc_client):
    return loop.run_until_complete(test_rpc_client(create_app))


@asyncio.coroutine
def test_1_test(client):
    result = yield from client.test()
    assert result is None


@asyncio.coroutine
def test_2_args(client):
    result = yield from client.args(1, 2, 3, 4, 5)
    assert result == 5


@asyncio.coroutine
def test_3_kwargs(client):
    result = yield from client.kwargs(foo=1, bar=2)
    assert result == 2


@asyncio.coroutine
def test_4_kwargs(client):
    result = yield from client.args_kwargs(1, 2, 3, 4, 5, foo=1, bar=2)
    assert result == 7


@asyncio.coroutine
def test_5_exception(client):
    with pytest.raises(Exception):
        yield from client.exception()


@asyncio.coroutine
def test_6_unknown_method(client):
    with pytest.raises(ApplicationError):
        yield from client['unknown_method']()


@asyncio.coroutine
def test_7_strings(test_client):
    request = E.methodCall(
        E.methodName('strings'),
        E.params(
            E.param(
                E.value('Some string')
            ),
            E.param(
                E.value(
                    E.string('Some string')
                )
            )
        )
    )
    client = yield from test_client(create_app)

    resp = yield from client.post(
        '/',
        data=etree.tostring(request, xml_declaration=True),
        headers={'Content-Type': 'text/xml'}
    )
    assert resp.status == 200

    root = etree.fromstring((yield from resp.read()))
    assert root.xpath('//value/boolean/text()')[0] == '1'


@asyncio.coroutine
def test_8_strings_pretty(test_client):
    request = E.methodCall(
        E.methodName('strings'),
        E.params(
            E.param(
                E.value('Some string')
            ),
            E.param(
                E.value(
                    E.string('Some string')
                )
            )
        )
    )
    client = yield from test_client(create_app)

    resp = yield from client.post(
        '/',
        data=etree.tostring(request, xml_declaration=True, pretty_print=True),
        headers={'Content-Type': 'text/xml'}
    )
    assert resp.status == 200

    root = etree.fromstring((yield from resp.read()))
    assert root.xpath('//value/boolean/text()')[0] == '1'


@asyncio.coroutine
def test_9_datetime(test_client):
    resp_date = datetime.datetime.now().strftime("%Y%m%dT%H:%M:%S")
    test_date = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    request = E.methodCall(
        E.methodName('datetime'),
        E.params(
            E.param(
                E.value(
                    E("dateTime.iso8601", test_date)
                )
            ),
            E.param(
                E.value(
                    E("dateTime.iso8601", resp_date)
                )
            )
        )
    )
    client = yield from test_client(create_app)

    resp = yield from client.post(
        '/',
        data=etree.tostring(request, xml_declaration=True, pretty_print=True),
        headers={'Content-Type': 'text/xml'}
    )
    assert resp.status == 200

    root = etree.fromstring((yield from resp.read()))
    assert root.xpath('//value/dateTime.iso8601/text()')[0] == resp_date
    assert root.xpath('//value/dateTime.iso8601/text()')[1] == resp_date
