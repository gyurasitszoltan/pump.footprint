from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import orjson
from aiohttp import web

if TYPE_CHECKING:
    from .token_manager import TokenManager

log = logging.getLogger(__name__)


class WsServer:
    def __init__(self, token_manager: TokenManager):
        self.token_manager = token_manager
        self.clients: dict[web.WebSocketResponse, str | None] = {}  # ws -> subscribed mint
        self._summary_task: asyncio.Task | None = None

    def start_summary_broadcast(self):
        self._summary_task = asyncio.ensure_future(self._summary_loop())

    async def _summary_loop(self):
        """Broadcast individual token summary updates every 2 seconds."""
        while True:
            await asyncio.sleep(2)
            if not self.clients:
                continue
            for summary in self.token_manager.get_token_summaries(include_expired=False):
                msg = orjson.dumps({"type": "token_summary_update", **summary})
                await self._broadcast_all(msg)

    async def handle_ws(self, request: web.Request) -> web.WebSocketResponse:
        ws = web.WebSocketResponse()
        await ws.prepare(request)
        self.clients[ws] = None
        log.info("Client connected (%d total)", len(self.clients))

        # Send current token list
        summaries = self.token_manager.get_token_summaries()
        await self._send(ws, {"type": "token_list", "tokens": summaries})

        try:
            async for msg in ws:
                if msg.type == web.WSMsgType.TEXT:
                    await self._handle_client_msg(ws, msg.data)
                elif msg.type in (web.WSMsgType.ERROR, web.WSMsgType.CLOSE):
                    break
        finally:
            self.clients.pop(ws, None)
            log.info("Client disconnected (%d remain)", len(self.clients))

        return ws

    async def _handle_client_msg(self, ws: web.WebSocketResponse, raw: str):
        try:
            data = orjson.loads(raw)
        except Exception:
            return

        msg_type = data.get("type")

        if msg_type == "select_token":
            mint = data.get("mint")
            self.clients[ws] = mint
            if mint:
                snapshot = self.token_manager.get_footprint_snapshot(mint)
                if snapshot:
                    await self._send(ws, snapshot)

        elif msg_type == "unselect_token":
            self.clients[ws] = None

        elif msg_type == "delete_token":
            mint = data.get("mint")
            if mint:
                await self.token_manager.delete_token(mint)

        elif msg_type == "like_token":
            mint = data.get("mint")
            liked = bool(data.get("liked", False))
            if mint:
                await self.token_manager.like_token(mint, liked)

    async def broadcast_token_added(self, token_summary: dict):
        msg = orjson.dumps({"type": "token_added", "token": token_summary})
        await self._broadcast_all(msg)

    async def broadcast_token_liked(self, mint: str, liked: bool):
        msg = orjson.dumps({"type": "token_liked", "mint": mint, "liked": liked})
        await self._broadcast_all(msg)

    async def broadcast_token_removed(self, mint: str):
        msg = orjson.dumps({"type": "token_removed", "mint": mint})
        await self._broadcast_all(msg)

    async def broadcast_footprint_update(self, update: dict):
        mint = update.get("mint")
        if not mint:
            return
        update["type"] = "footprint_update"
        msg = orjson.dumps(update)
        for ws, subscribed_mint in list(self.clients.items()):
            if subscribed_mint == mint:
                await self._send_raw(ws, msg)

    async def _broadcast_all(self, msg: bytes):
        for ws in list(self.clients.keys()):
            await self._send_raw(ws, msg)

    async def _send(self, ws: web.WebSocketResponse, data: dict):
        try:
            await ws.send_bytes(orjson.dumps(data))
        except Exception:
            pass

    async def _send_raw(self, ws: web.WebSocketResponse, msg: bytes):
        try:
            await ws.send_bytes(msg)
        except Exception:
            pass
