from aiohttp import web
from aiohttp_xmlrpc import handler
from aiohttp_xmlrpc.handler import rename


class XMLRPCExample(handler.XMLRPCView):

    @rename("nested.test")
    def rpc_test(self):
        return None

    def rpc_args(self, *args):
        return len(args)

    def rpc_kwargs(self, **kwargs):
        return len(kwargs)

    def rpc_args_kwargs(self, *args, **kwargs):
        return len(args) + len(kwargs)

    @rename("nested.exception")
    def rpc_exception(self):
        raise Exception("YEEEEEE!!!")


app = web.Application()
app.router.add_route('*', '/', XMLRPCExample)

if __name__ == "__main__":
    web.run_app(app)
