import asyncio

from aiohttp import web

from game import create_game_handler


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('GET', '/', create_game_handler(loop))

    server = await loop.create_server(app.make_handler(), 'localhost', 8765)
    return server


loop = asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()
