import asyncio
import pytest
from aiohttp.test_utils import TestClient, TestServer
from .client import ServerProxy


@pytest.yield_fixture
def test_rpc_client(loop):
    test_client = None
    rpc_client = None

    @asyncio.coroutine
    def _create_from_app_factory(app_factory, *args, **kwargs):
        nonlocal test_client, rpc_client
        app = app_factory(loop, *args, **kwargs)
        test_client = TestClient(TestServer(app), loop=loop)
        yield from test_client.start_server()

        rpc_client = ServerProxy(
            '',
            loop=loop,
            client=test_client
        )
        return rpc_client

    yield _create_from_app_factory

    if rpc_client:
        loop.run_until_complete(rpc_client.close())
        rpc_client = None

    if test_client:
        loop.run_until_complete(test_client.close())
        test_client = None
