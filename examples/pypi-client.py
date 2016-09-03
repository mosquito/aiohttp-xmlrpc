import asyncio
from aiohttp_xmlrpc.client import ServerProxy

loop = asyncio.get_event_loop()
client = ServerProxy("https://pypi.python.org/pypi", loop=loop)

async def main():
    pkg = 'aiohttp-xmlrpc'

    print("Requesting package info", pkg)

    releases = await client.package_releases(pkg, show_hidden=True)
    print('Releases', releases)

    user = 'mosquito'
    print("Find user packages")

    packages = await client.user_packages(user)

    print("User", user, "has packages")

    for role, package in sorted(packages[::3]):
        print("\t%r (role %r)" % (package, role))

    client.close()

if __name__ == "__main__":
    loop.run_until_complete(main())
