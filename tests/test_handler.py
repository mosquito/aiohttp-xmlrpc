#!/usr/bin/env python
# encoding: utf-8
import tornado.testing
from tornado.testing import gen_test
from tornado.web import Application

from . import handler, client


class XMLRPCTestHandler(handler.XMLRPCHandler):
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


class TestSimple(tornado.testing.AsyncHTTPTestCase):
    def setUp(self):
        super(TestSimple, self).setUp()
        self.server = client.ServerProxy("http://localhost:%d" % self.get_http_port())

    def tearDown(self):
        super(TestSimple, self).tearDown()
        self.server = None

    def get_app(self):
        return Application(handlers=[
            ('/', XMLRPCTestHandler),
        ])

    @gen_test
    def test_00_test(self):
        result = yield self.server.test()
        self.assertTrue(result is None)

    @gen_test
    def test_10_args(self):
        result = yield self.server.args(1, 2, 3, 4, 5)
        self.assertTrue(result == 5)

    @gen_test
    def test_20_kwargs(self):
        result = yield self.server.kwargs(foo=1, bar=2)
        self.assertTrue(result == 2)

    @gen_test
    def test_20_kwargs(self):
        result = yield self.server.args_kwargs(1, 2, 3, 4, 5, foo=1, bar=2)
        self.assertTrue(result == 7)

    @gen_test
    def test_30_exception(self):
        try:
            yield self.server.exception()
        except client.RemoteServerException as e:
            self.assertTrue("YEEEEEE!!!" in e.message)
        else:
            raise RuntimeError("No exception")
