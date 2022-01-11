import asyncio
from aiohttp_xmlrpc.client import ServerProxy


loop = asyncio.get_event_loop()
client = ServerProxy("http://127.0.0.1:8080/", loop=loop)


async def main():
    # 'nested.test' method call
    print(await client.nested.test())

    # 'args' method call
    print(await client.args(1, 2, 3))

    await client.close()

if __name__ == "__main__":
    loop.run_until_complete(main())
