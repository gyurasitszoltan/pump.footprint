from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING

import orjson
import websockets

from .const import FEEDER_URI

if TYPE_CHECKING:
    from .token_manager import TokenManager
    from .ws_server import WsServer

log = logging.getLogger(__name__)

# Migrate events we care about
TRUSTED_MIGRATE_POOLS = {"pump-amm"}
TRUSTED_POOL_CREATORS = {"pump"}


async def feeder_loop(token_manager: TokenManager, ws_server: WsServer):
    """Connect to the local feeder and process events forever (with reconnect)."""
    backoff = 1
    while True:
        try:
            log.info("Connecting to feeder: %s", FEEDER_URI)
            async with websockets.connect(FEEDER_URI, max_size=2**20) as ws:
                log.info("Connected to feeder")
                backoff = 1
                async for raw in ws:
                    try:
                        event = orjson.loads(raw)
                    except Exception:
                        continue
                    await _handle_event(event, token_manager, ws_server)
        except (websockets.ConnectionClosed, ConnectionRefusedError, OSError) as e:
            log.warning("Feeder connection lost (%s), reconnecting in %ds...", e, backoff)
        except Exception:
            log.exception("Unexpected feeder error, reconnecting in %ds...", backoff)

        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, 30)


async def _handle_event(event: dict, token_manager: TokenManager, ws_server: WsServer):
    tx_type = event.get("txType")
    if tx_type is None:
        return

    if tx_type == "create":
        log.info("CREATE %s (%s) pool=%s", event.get("mint", "?")[:12], event.get("symbol", "?"), event.get("pool", "?"))
        return

    if tx_type == "migrate":
        pool = event.get("pool", "")
        creator = event.get("poolCreatedBy", "")
        if pool in TRUSTED_MIGRATE_POOLS and creator in TRUSTED_POOL_CREATORS:
            token_manager.activate_token(event)
        return

    if tx_type in ("buy", "sell"):
        mint = event.get("mint")
        if mint is None or not token_manager.is_active(mint):
            return
        if "solAmount" not in event or "marketCapSol" not in event:
            return
        update = token_manager.process_trade(event)
        if update:
            await ws_server.broadcast_footprint_update(update)
