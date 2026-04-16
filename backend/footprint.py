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

    @classmethod
    def from_dict(cls, d: dict) -> CellData:
        return cls(buy_vol=d["buy"], sell_vol=d["sell"])


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

    @classmethod
    def from_dict(cls, d: dict) -> BucketOHLC:
        return cls(open_mc=d["o"], close_mc=d["c"], high_mc=d["h"], low_mc=d["l"])


@dataclass
class BucketStats:
    volume: float = 0.0
    buy_vol: float = 0.0
    sell_vol: float = 0.0
    delta: float = 0.0
    trades: int = 0
    new_wallets: int = 0
    # Trade size bins: list of {buy, sell} per bin
    # Index 0 = smallest bin, last = largest bin
    size_bins: list[dict] = field(default_factory=list)
    # RSI min/max within this 10s bucket
    rsi_min: float | None = None
    rsi_max: float | None = None
    # EMA values at the end of this 10s bucket
    ema9:  float | None = None
    ema21: float | None = None
    # Net EMA area: sum(ema9 - ema21) over each 1s close in this bucket
    ema_area: float = 0.0
    # Last known SOL in pool for this bucket
    sol_in_pool: float | None = None
    # Expected values from baseline × heat_factor
    vol_exp:  float | None = None
    tps_exp:  float | None = None
    pool_exp: float | None = None

    def ensure_bins(self, n: int):
        while len(self.size_bins) < n:
            self.size_bins.append({"buy": 0.0, "sell": 0.0})

    def to_dict(self) -> dict:
        return {
            "vol": round(self.volume, 2),
            "buy": round(self.buy_vol, 2),
            "sell": round(self.sell_vol, 2),
            "delta": round(self.delta, 2),
            "trades": self.trades,
            "neww": self.new_wallets,
            "bins": [{"buy": round(b["buy"], 2), "sell": round(b["sell"], 2)} for b in self.size_bins],
            "rsi_min": self.rsi_min,
            "rsi_max": self.rsi_max,
            "ema9":      self.ema9,
            "ema21":     self.ema21,
            "ema_area":  round(self.ema_area, 1),
            "sol_in_pool": round(self.sol_in_pool, 3) if self.sol_in_pool is not None else None,
            "vol_exp":     round(self.vol_exp,     3) if self.vol_exp     is not None else None,
            "tps_exp":     round(self.tps_exp,     3) if self.tps_exp     is not None else None,
            "pool_exp":    round(self.pool_exp,    3) if self.pool_exp    is not None else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> BucketStats:
        s = cls(
            volume=d["vol"], buy_vol=d["buy"], sell_vol=d["sell"],
            delta=d["delta"], trades=d["trades"],
            new_wallets=d.get("neww", 0),
        )
        s.size_bins = d.get("bins", [])
        s.rsi_min = d.get("rsi_min")
        s.rsi_max = d.get("rsi_max")
        s.ema9     = d.get("ema9")
        s.ema21    = d.get("ema21")
        s.ema_area = d.get("ema_area", 0.0)
        s.sol_in_pool = d.get("sol_in_pool")
        s.vol_exp     = d.get("vol_exp")
        s.tps_exp     = d.get("tps_exp")
        s.pool_exp    = d.get("pool_exp")
        return s
