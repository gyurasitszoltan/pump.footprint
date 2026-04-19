from __future__ import annotations

import asyncio
import os
from pathlib import Path

from aiohttp import web
import orjson

from .ws_server import WsServer
from . import trade_storage

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"


async def handle_all_trades(request: web.Request) -> web.Response:
    mint = request.match_info["mint"]
    trades = await asyncio.to_thread(trade_storage.read_all_trades, mint)
    return web.Response(
        body=orjson.dumps({"trades": trades, "mint": mint}),
        content_type="application/json",
    )


async def handle_bucket_trades(request: web.Request) -> web.Response:
    mint = request.match_info["mint"]
    try:
        bucket = int(request.match_info["bucket"])
    except ValueError:
        return web.json_response({"error": "invalid bucket"}, status=400)

    if bucket < 0 or bucket >= 60:
        return web.json_response({"error": "bucket must be 0-59"}, status=400)

    trades = await asyncio.to_thread(trade_storage.read_bucket_trades, mint, bucket)
    return web.Response(
        body=orjson.dumps({"trades": trades, "bucket": bucket, "mint": mint}),
        content_type="application/json",
    )


def create_app(ws_server: WsServer) -> web.Application:
    app = web.Application()
    app["ws_server"] = ws_server

    app.router.add_get("/ws", ws_server.handle_ws)
    app.router.add_get("/api/trades/{mint}/all", handle_all_trades)
    app.router.add_get("/api/trades/{mint}/{bucket}", handle_bucket_trades)

    if FRONTEND_DIST.is_dir():
        # Serve index.html for SPA routes
        async def index_handler(request: web.Request) -> web.StreamResponse:
            return web.FileResponse(FRONTEND_DIST / "index.html")

        # Static assets (js, css, etc.)
        app.router.add_static("/assets", FRONTEND_DIST / "assets", show_index=False)
        # Favicon and other root files
        for f in FRONTEND_DIST.iterdir():
            if f.is_file() and f.name != "index.html":
                app.router.add_get(f"/{f.name}", lambda req, path=f: web.FileResponse(path))
        # SPA fallback: all other routes serve index.html
        app.router.add_get("/{tail:.*}", index_handler)
    else:
        async def dev_handler(request: web.Request) -> web.Response:
            return web.Response(
                text="Frontend not built. Run: cd frontend && npm run build",
                content_type="text/plain",
            )
        app.router.add_get("/{tail:.*}", dev_handler)

    return app
