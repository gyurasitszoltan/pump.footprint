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
    """Save expired token to output/<mint>/data.json."""
    token_dir = OUTPUT_DIR / state.mint
    token_dir.mkdir(parents=True, exist_ok=True)

    data = {
        "mint": state.mint,
        "name": state.name,
        "symbol": state.symbol,
        "migrate_ts_ms": state.migrate_ts_ms,
        "pool": state.pool,
        "aggregator": state.aggregator.to_dict(),
    }

    path = token_dir / "data.json"
    path.write_bytes(orjson.dumps(data, option=orjson.OPT_INDENT_2))
    log.info("Saved expired token: %s (%s) → %s", state.mint[:12], state.symbol, path)


def load_all_expired() -> list[dict]:
    """Load all saved tokens from output/*/data.json. Returns raw dicts."""
    if not OUTPUT_DIR.is_dir():
        return []

    results = []
    for token_dir in OUTPUT_DIR.iterdir():
        if not token_dir.is_dir():
            continue
        data_file = token_dir / "data.json"
        if not data_file.exists():
            continue
        try:
            data = orjson.loads(data_file.read_bytes())
            results.append(data)
            log.info("Loaded expired token: %s (%s)", data.get("mint", "?")[:12], data.get("symbol", "?"))
        except Exception:
            log.exception("Failed to load %s", data_file)

    log.info("Loaded %d expired tokens from %s", len(results), OUTPUT_DIR)
    return results
