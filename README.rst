Tornado XMLRPC
==============

.. image:: https://travis-ci.org/mosquito/tornado-xmlrpc.svg
    :target: https://travis-ci.org/mosquito/tornado-xmlrpc

.. image:: https://img.shields.io/pypi/v/tornado-xmlrpc.svg
    :target: https://pypi.python.org/pypi/tornado-xmlrpc/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/wheel/tornado-xmlrpc.svg
    :target: https://pypi.python.org/pypi/tornado-xmlrpc/

.. image:: https://img.shields.io/pypi/pyversions/tornado-xmlrpc.svg
    :target: https://pypi.python.org/pypi/tornado-xmlrpc/

.. image:: https://img.shields.io/pypi/l/tornado-xmlrpc.svg
    :target: https://pypi.python.org/pypi/tornado-xmlrpc/


XML-RPC server and client implementation based on tornado. Using lxml and AsyncHttpClient.


Example:

.. code-block:: python

    from tornado_xmlrpc import handler, client
    from tornado.testing import *


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
            self.assertIsNone(result)

        @gen_test
        def test_10_args(self):
            result = yield self.server.args(1, 2, 3, 4, 5)
            self.assertEqual(result, 5)

        @gen_test
        def test_20_kwargs(self):
            result = yield self.server.kwargs(foo=1, bar=2)
            self.assertEqual(result, 2)

        @gen_test
        def test_20_kwargs(self):
            result = yield self.server.args_kwargs(1, 2, 3, 4, 5, foo=1, bar=2)
            self.assertEqual(result, 7)

        @gen_test
        def test_30_exception(self):
            try:
                yield self.server.exception()
            except client.RemoteServerException as e:
                self.assertIn("YEEEEEE!!!", e.message)
            else:
                raise RuntimeError("No exception")

