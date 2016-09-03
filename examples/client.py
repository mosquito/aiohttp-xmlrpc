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
