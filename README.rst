AIOHTTP XMLRPC
==============

.. image:: https://travis-ci.org/mosquito/aiohttp-xmlrpc.svg
    :target: https://travis-ci.org/mosquito/aiohttp-xmlrpc

.. image:: https://img.shields.io/pypi/v/aiohttp-xmlrpc.svg
    :target: https://pypi.python.org/pypi/aiohttp-xmlrpc/
    :alt: Latest Version

.. image:: https://img.shields.io/pypi/wheel/aiohttp-xmlrpc.svg
    :target: https://pypi.python.org/pypi/aiohttp-xmlrpc/

.. image:: https://img.shields.io/pypi/pyversions/aiohttp-xmlrpc.svg
    :target: https://pypi.python.org/pypi/aiohttp-xmlrpc/

.. image:: https://img.shields.io/pypi/l/aiohttp-xmlrpc.svg
    :target: https://pypi.python.org/pypi/aiohttp-xmlrpc/


XML-RPC server and client implementation based on aiohttp. Using lxml and aiohttp.Client.


Server example
---------------

.. code-block:: python

    from aiohttp import web
    from aiohttp_xmlrpc import handler
    from tornado.testing import *


    class XMLRPCExample(handler.XMLRPCView):
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


    app = web.Application()
    app.router.add_route('*', '/', XMLRPCExample)

    if __name__ == "__main__":
        web.run_app(app)



Client example
--------------

.. code-block:: python

    import asyncio
    from aiohttp_xmlrpc.client import ServerProxy


    loop = asyncio.get_event_loop()
    client = ServerProxy("http://127.0.0.1:8080/", loop=loop)

    async def main():
        print(await client.test())

        # Or via __getitem__
        method = client['args']
        print(await method(1, 2, 3))

        client.close()

    if __name__ == "__main__":
        loop.run_until_complete(main())
