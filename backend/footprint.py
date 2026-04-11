from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CellData:
    buy_vol: float = 0.0
    sell_vol: float = 0.0

    @property
    def delta(self) -> float:
        return self.buy_vol - self.sell_vol

    @property
    def total(self) -> float:
        return self.buy_vol + self.sell_vol

    def to_dict(self) -> dict:
        return {
            "buy": round(self.buy_vol, 2),
            "sell": round(self.sell_vol, 2),
            "delta": round(self.delta, 2),
        }


@dataclass
class BucketOHLC:
    open_mc: float = 0.0
    close_mc: float = 0.0
    high_mc: float = 0.0
    low_mc: float = 0.0

    def update(self, mc_usd: float):
        if self.open_mc == 0.0:
            self.open_mc = mc_usd
            self.high_mc = mc_usd
            self.low_mc = mc_usd
        self.close_mc = mc_usd
        if mc_usd > self.high_mc:
            self.high_mc = mc_usd
        if mc_usd < self.low_mc:
            self.low_mc = mc_usd

    @property
    def is_bull(self) -> bool:
        return self.close_mc >= self.open_mc

    def to_dict(self) -> dict:
        return {
            "o": round(self.open_mc, 1),
            "c": round(self.close_mc, 1),
            "h": round(self.high_mc, 1),
            "l": round(self.low_mc, 1),
        }


@dataclass
class BucketStats:
    volume: float = 0.0
    delta: float = 0.0
    trades: int = 0

    def to_dict(self) -> dict:
        return {
            "vol": round(self.volume, 2),
            "delta": round(self.delta, 2),
            "trades": self.trades,
        }
