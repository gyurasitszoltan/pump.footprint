from __future__ import annotations

import logging
from pathlib import Path

import orjson

from .const import TRADES_DIR, NUM_BUCKETS_10S

log = logging.getLogger(__name__)

# Keep open file handles per token (only handles in memory, not data)
_handles: dict[str, object] = {}


def _ensure_dir():
    TRADES_DIR.mkdir(parents=True, exist_ok=True)


def append_trade(mint: str, record: dict):
    """Append a single trade record as one JSONL line."""
    fh = _handles.get(mint)
    if fh is None:
        _ensure_dir()
        path = TRADES_DIR / f"{mint}.jsonl"
        fh = open(path, "ab")
        _handles[mint] = fh
    fh.write(orjson.dumps(record) + b"\n")
    fh.flush()


def read_bucket_trades(mint: str, bucket_idx: int) -> list[dict]:
    """Read all trades for a specific bucket from the JSONL file."""
    if bucket_idx < 0 or bucket_idx >= NUM_BUCKETS_10S:
        return []

    path = TRADES_DIR / f"{mint}.jsonl"
    if not path.exists():
        return []

    trades = []
    with open(path, "rb") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = orjson.loads(line)
                if rec.get("b") == bucket_idx:
                    trades.append({
                        "ts": rec["ts"],
                        "side": rec["s"],
                        "sol": rec["sol"],
                        "mc": rec["mc"],
                        "wallet": rec["w"],
                    })
            except Exception:
                continue
    return trades


def close_token(mint: str):
    """Close file handle for an expired token."""
    fh = _handles.pop(mint, None)
    if fh is not None:
        try:
            fh.close()
        except Exception:
            pass
