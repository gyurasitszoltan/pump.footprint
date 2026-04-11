# Pump.fun Footprint Chart - Rendszerterv

## Context

A footprint.example.py offline HTML-generátorának online, real-time változata. A backend WebSocketen fogadja a pumpapi adatokat, aggregálja, és Vue 3 frontendre tolja. Migrate event aktiválja a tokent, 10 percig trackeljük.

---

## Projekt struktúra

```
pump.footprint/
├── server.py                    # Belépési pont: minden szolgáltatás indítása
├── backend/
│   ├── __init__.py
│   ├── const.py                 # Konstansok (SOL_USD=85, MAX_DURATION=600, stb.)
│   ├── feeder.py                # WS kliens → ws://192.168.1.122:9944
│   ├── token_manager.py         # Aktív tokenek lifecycle (10 perc TTL)
│   ├── aggregator.py            # Per-token 1s/10s bucket aggregáció + RSI
│   ├── footprint.py             # Adat struktúrák (cell, OHLC, stats, snapshot)
│   ├── ws_server.py             # WS szerver a frontend felé
│   └── http_server.py           # aiohttp: static files + WS route
├── frontend/
│   ├── package.json
│   ├── vite.config.js           # proxy: /ws → backend
│   ├── tailwind.config.js
│   ├── index.html
│   └── src/
│       ├── main.js
│       ├── App.vue
│       ├── composables/
│       │   ├── useWebSocket.js      # WS kapcsolat + reconnect
│       │   └── useTokenStore.js     # Reaktív state: tokenek + chart
│       ├── components/
│       │   ├── TokenList.vue        # Aktív tokenek listája
│       │   ├── TokenRow.vue         # Egy token sor
│       │   ├── FootprintChart.vue   # Chart konténer
│       │   ├── FootprintGrid.vue    # HTML tábla (cellák)
│       │   ├── FootprintCell.vue    # buy|sell cella
│       │   └── StatsBar.vue         # Volume/Delta/Trades footer
│       └── utils/
│           ├── format.js            # SOL formázás, compact számok
│           └── colors.js            # Cella szín, delta szín, RSI szín
├── requirements.txt                 # websockets, orjson, aiohttp
└── .gitignore
```

---

## Backend modulok

### `const.py`
- `SOL_USD = 85.0`
- `MAX_DURATION_SEC = 600`, `TIME_BUCKET_10S = 10`, `NUM_BUCKETS_10S = 60`
- `MC_LEVEL_SIZE = 1000` (1K USD klaszterek)
- `INITIAL_MC_LOW = 20000`, `INITIAL_MC_HIGH = 50000`
- `IMBALANCE_RATIO = 2.5`, `RSI_PERIOD = 14`
- `FEEDER_URI = "ws://192.168.1.122:9944"`

### `feeder.py` - WebSocket kliens
- Csatlakozás a lokális feederhez, orjson parse
- Szűrés: `txType` == "migrate" / "buy" / "sell"
- Migrate: csak `pool == "pump-amm"` és `poolCreatedBy == "pump"` → `token_manager.activate_token()`
- Buy/sell: ha a `mint` aktív → `token_manager.process_trade()`
- Trade-hez szükséges mezők: `txType`, `mint`, `solAmount`, `marketCapSol`, `timestamp`
- Automatikus reconnect exponenciális backoff-fal
- Guard: ha nincs `marketCapSol` vagy `solAmount` a trade-ben → skip

### `token_manager.py` - TokenManager
- `active_tokens: dict[str, TokenState]`
- `activate_token(event)`: TokenState létrehozás, `asyncio.call_later(600, remove)` cleanup
- `process_trade(event)`: továbbítás az aggregátornak
- `remove_token(mint)`: törlés + frontend értesítés
- `get_token_summaries()`: lista a token list-hez
- `get_footprint_data(mint)`: teljes snapshot

### `aggregator.py` - Per-token aggregátor (a legkomplexebb modul)

**1 másodperces bucketek (600 db):**
- Csak `close_mc_usd` tárolás → RSI14 számoláshoz
- Ha nincs trade egy sec-ben, az a sec kimarad az RSI-ből

**10 másodperces bucketek (60 db):**
- `cells: dict[(bucket_idx, mc_level)] → {buy_vol, sell_vol}`
- OHLC per bucket: open, high, low, close (mc_usd)
- Trade count per bucket

**Számítások (footprint.example.py alapján):**
- **POC**: per bucket a legnagyobb (buy+sell) volumenű mc_level (sor 194-201)
- **Imbalance** (sor 241-246): diagonális összehasonlítás, ratio >= 2.5
  - buy_imb: `buy_vol[L] / sell_vol[L - 1000] >= 2.5`
  - sell_imb: `sell_vol[L] / buy_vol[L + 1000] >= 2.5`
- **RSI14**: Wilder-féle RSI az 1s close_mc értékekből
- **Delta**: `buy_vol - sell_vol` per cella és per bucket
- Y tengely dinamikus bővítés ha mc kilép a 20K-50K tartományból

### `ws_server.py` - Frontend WS szerver
- Kliensek kezelése, per-kliens token subscription
- Token lista broadcast MINDEN kliensnek
- Footprint update csak a feliratkozott klienseknek
- Token summary broadcast ~2 mp-enként

### `http_server.py` + `server.py`
- `aiohttp.web.Application`: static fájlok (`frontend/dist/`) + `/ws` route
- Egyetlen asyncio event loop: HTTP szerver + WS szerver + feeder kliens
- Egy port (8080), egy process, nincs szükség nginx-re

---

## Frontend komponensek

### `useWebSocket.js`
- WS kapcsolat: `/ws` (production-ben relatív, dev-ben proxy)
- Auto-reconnect, backoff
- Bejövő üzenetek dispatch → `useTokenStore`

### `useTokenStore.js`
- `tokens: Map<string, TokenSummary>` - aktiválás sorrendjében
- `selectedMint: ref(null)`
- `footprint: reactive(null)` - kiválasztott token chart adatai
- Snapshot és incremental update merge

### `TokenList.vue` + `TokenRow.vue`
- Mint address: kattintható link → `https://gmgn.ai/sol/token/{mint}` (új lap)
- Copy ikon → clipboard
- Aktív idő (sec): `setInterval(1s)` lokálisan, szerver sync 2mp-enként. >= 540s (9. perc) → piros háttér
- Trades per 10sec
- Marketcap USD
- RSI14: szín kódolva (0-30 piros, 30-70 zöld, 70-100 piros)
- Kiválasztott token: más háttérszín

### `FootprintGrid.vue` - HTML tábla
- **Döntés: HTML tábla (nem canvas)** - a footprint.example.py stílusa közvetlenül CSS-re fordítható (box-shadow, rgba, border). 60x~30 = ~1800 cella, DOM teljesítmény rendben van.
- Fejléc: időcímkék ("0s", "10s", ... "590s")
- Sorok: mc_level csökkenő sorrendben ("$20,000", "$21,000"...)
- Gyertya border: `box-shadow: inset 5px 0 0 color` (test), `2px` (kanóc). Zöld #26a69a bull, piros #ef5350 bear.
- POC: `border-right: 2px solid #ffd700`
- Auto-scroll jobbra (legújabb bucket)

### `FootprintCell.vue`
- `buy_vol | sell_vol` formátum
- Buy: #4ade80, imbalance esetén bold #2dd4bf
- Sell: #f87171, imbalance esetén bold #f472b6
- Háttér: `_cell_color()` logika (zöld/piros rgba, intenzitás a delta alapján)

### `StatsBar.vue`
- Elválasztó: 3px #2a2a2a
- Volume: kékes háttér, intenzitás a volumen alapján
- Delta: zöld/piros, intenzitás a delta alapján
- Trades: sima szám

### Design
- Sötét téma: #0d0d0d háttér, monospace font
- Tailwind CSS utility-k + inline stílusok a dinamikus színekhez

---

## WebSocket protokoll (Backend ↔ Frontend)

### Kliens → Szerver
```json
{ "type": "select_token", "mint": "..." }
{ "type": "unselect_token" }
```

### Szerver → Kliens

**token_list** (csatlakozáskor + változáskor):
```json
{ "type": "token_list", "tokens": [{ "mint", "name", "symbol", "migrate_ts_ms", "mc_usd", "trades_10s", "rsi14" }] }
```

**token_added / token_removed**:
```json
{ "type": "token_added", "token": { ... } }
{ "type": "token_removed", "mint": "..." }
```

**token_summary_update** (~2mp-enként, minden aktív tokenre):
```json
{ "type": "token_summary_update", "mint": "...", "mc_usd": ..., "trades_10s": ..., "rsi14": ... }
```

**footprint_snapshot** (token kiválasztásakor):
```json
{ "type": "footprint_snapshot", "mint", "mc_levels": [desc], "cells": {"bucket:level": {buy,sell,delta,buy_imb,sell_imb}}, "ohlc": {...}, "stats": {...}, "poc": {...}, "rsi14", "current_bucket", "max_abs_delta" }
```

**footprint_update** (minden trade-nél, feliratkozott kliensnek):
```json
{ "type": "footprint_update", "bucket", "mc_level", "cell", "ohlc", "stats", "poc", "mc_levels_expanded": null|[...], "max_abs_delta", "imbalance_updates": [...] }
```

---

## Adat folyam

```
ws://192.168.1.122:9944  →  feeder.py (szűr)  →  token_manager.py (lifecycle)
    →  aggregator.py (1s/10s bucket, OHLC, POC, imbalance, RSI)
    →  ws_server.py (push klienseknek)  →  Vue 3 Frontend
```

Production HTTP: `aiohttp` → `frontend/dist/` static fájlok + `/ws` WebSocket

---

## Megvalósítási sorrend

### Fázis 1 - Backend core
1. `const.py`
2. `aggregator.py` + `footprint.py` (tesztelhető szintetikus adattal)
3. `token_manager.py`
4. `feeder.py` (WS kliens a feederhez)

### Fázis 2 - Backend szerver
5. `ws_server.py`
6. `http_server.py`
7. `server.py` (összekötés)

### Fázis 3 - Frontend scaffolding
8. Vue 3 + Vite + Tailwind projekt (`frontend/`)
9. `useWebSocket.js` + `useTokenStore.js`
10. `App.vue` alap layout

### Fázis 4 - Token lista
11. `TokenRow.vue` + `TokenList.vue`
12. Token kiválasztás + highlight

### Fázis 5 - Footprint chart
13. `FootprintGrid.vue` + `FootprintCell.vue`
14. Gyertya borderek + POC + imbalance
15. `StatsBar.vue`

### Fázis 6 - Integráció és finomítás
16. Live update (incremental merge)
17. Y-tengely dinamikus bővítés
18. Auto-scroll, production build, hibakezelés

---

## Verifikáció

1. **Backend unit**: Szintetikus trade-eket küldeni az aggregátornak, ellenőrizni cellák/OHLC/POC/imbalance/RSI értékeket
2. **Feeder teszt**: Csatlakozás a ws://192.168.1.122:9944-hez, migrate eventek logolása
3. **WS protokoll**: `websocat` vagy Python WS klienssel ellenőrizni a szerver üzeneteket
4. **Frontend dev**: `vite dev` + proxy → backend, élő adatokkal tesztelni
5. **Production**: `vite build` → Python `server.py` kiszolgálja → böngészőben ellenőrizni
6. **End-to-end**: Migrate event → token megjelenik listában → kiválasztás → footprint chart épül → 10 perc után eltűnik
