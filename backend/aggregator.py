from __future__ import annotations

from .const import (
    SOL_USD, MAX_DURATION_SEC, TIME_BUCKET_10S, NUM_BUCKETS_10S,
    NUM_BUCKETS_1S, MC_LEVEL_SIZE, INITIAL_MC_LOW, INITIAL_MC_HIGH,
    IMBALANCE_RATIO, RSI_PERIOD, TRADE_SIZE_BINS,
)
from .footprint import CellData, BucketOHLC, BucketStats


class Aggregator:
    """Per-token aggregation: 1s buckets (RSI) + 10s buckets (footprint chart)."""

    def __init__(self, migrate_ts_ms: int):
        self.migrate_ts_ms = migrate_ts_ms

        # 1s buckets: only close_mc for RSI
        self.close_1s: list[float | None] = [None] * NUM_BUCKETS_1S

        # 10s buckets
        self.cells: dict[tuple[int, int], CellData] = {}  # (bucket_idx, mc_level) -> CellData
        self.ohlc: dict[int, BucketOHLC] = {}              # bucket_idx -> OHLC
        self.stats: dict[int, BucketStats] = {}            # bucket_idx -> stats

        # Y-axis range
        self.mc_low = INITIAL_MC_LOW
        self.mc_high = INITIAL_MC_HIGH

        # Track last mc for summary
        self.last_mc_usd: float = 0.0
        self.last_trade_bucket: int = 0

    def process_trade(self, tx_type: str, sol_amount: float,
                      market_cap_sol: float, timestamp: int) -> dict:
        """Process a single trade event. Returns update info dict."""
        rel_ms = timestamp - self.migrate_ts_ms
        rel_sec = rel_ms / 1000.0
        if rel_sec < 0:
            rel_sec = 0
        if rel_sec >= MAX_DURATION_SEC:
            rel_sec = MAX_DURATION_SEC - 0.001

        mc_usd = market_cap_sol * SOL_USD
        self.last_mc_usd = mc_usd
        sol_amount = abs(sol_amount)

        # 1s bucket
        bucket_1s = int(rel_sec)
        if 0 <= bucket_1s < NUM_BUCKETS_1S:
            self.close_1s[bucket_1s] = mc_usd

        # 10s bucket
        bucket_10s = min(int(rel_sec // TIME_BUCKET_10S), NUM_BUCKETS_10S - 1)
        mc_level = int(mc_usd // MC_LEVEL_SIZE) * MC_LEVEL_SIZE
        self.last_trade_bucket = bucket_10s

        # Expand Y range if needed
        mc_levels_expanded = None
        if mc_level < self.mc_low:
            self.mc_low = mc_level
            mc_levels_expanded = True
        if mc_level + MC_LEVEL_SIZE > self.mc_high:
            self.mc_high = mc_level + MC_LEVEL_SIZE
            mc_levels_expanded = True

        # Update cell
        key = (bucket_10s, mc_level)
        cell = self.cells.get(key)
        if cell is None:
            cell = CellData()
            self.cells[key] = cell

        if tx_type == "buy":
            cell.buy_vol += sol_amount
        else:
            cell.sell_vol += sol_amount

        # Update OHLC
        ohlc = self.ohlc.get(bucket_10s)
        if ohlc is None:
            ohlc = BucketOHLC()
            self.ohlc[bucket_10s] = ohlc
        ohlc.update(mc_usd)

        # Update stats
        stats = self.stats.get(bucket_10s)
        if stats is None:
            stats = BucketStats()
            self.stats[bucket_10s] = stats
        stats.volume += sol_amount
        stats.trades += 1
        if tx_type == "buy":
            stats.buy_vol += sol_amount
            stats.delta += sol_amount
        else:
            stats.sell_vol += sol_amount
            stats.delta -= sol_amount

        # Trade size bins
        num_bins = len(TRADE_SIZE_BINS) + 1
        stats.ensure_bins(num_bins)
        bin_idx = num_bins - 1  # default: largest bin
        for i, threshold in enumerate(TRADE_SIZE_BINS):
            if sol_amount < threshold:
                bin_idx = i
                break
        side = "buy" if tx_type == "buy" else "sell"
        stats.size_bins[bin_idx][side] += sol_amount

        # Compute imbalance for the updated cell + neighbors
        imbalance_updates = self._compute_imbalance_around(bucket_10s, mc_level)

        # POC for this bucket
        poc_level = self._compute_poc(bucket_10s)

        return {
            "bucket": bucket_10s,
            "mc_level": mc_level,
            "cell": cell.to_dict(),
            "ohlc": ohlc.to_dict(),
            "stats": stats.to_dict(),
            "poc": poc_level,
            "mc_levels_expanded": self.get_mc_levels() if mc_levels_expanded else None,
            "max_abs_delta": self._max_abs_delta(),
            "imbalance_updates": imbalance_updates,
        }

    def _compute_poc(self, bucket_idx: int) -> int | None:
        """Point of Control: mc_level with highest total volume in this bucket."""
        best_level = None
        best_vol = 0.0
        for (bi, ml), cell in self.cells.items():
            if bi == bucket_idx and cell.total > best_vol:
                best_vol = cell.total
                best_level = ml
        return best_level

    def _compute_imbalance_around(self, bucket_idx: int, mc_level: int) -> list[dict]:
        """Compute imbalance flags for the cell and its vertical neighbors."""
        updates = []
        for level in [mc_level - MC_LEVEL_SIZE, mc_level, mc_level + MC_LEVEL_SIZE]:
            cell = self.cells.get((bucket_idx, level))
            if cell is None:
                continue
            buy_imb = False
            sell_imb = False

            # Buy imbalance: this level's buy vs. level below's sell
            below = self.cells.get((bucket_idx, level - MC_LEVEL_SIZE))
            if below and below.sell_vol > 0 and cell.buy_vol / below.sell_vol >= IMBALANCE_RATIO:
                buy_imb = True

            # Sell imbalance: this level's sell vs. level above's buy
            above = self.cells.get((bucket_idx, level + MC_LEVEL_SIZE))
            if above and above.buy_vol > 0 and cell.sell_vol / above.buy_vol >= IMBALANCE_RATIO:
                sell_imb = True

            updates.append({
                "bucket": bucket_idx,
                "mc_level": level,
                "buy_imb": buy_imb,
                "sell_imb": sell_imb,
            })
        return updates

    def _max_abs_delta(self) -> float:
        if not self.cells:
            return 1.0
        return max((abs(c.delta) for c in self.cells.values()), default=1.0) or 1.0

    def compute_rsi14(self) -> float | None:
        """Wilder's RSI from 1-second close values."""
        closes = [v for v in self.close_1s if v is not None]
        if len(closes) < RSI_PERIOD + 1:
            return None

        changes = [closes[i] - closes[i - 1] for i in range(1, len(closes))]

        # Use last RSI_PERIOD changes
        recent = changes[-(RSI_PERIOD):]
        gains = [c for c in recent if c > 0]
        losses = [-c for c in recent if c < 0]

        avg_gain = sum(gains) / RSI_PERIOD if gains else 0.0
        avg_loss = sum(losses) / RSI_PERIOD if losses else 0.0

        if avg_loss == 0:
            return 100.0 if avg_gain > 0 else 50.0

        rs = avg_gain / avg_loss
        return round(100.0 - (100.0 / (1.0 + rs)), 1)

    def get_mc_levels(self) -> list[int]:
        """All mc_levels in descending order."""
        return list(range(self.mc_high, self.mc_low - MC_LEVEL_SIZE, -MC_LEVEL_SIZE))

    def get_all_poc(self) -> dict[int, int | None]:
        """POC for every bucket that has data."""
        poc = {}
        # Group cells by bucket
        bucket_cells: dict[int, list[tuple[int, CellData]]] = {}
        for (bi, ml), cell in self.cells.items():
            bucket_cells.setdefault(bi, []).append((ml, cell))
        for bi, cells in bucket_cells.items():
            best_level = max(cells, key=lambda x: x[1].total)[0]
            poc[bi] = best_level
        return poc

    def get_all_imbalances(self) -> dict[str, dict]:
        """Imbalance flags for all cells."""
        result = {}
        for (bi, ml), cell in self.cells.items():
            buy_imb = False
            sell_imb = False
            below = self.cells.get((bi, ml - MC_LEVEL_SIZE))
            if below and below.sell_vol > 0 and cell.buy_vol / below.sell_vol >= IMBALANCE_RATIO:
                buy_imb = True
            above = self.cells.get((bi, ml + MC_LEVEL_SIZE))
            if above and above.buy_vol > 0 and cell.sell_vol / above.buy_vol >= IMBALANCE_RATIO:
                sell_imb = True
            if buy_imb or sell_imb:
                result[f"{bi}:{ml}"] = {"buy_imb": buy_imb, "sell_imb": sell_imb}
        return result

    def get_snapshot(self) -> dict:
        """Full footprint snapshot for frontend."""
        cells_dict = {}
        for (bi, ml), cell in self.cells.items():
            cells_dict[f"{bi}:{ml}"] = cell.to_dict()

        ohlc_dict = {str(bi): o.to_dict() for bi, o in self.ohlc.items()}
        stats_dict = {str(bi): s.to_dict() for bi, s in self.stats.items()}
        poc = {str(bi): ml for bi, ml in self.get_all_poc().items()}
        imbalances = self.get_all_imbalances()

        # Merge imbalance flags into cells
        for key, imb in imbalances.items():
            if key in cells_dict:
                cells_dict[key]["buy_imb"] = imb["buy_imb"]
                cells_dict[key]["sell_imb"] = imb["sell_imb"]

        return {
            "mc_levels": self.get_mc_levels(),
            "cells": cells_dict,
            "ohlc": ohlc_dict,
            "stats": stats_dict,
            "poc": poc,
            "rsi14": self.compute_rsi14(),
            "current_bucket": self.last_trade_bucket,
            "max_abs_delta": self._max_abs_delta(),
            "size_bins": TRADE_SIZE_BINS,
        }

    def get_trades_last_bucket(self) -> int:
        """Trade count in the most recent active bucket."""
        stats = self.stats.get(self.last_trade_bucket)
        return stats.trades if stats else 0

    def to_dict(self) -> dict:
        """Serialize full aggregator state for persistence."""
        cells = {f"{bi}:{ml}": c.to_dict() for (bi, ml), c in self.cells.items()}
        ohlc = {str(bi): o.to_dict() for bi, o in self.ohlc.items()}
        stats = {str(bi): s.to_dict() for bi, s in self.stats.items()}
        return {
            "close_1s": self.close_1s,
            "cells": cells,
            "ohlc": ohlc,
            "stats": stats,
            "mc_low": self.mc_low,
            "mc_high": self.mc_high,
            "last_mc_usd": self.last_mc_usd,
            "last_trade_bucket": self.last_trade_bucket,
        }

    @classmethod
    def from_dict(cls, migrate_ts_ms: int, d: dict) -> Aggregator:
        """Restore aggregator from persisted dict."""
        agg = cls(migrate_ts_ms)
        agg.close_1s = d["close_1s"]
        for key, cd in d["cells"].items():
            bi, ml = key.split(":")
            agg.cells[(int(bi), int(ml))] = CellData.from_dict(cd)
        for bi_str, od in d["ohlc"].items():
            agg.ohlc[int(bi_str)] = BucketOHLC.from_dict(od)
        for bi_str, sd in d["stats"].items():
            agg.stats[int(bi_str)] = BucketStats.from_dict(sd)
        agg.mc_low = d["mc_low"]
        agg.mc_high = d["mc_high"]
        agg.last_mc_usd = d["last_mc_usd"]
        agg.last_trade_bucket = d["last_trade_bucket"]
        return agg
