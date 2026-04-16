from __future__ import annotations

import csv
import datetime
from pathlib import Path

BASELINE_DIR = Path(__file__).parent.parent / "baseline"


def _load_bl(filename: str) -> dict[int, float]:
    """Load a baseline CSV → {second: median}."""
    result: dict[int, float] = {}
    path = BASELINE_DIR / filename
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            result[int(float(row["second"]))] = float(row["median"])
    return result


def _load_hf(filename: str) -> dict[tuple[int, int], float]:
    """Load a heat-factor CSV → {(hour, slot): smooth_heat_factor}.
    slot = minute // 15 + 1  (1..4)
    """
    result: dict[tuple[int, int], float] = {}
    path = BASELINE_DIR / filename
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            key = (int(row["hour"]), int(row["slot"]))
            result[key] = float(row["smooth_heat_factor"])
    return result


# Loaded once at module import time — no runtime I/O after startup.
BL_VOL  = _load_bl("bl_SOL_VOL_b10.csv")
BL_TPS  = _load_bl("bl_TPS_b10.csv")
BL_POOL = _load_bl("bl_SOL_IN_POOL_b10.csv")
HF_VOL  = _load_hf("heat_factor_15m_SOL_VOL_b10.csv")
HF_TPS  = _load_hf("heat_factor_15m_b10.csv")
HF_POOL = _load_hf("heat_factor_15m_SOL_IN_POOL_b10.csv")


def _hf(table: dict[tuple[int, int], float], ts_ms: int) -> float:
    dt = datetime.datetime.fromtimestamp(ts_ms / 1000.0)
    return table.get((dt.hour, dt.minute // 15 + 1), 1.0)


def get_expected_vol(bucket_mid_sec: int, ts_ms: int) -> float:
    s = max(9, min(599, bucket_mid_sec))
    return BL_VOL.get(s, 0.0) * _hf(HF_VOL, ts_ms)


def get_expected_tps(bucket_mid_sec: int, ts_ms: int) -> float:
    s = max(9, min(599, bucket_mid_sec))
    return BL_TPS.get(s, 0.0) * _hf(HF_TPS, ts_ms)


def get_expected_pool(bucket_mid_sec: int, ts_ms: int) -> float:
    s = max(9, min(599, bucket_mid_sec))
    return BL_POOL.get(s, 0.0) * _hf(HF_POOL, ts_ms)
