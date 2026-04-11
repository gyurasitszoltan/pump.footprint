from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .aggregator import Aggregator
from .const import MAX_DURATION_SEC, SOL_USD

if TYPE_CHECKING:
    from .ws_server import WsServer

log = logging.getLogger(__name__)


@dataclass
class TokenState:
    mint: str
    name: str
    symbol: str
    migrate_ts_ms: int
    pool: str
    aggregator: Aggregator
    cleanup_handle: asyncio.TimerHandle | None = None


class TokenManager:
    def __init__(self):
        self.active_tokens: dict[str, TokenState] = {}
        self._ws_server: WsServer | None = None

    def set_ws_server(self, ws_server: WsServer):
        self._ws_server = ws_server

    def activate_token(self, event: dict):
        mint = event["mint"]
        if mint in self.active_tokens:
            return

        migrate_ts_ms = event["timestamp"]
        agg = Aggregator(migrate_ts_ms)

        # Set initial mc from migrate event
        mc_sol = event.get("marketCapSol", 0)
        if mc_sol:
            agg.last_mc_usd = mc_sol * SOL_USD

        state = TokenState(
            mint=mint,
            name=event.get("name", event.get("symbol", mint[:8])),
            symbol=event.get("symbol", ""),
            migrate_ts_ms=migrate_ts_ms,
            pool=event.get("pool", ""),
            aggregator=agg,
        )

        loop = asyncio.get_event_loop()
        state.cleanup_handle = loop.call_later(
            MAX_DURATION_SEC, lambda m=mint: asyncio.ensure_future(self._remove_token(m))
        )

        self.active_tokens[mint] = state
        log.info("Token activated: %s (%s) pool=%s", mint[:12], state.symbol, state.pool)

        if self._ws_server:
            asyncio.ensure_future(self._ws_server.broadcast_token_added(self._token_summary(state)))

    async def _remove_token(self, mint: str):
        state = self.active_tokens.pop(mint, None)
        if state is None:
            return
        if state.cleanup_handle:
            state.cleanup_handle.cancel()
        log.info("Token removed: %s (%s)", mint[:12], state.symbol)
        if self._ws_server:
            await self._ws_server.broadcast_token_removed(mint)

    def process_trade(self, event: dict) -> dict | None:
        mint = event["mint"]
        state = self.active_tokens.get(mint)
        if state is None:
            return None

        sol_amount = event.get("solAmount")
        market_cap_sol = event.get("marketCapSol")
        if sol_amount is None or market_cap_sol is None:
            return None

        update = state.aggregator.process_trade(
            tx_type=event["txType"],
            sol_amount=float(sol_amount),
            market_cap_sol=float(market_cap_sol),
            timestamp=event["timestamp"],
        )
        update["mint"] = mint
        return update

    def get_token_summaries(self) -> list[dict]:
        now_ms = int(time.time() * 1000)
        return [self._token_summary(s, now_ms) for s in self.active_tokens.values()]

    def _token_summary(self, state: TokenState, now_ms: int | None = None) -> dict:
        if now_ms is None:
            now_ms = int(time.time() * 1000)
        active_sec = (now_ms - state.migrate_ts_ms) / 1000.0
        agg = state.aggregator
        return {
            "mint": state.mint,
            "name": state.name,
            "symbol": state.symbol,
            "migrate_ts_ms": state.migrate_ts_ms,
            "mc_usd": round(agg.last_mc_usd, 1),
            "trades_10s": agg.get_trades_last_bucket(),
            "rsi14": agg.compute_rsi14(),
            "active_sec": round(active_sec, 0),
        }

    def get_footprint_snapshot(self, mint: str) -> dict | None:
        state = self.active_tokens.get(mint)
        if state is None:
            return None
        snapshot = state.aggregator.get_snapshot()
        snapshot["mint"] = mint
        snapshot["type"] = "footprint_snapshot"
        return snapshot

    def is_active(self, mint: str) -> bool:
        return mint in self.active_tokens
