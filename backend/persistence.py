from __future__ import annotations

import logging
from pathlib import Path
from typing import TYPE_CHECKING

import orjson

from .aggregator import Aggregator

if TYPE_CHECKING:
    from .token_manager import TokenState

log = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def save_token(state: TokenState):
    """Save expired token to output/<mint>.json."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "mint": state.mint,
        "name": state.name,
        "symbol": state.symbol,
        "migrate_ts_ms": state.migrate_ts_ms,
        "pool": state.pool,
        "aggregator": state.aggregator.to_dict(),
    }

    path = OUTPUT_DIR / f"{state.mint}.json"
    path.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))
    log.info("Saved expired token: %s (%s) → %s", state.mint[:12], state.symbol, path)


def load_all_expired() -> list[dict]:
    """Load all saved tokens from output/*.json. Returns raw dicts."""
    if not OUTPUT_DIR.is_dir():
        return []

    results = []
    for f in OUTPUT_DIR.glob("*.json"):
        try:
            data = orjson.loads(f.read_bytes())
            results.append(data)
            log.info("Loaded expired token: %s (%s)", data.get("mint", "?")[:12], data.get("symbol", "?"))
        except Exception:
            log.exception("Failed to load %s", f)

    log.info("Loaded %d expired tokens from %s", len(results), OUTPUT_DIR)
    return results
