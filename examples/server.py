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
