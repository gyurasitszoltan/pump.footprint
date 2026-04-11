#!/usr/bin/env python3
"""Pump.fun Footprint Chart - Main server entry point."""

import asyncio
import logging

from aiohttp import web

from backend.const import SERVER_PORT
from backend.feeder import feeder_loop
from backend.http_server import create_app
from backend.token_manager import TokenManager
from backend.ws_server import WsServer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("server")


async def main():
    token_manager = TokenManager()
    token_manager.load_expired()
    ws_server = WsServer(token_manager)
    token_manager.set_ws_server(ws_server)

    app = create_app(ws_server)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", SERVER_PORT)
    await site.start()
    log.info("Server running on http://0.0.0.0:%d", SERVER_PORT)

    ws_server.start_summary_broadcast()

    # Feeder loop runs forever (with reconnect)
    await feeder_loop(token_manager, ws_server)


if __name__ == "__main__":
    asyncio.run(main())
