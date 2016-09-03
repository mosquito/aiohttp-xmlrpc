import asyncio

import pytest
from aiohttp import web
from aiohttp_xmlrpc import handler
from aiohttp_xmlrpc.client import RemoteServerException

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
    with pytest.raises(RemoteServerException):
        yield from client.exception()
