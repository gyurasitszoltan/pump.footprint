"""
Footprint chart generátor – HTML kimenet.

Minden cella: buy_vol | sell_vol (SOL-ban)
Háttérszín: zöld ha delta > 0, piros ha delta < 0

Használat:
    python footprint.py                          # első token a good_tokens.csv-ből
    python footprint.py --mint <MINT_ADDRESS>
    python footprint.py --random 5               # 5 véletlenszerű token
    python footprint.py --time-bucket 5          # 5 másodperces x-sávok
    python footprint.py --mc-level 500           # 500 USD-es y-sávok
"""
import argparse
import math
import tempfile
import webbrowser

import numpy as np
import pandas as pd

from const import MAX_DURATION_SEC, SOL_USD, GOOD_TOKENS_FILE

DATA_DIR   = "data"
TRADES_DIR = f"{DATA_DIR}/trades_migrated"

# --- Argumentumok ---
parser = argparse.ArgumentParser()
group = parser.add_mutually_exclusive_group()
group.add_argument("--mint",   type=str, default=None)
group.add_argument("--random", type=int, default=None, metavar="N")
parser.add_argument("--sol-usd",      type=float, default=SOL_USD, help="SOL/USD árfolyam")
parser.add_argument("--time-bucket",  type=int,   default=10,   metavar="SEC",
                    help="X-sáv szélessége másodpercben (alapért.: 10)")
parser.add_argument("--mc-level",     type=int,   default=1000, metavar="USD",
                    help="Y-sáv magassága USD marketcapban (alapért.: 1000)")
parser.add_argument("--cell-width",   type=int,   default=50,   metavar="PX",
                    help="Cella pixel-szélessége (alapért.: 75)")
parser.add_argument("--cell-height",  type=int,   default=12,   metavar="PX",
                    help="Cella pixel-magassága (alapért.: 18)")
args = parser.parse_args()

sol_usd          = args.sol_usd
TIME_BUCKET_SEC  = args.time_bucket
MC_LEVEL_SIZE    = args.mc_level
CELL_W           = args.cell_width
CELL_H           = args.cell_height
NUM_TIME_BUCKETS = MAX_DURATION_SEC // TIME_BUCKET_SEC

MAX_MC_FILTER_USD = 100_000   # random módban kizárja a 100k USD fölé menő tokeneket

# --- Tokenek betöltése ---
tokens = pd.read_csv(GOOD_TOKENS_FILE)


def _max_mc_usd(mint: str, migrate_ts_ms: int) -> float:
    """Visszaadja a token maximális marketcap-jét USD-ben a 600s ablakban."""
    try:
        df = pd.read_csv(f"{TRADES_DIR}/{mint}.csv", usecols=["marketCapSol", "timestamp"])
        df = df[(df["timestamp"] >= migrate_ts_ms) &
                (df["timestamp"] <  migrate_ts_ms + MAX_DURATION_SEC * 1000)]
        return pd.to_numeric(df["marketCapSol"], errors="coerce").max() * sol_usd
    except Exception:
        return float("inf")


if args.mint:
    selected = tokens[tokens["mint"] == args.mint]
elif args.random:
    pool   = tokens.sample(frac=1, random_state=None)   # teljes lista keverve
    chosen = []
    for _, row in pool.iterrows():
        if _max_mc_usd(row["mint"], row["timestamp"]) <= MAX_MC_FILTER_USD:
            chosen.append(row)
            if len(chosen) == args.random:
                break
    if not chosen:
        raise SystemExit("Nincs elegendő token a 100k USD szűrő alatt.")
    selected = pd.DataFrame(chosen)
else:
    selected = tokens.iloc[[0]]


# ---------------------------------------------------------------------------
def _cell_color(delta: float, max_abs: float) -> str:
    """Cella háttérszíne delta alapján."""
    if max_abs == 0 or math.isnan(delta):
        return "transparent"
    intensity = min(abs(delta) / max_abs, 1.0)
    alpha = 0.20 + 0.70 * intensity
    if delta > 0:
        return f"rgba(0,180,80,{alpha:.2f})"
    else:
        return f"rgba(220,50,50,{alpha:.2f})"


def build_footprint_html(mint: str, migrate_ts_ms: int,
                         cell_w: int = 75, cell_h: int = 18) -> str:
    """Visszaad egy HTML snippet-et (a teljes <div> blokkot a footprint charttal)."""
    font_sz  = max(7, min(11, cell_h - 7))   # font arányos a magassághoz
    pad_v    = max(0, (cell_h - font_sz) // 2 - 1)

    # --- Trade betöltés (ua. mint visualize_indicators.py:94-105) ---
    trades = pd.read_csv(
        f"{TRADES_DIR}/{mint}.csv",
        usecols=["txType", "solAmount", "marketCapSol", "timestamp"],
    )
    trades = trades[trades["timestamp"] >= migrate_ts_ms].copy()
    end_ts_ms = migrate_ts_ms + MAX_DURATION_SEC * 1000
    trades = trades[trades["timestamp"] < end_ts_ms].copy()

    if trades.empty:
        return f'<div style="color:#888;font-family:monospace;padding:8px;">Nincs adat: {mint}</div>'

    trades["rel_sec"]    = (trades["timestamp"] - migrate_ts_ms) / 1000.0
    trades["mc_usd"]     = pd.to_numeric(trades["marketCapSol"], errors="coerce") * sol_usd
    trades["solAmount"]  = pd.to_numeric(trades["solAmount"],    errors="coerce").abs()
    trades = trades.dropna(subset=["mc_usd", "solAmount"])

    # Bucket assignment
    trades["time_bucket"] = (trades["rel_sec"] // TIME_BUCKET_SEC).astype(int).clip(0, NUM_TIME_BUCKETS - 1)
    trades["mc_level"]    = (trades["mc_usd"] // MC_LEVEL_SIZE).astype(int) * MC_LEVEL_SIZE

    # --- Aggregálás: buy / sell vol per (time_bucket, mc_level) ---
    agg = (
        trades.groupby(["time_bucket", "mc_level", "txType"])["solAmount"]
        .sum()
        .unstack(fill_value=0.0)
    )
    # Biztosítjuk, hogy mindkét oszlop létezik
    for col in ("buy", "sell"):
        if col not in agg.columns:
            agg[col] = 0.0
    agg = agg.reset_index()
    agg["delta"] = agg["buy"] - agg["sell"]

    # --- Per-bucket statisztikák (stat sávokhoz) + OHLC (candle border-hez) ---
    bucket_stats = {}
    ohlc = {}
    for tb in range(NUM_TIME_BUCKETS):
        bt = trades[trades["time_bucket"] == tb]
        vol   = bt["solAmount"].sum()
        buys  = bt[bt["txType"] == "buy"]["solAmount"].sum()
        sells = bt[bt["txType"] == "sell"]["solAmount"].sum()
        count = len(bt)
        bucket_stats[tb] = {"volume": vol, "delta": buys - sells, "trades": count}
        if not bt.empty:
            bt_s = bt.sort_values("timestamp")
            ohlc[tb] = {
                "open":  bt_s["mc_usd"].iloc[0],
                "close": bt_s["mc_usd"].iloc[-1],
                "high":  bt_s["mc_usd"].max(),
                "low":   bt_s["mc_usd"].min(),
            }

    def _candle_shadow(tb: int, level: int) -> str:
        """box-shadow a cella bal oldalán: test=5px, kanóc=2px, kívül=nincs."""
        if tb not in ohlc:
            return ""
        o = ohlc[tb]
        is_bull  = o["close"] >= o["open"]
        color    = "#26a69a" if is_bull else "#ef5350"
        body_lo  = min(o["open"], o["close"])
        body_hi  = max(o["open"], o["close"])
        level_hi = level + MC_LEVEL_SIZE
        if level < body_hi and level_hi > body_lo:          # test
            return f"box-shadow:inset 5px 0 0 {color};"
        elif level < o["high"] and level_hi > o["low"]:    # kanóc
            return f"box-shadow:inset 2px 0 0 {color};"
        return ""

    # Y-tengely: csak azok a szintek, ahol van adat ± 2 szomszédos sávval
    traded_levels = sorted(agg["mc_level"].unique())
    if not traded_levels:
        return f'<div style="color:#888;font-family:monospace;padding:8px;">Nincs trade: {mint}</div>'

    min_level = traded_levels[0]  - 2 * MC_LEVEL_SIZE
    max_level = traded_levels[-1] + 2 * MC_LEVEL_SIZE
    all_levels = list(range(
        int(max_level),
        int(min_level) - MC_LEVEL_SIZE,
        -MC_LEVEL_SIZE,
    ))  # csökkenő sorrendben (legmagasabb felül)

    # Cellák dict-be: (time_bucket, mc_level) → (buy, sell, delta)
    # 0+0 sorok kizárva (ismeretlen txType vagy kerekítési artifact)
    cell = {}
    for _, r in agg.iterrows():
        if r["buy"] + r["sell"] > 0:
            cell[(int(r["time_bucket"]), int(r["mc_level"]))] = (r["buy"], r["sell"], r["delta"])

    max_abs_delta = agg["delta"].abs().max() if not agg.empty else 1.0

    # POC per time_bucket: legnagyobb buy+sell volumenű mc_level
    agg["total_vol"] = agg["buy"] + agg["sell"]
    poc = (
        agg[agg["total_vol"] > 0]
        .loc[lambda df: df.groupby("time_bucket")["total_vol"].transform("max") == df["total_vol"]]
        .groupby("time_bucket")["mc_level"].first()
        .to_dict()
    )  # {time_bucket: mc_level}

    # --- HTML tábla generálás ---
    cell_style_base = (
        f"width:{cell_w}px;min-width:{cell_w}px;max-width:{cell_w}px;"
        f"height:{cell_h}px;font-size:{font_sz}px;padding:{pad_v}px 3px;"
        f"text-align:center;white-space:nowrap;overflow:hidden;"
    )

    # Fejléc: időcímkék
    header_cells = [
        f'<th style="width:52px;min-width:52px;color:#555;font-size:{font_sz}px;'
        f'padding:{pad_v}px 4px;border-right:1px solid #222;">MC\\T</th>'
    ]
    for tb in range(NUM_TIME_BUCKETS):
        t_label = f"{tb * TIME_BUCKET_SEC}s"
        header_cells.append(
            f'<th style="{cell_style_base}color:#666;font-weight:normal;'
            f'border-right:1px solid #1a1a1a;">{t_label}</th>'
        )
    header_row = f'<tr>{"".join(header_cells)}</tr>'

    # Sorok: mc_level csökkenő sorrendben
    rows_html = []
    for level in all_levels:
        level_label = f"${level:,}"
        row_cells = [
            f'<td style="color:#555;font-size:{font_sz}px;padding:{pad_v}px 4px;'
            f'white-space:nowrap;border-right:1px solid #222;'
            f'border-bottom:1px solid #1a1a1a;">{level_label}</td>'
        ]
        for tb in range(NUM_TIME_BUCKETS):
            shadow = _candle_shadow(tb, level)
            key = (tb, level)
            is_poc     = poc.get(tb) == level
            right_border = "border-right:2px solid #ffd700;" if is_poc else "border-right:1px solid #111;"
            if key in cell:
                buy_v, sell_v, delta = cell[key]
                bg = _cell_color(delta, max_abs_delta)

                # Imbalance: átlós összehasonlítás ugyanazon bucket-en belül
                sell_below = cell.get((tb, level - MC_LEVEL_SIZE), (0, 0, 0))[1]
                buy_above  = cell.get((tb, level + MC_LEVEL_SIZE), (0, 0, 0))[0]
                IMBALANCE_RATIO = 2.5
                buy_imb  = buy_v  > 0 and sell_below > 0 and buy_v  / sell_below >= IMBALANCE_RATIO
                sell_imb = sell_v > 0 and buy_above  > 0 and sell_v / buy_above  >= IMBALANCE_RATIO

                buy_style  = "color:#2dd4bf;font-weight:bold;" if buy_imb  else "color:#4ade80;"
                sell_style = "color:#f472b6;font-weight:bold;" if sell_imb else "color:#f87171;"
                content = (
                    f'<span style="{buy_style}">{buy_v:.1f}</span>'
                    f'<span style="color:#aaa;">|</span>'
                    f'<span style="{sell_style}">{sell_v:.1f}</span>'
                )
                row_cells.append(
                    f'<td style="{cell_style_base}background:{bg};'
                    f'{right_border}border-bottom:1px solid #111;{shadow}">'
                    f'{content}</td>'
                )
            else:
                row_cells.append(
                    f'<td style="{cell_style_base}background:#0d0d0d;'
                    f'{right_border}border-bottom:1px solid #111;{shadow}"></td>'
                )
        rows_html.append(f'<tr>{"".join(row_cells)}</tr>')

    # --- Stat footer sorok ---
    max_abs_bucket_delta = max(abs(bucket_stats[tb]["delta"]) for tb in range(NUM_TIME_BUCKETS)) or 1.0
    max_bucket_vol       = max(bucket_stats[tb]["volume"]     for tb in range(NUM_TIME_BUCKETS)) or 1.0

    def _fmt_sol(v: float) -> str:
        """Kompakt SOL formátum: 1 tizedesjegy, K rövidítés ha >= 1000."""
        if v >= 1000:
            return f"{v/1000:.1f}K"
        return f"{v:.1f}"

    stat_rows_def = [
        ("Volume", "volume",  "#1a1a1a", "#888",  False),
        ("Delta",  "delta",   "#0d0d0d", None,    True),
        ("Trades", "trades",  "#111",    "#777",  False),
    ]

    stat_rows_html = []
    # elválasztó sor
    stat_rows_html.append(
        f'<tr><td colspan="{NUM_TIME_BUCKETS + 1}" '
        f'style="height:3px;background:#2a2a2a;padding:0;"></td></tr>'
    )

    for label, key, row_bg, text_col, use_delta_color in stat_rows_def:
        cells = [
            f'<td style="color:#666;font-size:{font_sz}px;padding:{pad_v}px 4px;'
            f'white-space:nowrap;border-right:1px solid #222;'
            f'background:{row_bg};font-weight:bold;">{label}</td>'
        ]
        for tb in range(NUM_TIME_BUCKETS):
            val = bucket_stats[tb][key]
            if key == "trades":
                val_str = str(val) if val > 0 else ""
            else:
                val_str = _fmt_sol(abs(val)) if val != 0 else ""
                if key == "delta" and val < 0:
                    val_str = f"-{val_str}"

            if use_delta_color and val != 0:
                intensity = min(abs(val) / max_abs_bucket_delta, 1.0)
                alpha = 0.25 + 0.65 * intensity
                bg = f"rgba(0,180,80,{alpha:.2f})" if val > 0 else f"rgba(220,50,50,{alpha:.2f})"
                fg = "#fff"
            elif key == "volume" and val > 0:
                intensity = min(val / max_bucket_vol, 1.0)
                alpha = 0.10 + 0.30 * intensity
                bg = f"rgba(100,100,180,{alpha:.2f})"
                fg = "#aaa"
            else:
                bg = row_bg
                fg = text_col or "#777"

            cells.append(
                f'<td style="{cell_style_base}background:{bg};color:{fg};'
                f'border-right:1px solid #111;">{val_str}</td>'
            )
        stat_rows_html.append(f'<tr>{"".join(cells)}</tr>')

    table_html = (
        f'<table style="border-collapse:collapse;background:#0d0d0d;'
        f'font-family:monospace;table-layout:fixed;">'
        f'<thead>{header_row}</thead>'
        f'<tbody>{"".join(rows_html)}</tbody>'
        f'<tfoot>{"".join(stat_rows_html)}</tfoot>'
        f'</table>'
    )

    return (
        f'<div style="overflow-x:auto;padding:8px;">'
        f'{table_html}'
        f'<div style="color:#555;font-size:9px;margin-top:4px;font-family:monospace;">'
        f'Zöld = buy &gt; sell | Piros = sell &gt; buy | Cella: buy_sol | sell_sol | '
        f'Bucket: {TIME_BUCKET_SEC}s × ${MC_LEVEL_SIZE:,} MC | SOL=${sol_usd}'
        f'</div>'
        f'</div>'
    )


# ---------------------------------------------------------------------------
# Chartok összegyűjtése → egyetlen HTML (ua. minta mint visualize_indicators.py:281-311)
html_parts = []
for _, row in selected.iterrows():
    mint          = row["mint"]
    migrate_ts_ms = row["timestamp"]
    print(f"  Generálás: {mint[:20]}…")

    mint_header = (
        f'<div style="font-family:monospace;font-size:13px;color:#ccc;padding:10px 8px 4px;">'
        f'<span style="color:#888;">mint:</span> '
        f'<span id="mint-{mint}" style="cursor:pointer;color:#7ec8ff;" '
        f'onclick="navigator.clipboard.writeText(\'{mint}\').then(()=>{{this.style.color=\'#7fff7e\';'
        f'setTimeout(()=>this.style.color=\'#7ec8ff\',1200)}})" title="Kattints a másoláshoz">'
        f'{mint}</span>'
        f'</div>'
    )
    html_parts.append(mint_header + build_footprint_html(mint, migrate_ts_ms, CELL_W, CELL_H))

full_html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Footprint Chart</title>
  <style>
    body {{ background:#0d0d0d; margin:0; padding:10px; color:#ccc; }}
    hr   {{ border:none; border-top:1px solid #222; margin:16px 0; }}
  </style>
</head>
<body>
{"<hr>".join(html_parts)}
</body>
</html>"""

with tempfile.NamedTemporaryFile(suffix=".html", delete=False, mode="w", encoding="utf-8") as f:
    f.write(full_html)
    tmp_path = f.name

webbrowser.open(f"file://{tmp_path}")
print(f"\n{len(selected)} footprint chart megjelenítve: {tmp_path}")
