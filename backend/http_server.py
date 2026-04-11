from __future__ import annotations

import os
from pathlib import Path

from aiohttp import web

from .ws_server import WsServer

FRONTEND_DIST = Path(__file__).parent.parent / "frontend" / "dist"


def create_app(ws_server: WsServer) -> web.Application:
    app = web.Application()
    app["ws_server"] = ws_server

    app.router.add_get("/ws", ws_server.handle_ws)

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
