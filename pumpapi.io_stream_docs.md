# Data Stream – WebSocket API

Use this endpoint to stream live:

- Solana and tokens transfers
- Pump.fun
- PumpSwap
- Raydium Launchpad (Bonk)
- Raydium-CPMM
- Meteora Launchpad (Bags, moonshot)
- Meteora DAMM V1
- Meteora DAMM V2

Subscribing delivers every event the moment it happens — **transfers, token creations, buys, sells, migrations, pool creations, adding and removing liquidity.**

---

## Endpoint

```
wss://stream.pumpapi.io/
```

**Filter on the client.** The server sends *all* events.  
**One connection only.** Open a single WebSocket per client and reuse it to avoid rate limits.  
**Reconnect logic.** Connections can drop (for example, due to server-side updates or your network issues). You should implement automatic reconnection in your client.

---

## 📦 Code Examples

### Python

```python
import asyncio  
import websockets  
import orjson as json  # or use the standard json module (orjson is faster)  
  
async def pumpapi_data_stream():  
    uri = "wss://stream.pumpapi.io/"  
    async with websockets.connect(uri) as websocket:  
        async for message in websocket:  
            event = json.loads(message)  
            print(event)  # {'txType': 'buy', 'pool': 'pump', ...}  
  
asyncio.run(pumpapi_data_stream())
```


---

## Event Examples

### Create

#### Pump.Fun

```json
{  
  "signature": "58zv6eEs2Y9ARPt9VSdpo6h3A4sg2ijgNftk8vXGvjoHQEiMqgoL6mNnWX9uZ26WS6mtzWuXduf8vuhUwUKJ73Wk",  
  "txType": "create",  
  "poolId": "EzW8aPTiayL6zNw3rpPTDiPsbPFfNcn7TNB8BstbUYh9",  
  "mint": "AvxohnS3SSJRfw4h9u2am5DTRrNv9HY5je7EdqpVSA2i",  
  "txSigner": "3dxmSSoSbLpmyZZTJhGP4w9DUPLCrMyyUNpb6eL8e3Rf",  
  "initialBuy": 97545454.545454,  
  "solAmount": 3.0,  
  "tokensInPool": 695554545.454546,  
  "solInPool": 3.0,  
  "vTokensInBondingCurve": 975454545.454546,  
  "vSolInBondingCurve": 33.0,  
  "price": 3.383038210624416e-8,  
  "marketCapSol": 33.83038210624416,  
  "poolFeeRate": 0.0125,  
  "name": "CHUD",  
  "symbol": "CHUD",  
  "uri": "https://metadata.j7tracker.com/metadata/2456cf930d0a4a0e.json",  
  "supply": 1000000000,  
  "pool": "pump",  
  "creatorFeeAddress": "3dxmSSoSbLpmyZZTJhGP4w9DUPLCrMyyUNpb6eL8e3Rf",  
  "mayhemMode": false,  
  "cashbackEnabled": true,  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token-2022",  
  "tokenExtensions": {  
    "metadataPointer": {},  
    "tokenMetadata": {}  
  },  
  "tradersInvolved": {  
    "3dxmSSoSbLpmyZZTJhGP4w9DUPLCrMyyUNpb6eL8e3Rf": {}  
  },  
  "decimals": 6,  
  "block": 401114006,  
  "timestamp": 1771427621579  
}
```

#### Raydium Launchpad (Bonk)

```json
{  
  "signature": "3LweLX1CG8qV17EmUztAw6isAZdY8sk2ZmHjiGhC6oY6BvdYQousXDivsSPi2xCf99PDdVAgqDBfyiLniTcmHNqR",  
  "txType": "create",  
  "poolId": "FADuSqhV5nQqxCapi2PDvKnNnBBqg8DZEEvVGviELXrk",  
  "mint": "HnXKZ5GRemRnKUP7wBcmrVcRYkFvQNKq8FtLj3gB1ray",  
  "txSigner": "tAg2tgyHmkGTsmq8wBSKsGvUUgoH37cxmCfRUZSXdtB",  
  "initialBuy": 151903987.89698,  
  "solAmount": 5.0,  
  "tokensInPool": 848096012.10302,  
  "solInPool": 4.9475,  
  "vTokensInBondingCurve": 921121617.699402,  
  "vSolInBondingCurve": 34.948352951,  
  "price": 3.7941084303598455e-8,  
  "marketCapSol": 37.94108430359845,  
  "poolFeeRate": 0.0105,  
  "name": "arrest",  
  "symbol": "aarrest",  
  "uri": "https://ipfs.io/ipfs/bafkreih2bzlff4xrkehmezdzirl6ybawtth24niqtjc6qwnordbhydglaq",  
  "supply": 1000000000,  
  "pool": "raydium-launchpad",  
  "platform": "custom",  
  "launchpadConfig": "4Bu96XjU84XjPDSpveTVf6LYGCkfW5FK7SNkREWcEfV4",  
  "migrationThreshholds": {  
    "quote": 85.0  
  },  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "tAg2tgyHmkGTsmq8wBSKsGvUUgoH37cxmCfRUZSXdtB": {}  
  },  
  "decimals": 6,  
  "block": 401380627,  
  "timestamp": 1771532401666  
}
```

#### Meteora Launchpad (Bags, moonshot)

```json
{  
  "signature": "4gDNN8nDdoi84oUW4vb7yKQhsR8kZ5wTiF92REqDiDREGijh7P6VhNeW3QHSozKWA1vCN3GVLjYZfYuetMLjDvtb",  
  "txType": "create",  
  "poolId": "BDLE4vLJ94mp9tEbTNRhf16vaNJ1cWfUrn5ePfx4EWpv",  
  "mint": "CBy1rMkQAHH2Jq8fDsHYTQJBy8S83saHMHM4674TPMuX",  
  "txSigner": "6Ed7RBZrKVAq2V67CpNUGJXp4Avnz25KjVzJCq7LaLYz",  
  "initialBuy": 984498429.538417,  
  "solAmount": 23.0,  
  "tokensInPool": 13034155.851211,  
  "solInPool": 23.0,  
  "price": 1.7741917491987863e-6,  
  "marketCapSol": 1774.1917491987863,  
  "poolFeeRate": 0.0025,  
  "name": "Tesla AI",  
  "symbol": "Tesla AI",  
  "uri": "https://ipfs.io/ipfs/bafkreigcmxnxj2gteuf6oti2orhztqxp4ngtesaayw2xnmbp6h4pxspgba",  
  "supply": 1000000000,  
  "pool": "meteora-launchpad",  
  "lockedLiquidityAfterMigration": "10%",
  "poolFeeRateAfterMigration": 0.001,  
  "migrationThreshholds": {  
    "quote": 30.0  
  },  
  "launchpadConfig": "E6MQpAxta1AQhsDii3trQrGVooqjkwKQ4LgwZ4SCVgo",  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "6Ed7RBZrKVAq2V67CpNUGJXp4Avnz25KjVzJCq7LaLYz": {}  
  },  
  "decimals": 6,  
  "block": 400339537,  
  "timestamp": 1771124275539  
}
```

> ⚠️ Beware of `lockedLiquidityAfterMigration` values below 100%, as they could lead to a rug pull after migration.

---

### Trade (buy / sell)

#### Pump.Fun – buy

```json
{  
  "signature": "91cQMmvA6hrQUuDbAtoKUG8vq3EC8NaNCAh3n4XSoCVoNQqdC9SgtL4zzGdMPXbN9gRivmEk3DLBwzXFzBuyTq7",  
  "txType": "buy",  
  "poolId": "FoZhom3zWdgAG2JPbMyZyhRnhrCYi3s5jXfZtoJG5JQ1",  
  "mint": "J5ThJvvEctb6biaumE9bFi8QyShLKBwSmftsqxdCgmi9",  
  "txSigner": "4N5vGo5R1cWHb5vktSR5VHhPkt7eHYM8JE7vFE9G9uux",  
  "tokenAmount": 42640626.248501,  
  "solAmount": 2.151563012,  
  "tokensInPool": 497785441.584331,  
  "solInPool": 11.392056839,  
  "vTokensInBondingCurve": 777685441.584331,  
  "vSolInBondingCurve": 41.392056839,  
  "price": 5.322467751829646e-8,  
  "marketCapSol": 53.22467751829646,  
  "poolFeeRate": 0.0125,  
  "pool": "pump",  
  "creatorFeeAddress": "bwamJzztZsepfkteWRChggmXuiiCQvpLqPietdNfSXa",  
  "mayhemMode": false,  
  "cashbackEnabled": true,  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token-2022",  
  "tokenExtensions": {  
    "metadataPointer": {},  
    "tokenMetadata": {}  
  },  
  "tradersInvolved": {  
    "4N5vGo5R1cWHb5vktSR5VHhPkt7eHYM8JE7vFE9G9uux": {}  
  },  
  "block": 401114161,  
  "timestamp": 1771427682998  
}
```

#### Pump AMM – buy (pool created by Pump.Fun migration)

```json
{  
  "signature": "63NbM8aanc3y2NjNp18sEFwv65qW4qzYLfQod8gmEGrGhKiBiGBH7fsHZ7MWbXLNP6RGTCznP4fGQu3YboCkdkwD",  
  "txType": "buy",  
  "poolId": "BP7s98rTsd5xTr2CgSVd9Lcpie3KF5yAkmohUgAp1No4",  
  "mint": "E9qgYkgok8aCFXWuvQiYM8krmDbeTuARLgrBjThWpump",  
  "txSigner": "52oc72vjNbpUhF7jNE1pPAvc17JwBTyxybFp3u7PvetG",  
  "tokenAmount": 321548.585603,  
  "solAmount": 0.33830352,  
  "tokensInPool": 135059178.605839,  
  "solInPool": 142.435011367,  
  "price": 1.0546118585741353e-6,  
  "marketCapSol": 1054.6034417168921,  
  "poolFeeRate": 0.012,  
  "pool": "pump-amm",  
  "poolCreatedBy": "pump",
  "burnedLiquidity": "100%",
  "creatorFeeAddress": "HRs5oryur4seP4ei1VUqV3j82HMGuvQrjsEzASHed8Ud",  
  "mayhemMode": false,  
  "cashbackEnabled": false,  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token-2022",  
  "tokenExtensions": {  
    "metadataPointer": {},  
    "tokenMetadata": {}  
  },  
  "tradersInvolved": {  
    "52oc72vjNbpUhF7jNE1pPAvc17JwBTyxybFp3u7PvetG": {}  
  },  
  "block": 388731952,  
  "timestamp": 1766534221298  
}
```

> `poolCreatedBy: "pump"` → pool created through a pump.fun migration. You can trust these pools — you will be able to sell.  
> `burnedLiquidity: "100%"` → no one has the ability to withdraw liquidity and perform a rug pull.

#### Pump AMM – sell (custom pool, SCAM example)

```json
{  
  "signature": "3fYZhMxTRAkxnqfs6P9KShx7AuaxUEKVtCBsP45reqbvrwubc8xk6MCfXBWTVQ3ByPZBgNUnLeC28L5D1WZq9C9q",  
  "txType": "sell",  
  "poolId": "HF9dDDhUu5EjCNTTe2vqvGp8y2SzYHG65RV8Ta1RGSTf",  
  "mint": "941B3sqimoBugHGRDikTaHRwCa5Bv98PEHPK1NFFEmFe",  
  "txSigner": "GJFEs6vbiWF42Sm4ZirZwSzyH5g2NkhetasBfq56rYR8",  
  "tokenAmount": 1182305.746851,  
  "solAmount": 0.590348816,  
  "tokensInPool": 825918325.932008,  
  "solInPool": 411.979377831,  
  "price": 4.988137021491824e-7,  
  "marketCapSol": 498.81347768301646,  
  "poolFeeRate": 0.003,  
  "pool": "pump-amm",  
  "poolCreatedBy": "custom",
  "burnedLiquidity": "0%",
  "creatorFeeAddress": null,  
  "mayhemMode": false,  
  "cashbackEnabled": false,  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "GJFEs6vbiWF42Sm4ZirZwSzyH5g2NkhetasBfq56rYR8": {},  
    "BhVaZzm4Qz7KFUsjWvqYMYWhC34jEMKdQbQK4ws9ycKX": {}  
  },  
  "block": 388691516,  
  "timestamp": 1766518353581  
}
```

> ⚠️ `poolCreatedBy: "custom"` → Be careful with pools on pump-amm where poolCreatedBy is not `"pump"`.  
> ⚠️ `burnedLiquidity: "0%"` → SCAM pool. 0% means it's possible to withdraw all liquidity — you will not be able to sell bought tokens after that.

#### Pump AMM – sell (Token-USDC pool, without SOL)

```json
{  
  "signature": "2gAVP6wcY9xd9L1Gr4F3J2P8h8HS4akXci79Mj9D54vgfgvuZt7U1oX3KjQhHw4JfpvZ9Y1X1sYoAAs6B8xSnBJD",  
  "txType": "sell",  
  "poolId": "2uF4Xh61rDwxnG9woyxsVQP7zuA6kLFpb3NvnRQeoiSd",
  "mint": "pumpCmXqMfrsAkQ5r49WcJnRayYRqmXz6ae8H7H9Dfn",  
  "quoteMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
  "txSigner": "MfDuWeqSHEqTFVYZ7LoexgAK9dxk7cy4DFJWjWMGVWa",  
  "tokenAmount": 1413344.36767,  
  "quoteAmount": 2434.650564,
  "tokensInPool": 3722501951.582035,  
  "quoteInPool": 6411226.583998,
  "price": 0.0017222896501836024,  
  "marketCapQuote": 1722271139.078167,
  "poolFeeRate": 0.003,  
  "pool": "pump-amm",  
  "poolCreatedBy": "custom",  
  "burnedLiquidity": "0%",
  "creatorFeeAddress": null,  
  "mayhemMode": false,  
  "cashbackEnabled": false,  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token-2022",  
  "tokenExtensions": {  
    "transferHook": {},  
    "metadataPointer": {},  
    "tokenMetadata": {}  
  },  
  "tradersInvolved": {  
    "MfDuWeqSHEqTFVYZ7LoexgAK9dxk7cy4DFJWjWMGVWa": {}  
  },  
  "block": 388734360,  
  "timestamp": 1766535166075  
}
```

> Note: Token-USDC pools use `quoteAmount` instead of `solAmount`, `quoteInPool` instead of `solInPool`, and `marketCapQuote` instead of `marketCapSol`. You can open the poolId on solscan.io to verify there's no SOL in the pool. To buy this token, first buy the `quoteMint` (USDC) elsewhere.  
> In this particular case, `burnedLiquidity: "0%"` is not a problem because this poolId is the official PUMP-USDC pool from the pump.fun team.

#### Raydium CPMM – sell (pool created by Raydium Launchpad migration)

```json
{  
  "signature": "2CHuzsiFN94ptUneFuSUCn9miTCTnUX4AWSczCpzAFAa3Mb9RruLPuyTBRYYFXWKPNXSNMqAHJm3zGYuDE6aHcEw",  
  "txType": "sell",  
  "poolId": "4UN6WPJhfB9eoQq4XUwWiDj7NguW4iw9rx4iGBUguXcT",  
  "mint": "6Tph3SxbAW12BSJdCevVV9Zujh97X69d5MJ4XjwKmray",  
  "txSigner": "91WuBL56WNkLeXiFPQ1B1zDrHYNWo3KiC8Gp3FeJVCay",  
  "tokenAmount": 142506.761471,  
  "solAmount": 0.200875025,  
  "tokensInPool": 143086855.207232,  
  "solInPool": 201.996832141,  
  "price": 1.4117078179435069e-6,  
  "marketCapSol": 1411.489916606684,  
  "poolFeeRate": 0.003,  
  "pool": "raydium-cpmm",  
  "poolCreatedBy": "raydium-launchpad",
  "burnedLiquidity": "91%",  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "HU23r7UoZbqTUuh3vA7emAGztFtqwTeVips789vqxxBw": {}  
  },  
  "block": 388738247,  
  "timestamp": 1766536690846  
}
```

> `poolCreatedBy: "raydium-launchpad"` → pool created by raydium-launchpad (usually Bonk), so you can trust it.

#### Raydium CPMM – sell (Token-to-Token pool, without SOL)

```json
{  
  "signature": "3DNxxfNzKEG7VLiKE8E39Ss3y2vtxxVabdgS4S3brj4M7HmeMwE8Qi11EnnyEngFPvi5zqv5GBzGXUAwxCBuDK4t",  
  "txType": "sell",  
  "poolId": "4aqQuRPDZBH29Y2SrpWm94mzVNjikwciorVTitQqJG9f",  
  "mint": "J3NKxxXZcnNiMjKw9hYb2K4LUxgwB6t1FtPtQVsv3KFr",
  "quoteMint": "2GPJhV9jNrj7TaLYMRgWkcy6sTKLcwntv7nZ7qDyMRGM",
  "txSigner": "3nMNd89AxwHUa1AFvQGqohRkxFEQsTsgiEyEyqXFHyyH",  
  "tokenAmount": 44.84029903,  
  "quoteAmount": 165.07403,
  "tokensInPool": 72739.71645621,  
  "quoteInPool": 268287.940938,
  "price": 3.6883281102630074,  
  "marketCapQuote": 378212218.3457152,
  "poolFeeRate": 0.003,  
  "pool": "raydium-cpmm",  
  "poolCreatedBy": "custom",  
  "burnedLiquidity": "0%",  
  "mintAuthority": "BCD75RNBHrJJpW4dXVagL5mPjzRLnVZq4YirJdjEYMV7",  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "3nMNd89AxwHUa1AFvQGqohRkxFEQsTsgiEyEyqXFHyyH": {}  
  },  
  "block": 388739013,  
  "timestamp": 1766536990765  
}
```

> The `quoteMint` here is another memecoin (not SOL/stablecoin). To buy this token, first buy the `quoteMint` elsewhere.

#### Raydium Launchpad (Bonk) – buy (USD1 pool)

```json
{  
  "signature": "5kLZfmUnb7mDnXyNZXSVGWcUdj8BFkyLauycWMYpM6j2GPg9VFjgRnyGdqU1yij8wWahseVj5AwXeyBTw8m2oDpj",  
  "txType": "buy",  
  "poolId": "BnHRVmtz66soqmGifK7725TXzxUN2oBEhVDs2LjkhYN6",  
  "mint": "rz9G7vCQBxPNrejMv4iVa3UyuxJasBAjjsmDnhnbonk",  
  "quoteMint": "USD1ttGY1N17NEEHLmELoaybftRBUSErhqYiQzvEmuB",
  "txSigner": "HKHMrsfW9rDc1KrT1gU4AmC5A2hvVqwRMujN5eegMLX8",  
  "tokenAmount": 0.227592,  
  "quoteAmount": 0.000012,  
  "tokensInPool": 239942135.99963,  
  "quoteInPool": 10714.496586,  
  "vTokensInBondingCurve": 312967741.595121,  
  "vSolInBondingCurve": 15126.386725,  
  "price": 0.00004833209533961698,  
  "marketCapQuote": 48332.095339616986,  
  "poolFeeRate": 0.013,  
  "pool": "raydium-launchpad",  
  "platform": "bonk",
  "launchpadConfig": "FfYek5vEz23cMkWsdJwG2oa6EphsvXSHrGpdALN4g6W1",  
  "migrationThreshholds": {  
    "quote": 12500.0  
  },  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "HKHMrsfW9rDc1KrT1gU4AmC5A2hvVqwRMujN5eegMLX8": {}  
  },  
  "block": 388764798,  
  "timestamp": 1766547117907  
}
```

> `platform` can be `"bonk"`, `"raydium-launchlab"`, or `"custom"`. Anyone can create a platform on the Raydium launchpad — Bonk is just one of them.

#### Meteora Launchpad – buy

```json
{  
  "signature": "5RKRyZ5E4EjezdhkpnvtPXJoR2hLpHispSrAEWebCAEjheni3D6UrciBWN3becVaaEnZBS69XcdnvvLDRENzUEJv",  
  "txType": "buy",  
  "poolId": "3DrHmGXh9LVFFxz5yGmgm8jagHijqhXvSQyjhus1etPa",  
  "mint": "3DsdCFH1RGfaV1CUSJzbmYQ7vFSsVuEFK1tHRVAiBAGS",  
  "txSigner": "13NZSDSMRvP75Y97UnDxD12LCTDtaXsmbyABSqyz8yDP",  
  "tokenAmount": 2921696.077137405,  
  "solAmount": 0.26,  
  "tokensInPool": 469002275.1985069,  
  "solInPool": 26.757985773,  
  "price": 8.756358166765358e-8,  
  "marketCapSol": 87.56358166765358,  
  "poolFeeRate": 0.02,  
  "pool": "meteora-launchpad",  
  "lockedLiquidityAfterMigration": "100%",
  "poolFeeRateAfterMigration": 0.02,
  "migrationThreshholds": {  
    "quote": 85.0  
  },  
  "launchpadConfig": "A1z7xx4Vr24q2P6Hy7ee4Xo7RtQraM93M9FdTobmL3G9",  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "13NZSDSMRvP75Y97UnDxD12LCTDtaXsmbyABSqyz8yDP": {}  
  },  
  "block": 400331273,  
  "timestamp": 1771121062458  
}
```

> ⚠️ Check `poolFeeRateAfterMigration`: if it's `0.1` (the maximum future fee allowed), you will lose 10% on each trade.

#### Meteora DAMM V1 – buy

```json
{  
  "signature": "4XRntfX8s4ryHi9XckbvPSFHeuhZ5AinoieybTRFuW39XW8ue9jheT4hDMj7eZnPt1Wc6XXkUHJNKt3H6VRCErXU",  
  "txType": "buy",  
  "poolId": "ERgpKaq59Nnfm9YRVAAhnq16cZhHxGcDoDWCzXbhiaNw",  
  "mint": "J1toso1uCk3RLmjorhTtrVwY9HJ7X8V9yYac6Y7kGCPn",  
  "txSigner": "BCdcmLAuYx2RCGGCZhWuP9fgiZje2pBRrjLHr1qH4nZL",  
  "tokenAmount": 0.111010032,  
  "solAmount": 0.13997,  
  "tokensInPool": 13603.81205579,  
  "solInPool": 9693.056530216,  
  "price": 1.2611303844898412,  
  "marketCapSol": 13431882.291044032,  
  "poolFeeRate": 0.0001,  
  "pool": "meteora-damm-v1",  
  "poolCreatedBy": "custom",  
  "burnedLiquidity": "0%",  
  "curveType": "StableSwap",  
  "mintAuthority": "6iQKfEyhr3bZMotVkW6beNZz5CPAkiwvgV2CTje9pVSS",  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "BCdcmLAuYx2RCGGCZhWuP9fgiZje2pBRrjLHr1qH4nZL": {}  
  },  
  "block": 400345180,  
  "timestamp": 1771126482369  
}
```

#### Meteora DAMM V2 – buy

```json
{  
  "signature": "4XMDoJJt5HK97oWcqyjSKVw8pJY8McSy6KnEFiutuxWwkiqmmWwrrN2AtCBED77cz35gkitB6JatGD4cZzLFTXk5",  
  "txType": "buy",  
  "poolId": "Fy62YfCBu2z4hmLk3m68XrtBBLHtZXY1Si5rtVsrsRvs",  
  "mint": "E9vNSVzuwWcmsFkbSVWXAhbPwETJv4aM8Lvs5ympump",  
  "txSigner": "7zZ2vRvqyP5Ey9qy4s2593DTg8J4sNYWrmcNnmDE4F9B",  
  "tokenAmount": 105775.084401,  
  "solAmount": 0.610509458,  
  "tokensInPool": 2944583.780026,  
  "solInPool": 17.588974243,  
  "price": 5.973331244963443e-6,  
  "marketCapSol": 5973.331244963442,  
  "poolFeeRate": 0.001,  
  "pool": "meteora-damm-v2",  
  "poolCreatedBy": "meteora-launchpad",  
  "burnedLiquidity": "10%",  
  "minPrice": 5.421214630269583e-23,  
  "maxPrice": 1.844605071373595e16,  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "7zZ2vRvqyP5Ey9qy4s2593DTg8J4sNYWrmcNnmDE4F9B": {}  
  },  
  "block": 400350764,  
  "timestamp": 1771128655157  
}
```

---

### Migration

#### Pump AMM

```json
{  
  "signature": "4nownD6mfEWqPobc7TrfYk6VyTiqdyzkXqgSbJb2hNVxsXoNfAQADJBRP3JzuYX921NTyY9TLNVZnREdcbo3D4NP",  
  "txType": "migrate",  
  "poolId": "8xLk84gnavkayCu4o345bgC7Qk4oRNtU2AS1PaTqujwH",  
  "mint": "3x2vP4L8D63AHh7DhLR2XuRuMT7CsMqDHwVKTdFepump",  
  "txSigner": "EbpZp7vbpGXH4J22dJQAnLVoqTH688rQeJuaPWvF2sbz",  
  "initialBuy": 0.0,  
  "solAmount": 0.0,  
  "tokensInPool": 206900000.0,  
  "solInPool": 84.99036005,  
  "price": 4.1077989391010155e-7,  
  "marketCapSol": 410.7798906238624,  
  "poolFeeRate": 0.0125,  
  "supply": 999999992,  
  "pool": "pump-amm",  
  "poolCreatedBy": "pump",  
  "burnedLiquidity": "100%",  
  "creatorFeeAddress": "5cyRTqMkuDJeVC8Q1Bk1DnwAKFMEDX1ANG7ZbyA362F",  
  "mayhemMode": false,  
  "cashbackEnabled": false,  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token-2022",  
  "tokenExtensions": {  
    "metadataPointer": {},  
    "tokenMetadata": {}  
  },  
  "tradersInvolved": {  
    "2pUhfahHvTXKmSKXEzHd77DJnRYH7cExRjfzGQaNqGyN": {}  
  },  
  "block": 388775295,  
  "timestamp": 1766551228263  
}
```

#### Meteora DAMM V1

```json
{  
  "signature": "AgmvLnh4DR52FmPvGmPYLwmSihhU59iMe9F9TNXSsPLgV9JokAjzxrjAmQBPvXiv88noYD5ieWQzWtLefoafmEZ",  
  "txType": "migrate",  
  "poolId": "5DuwQd3MAiCcugJG24tq3TJ5MHCuWpZJywbkgMTYao6h",  
  "mint": "DHuyFyr5vwMa9hC71i1nqg7kZ4PfxBG5FEm7TqrsxgUb",  
  "txSigner": "CQdrEsYAxRqkwmpycuTwnMKggr3cr9fqY8Qma4J9TudY",  
  "initialBuy": 0.0,  
  "solAmount": 0.0,  
  "tokensInPool": 23989059.724993,  
  "solInPool": 11.976219064,  
  "price": 4.992367021172813e-7,  
  "marketCapSol": 499.2367021172813,  
  "poolFeeRate": 0.0025,  
  "supply": 1000000000,  
  "pool": "meteora-damm-v1",  
  "poolCreatedBy": "meteora-launchpad",  
  "burnedLiquidity": "0%",  
  "curveType": "ConstantProduct",  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM": {}  
  },  
  "block": 400336821,  
  "timestamp": 1771123217240  
}
```

#### Meteora DAMM V2

```json
{  
  "signature": "4pqYzmMniFutZgzeKzVYcQxAQab872RLG5mGeTcAEBzZ9uLmELTpEXsrt3hsrHvSB8jYnW9HGRWxAYPZsypmdyBY",  
  "txType": "migrate",  
  "poolId": "GCv2qtGK2Qzi7df9dU6urKzo9WcsrU3fDjwkpddPYn7x",  
  "mint": "CBy1rMkQAHH2Jq8fDsHYTQJBy8S83saHMHM4674TPMuX",  
  "txSigner": "CQdrEsYAxRqkwmpycuTwnMKggr3cr9fqY8Qma4J9TudY",  
  "initialBuy": 0.0,  
  "solAmount": 0.0,  
  "tokensInPool": 9980000.042297,  
  "solInPool": 29.939999999,  
  "price": 3e-6,  
  "marketCapSol": 3000.0,  
  "poolFeeRate": 0.001,  
  "supply": 1000000000,  
  "pool": "meteora-damm-v2",  
  "poolCreatedBy": "meteora-launchpad",  
  "burnedLiquidity": "10%",  
  "minPrice": 5.421214630269583e-23,  
  "maxPrice": 1.844605071373595e16,  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "FhVo3mqL8PW5pH5U2CN4XE33DokiyZnUwuGpH2hmHLuM": {}  
  },  
  "block": 400343572,  
  "timestamp": 1771125858449  
}
```

---

### Create Pool

#### Pump AMM

```json
{  
  "signature": "3BiAqMmm2dX4GjLdajKQnSTMLTC3oQzRVVTEKvKeFu7jSAcE3kFVq7u3BpoSasx77U2rBTArRgqossfiGaTP1iDh",  
  "txType": "createPool",  
  "poolId": "8yEwjGT16re94WAahxrvMg79smn5B8rzZgPTNWFzkW3K",  
  "mint": "DGvxoH8zEmatVbMMydMFDhsiofdgK2cFn6dPccNJ6hEg",  
  "txSigner": "JBHqRGJ9rVGzHg3DqzbFkh235kjvEiEMhBMQsU4fiAon",  
  "initialBuy": 0.0,
  "solAmount": 0.0,  
  "tokensInPool": 1000000000.0,  
  "solInPool": 200.0,  
  "price": 2e-7,  
  "marketCapSol": 200.0000002,  
  "poolFeeRate": 0.003,  
  "supply": 1000000001,  
  "pool": "pump-amm",  
  "poolCreatedBy": "custom",
  "burnedLiquidity": "0%",
  "creatorFeeAddress": null,  
  "mayhemMode": false,  
  "cashbackEnabled": false,  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "JBHqRGJ9rVGzHg3DqzbFkh235kjvEiEMhBMQsU4fiAon": {}  
  },  
  "block": 388775128,  
  "timestamp": 1766551163729  
}
```

> ⚠️ `poolCreatedBy` will always be `"custom"` in `createPool` events. If it's `"pump"` or `"raydium-launchpad"`, it's a `migrate` event instead.  
> ⚠️ `burnedLiquidity: "0%"` is a typical scam pattern. They create a pool with a lot of liquidity but can remove it later.

#### Raydium CPMM

```json
{  
  "signature": "4j6NuFZSfXehhVVe9fw9dqwohWXUqcHVv53uGq5ypyQoh6ZhJFVworjC7EVNCJugvyayNP241ibadi4hjYbALFVi",  
  "txType": "createPool",  
  "poolId": "JBAdtP9nYk95z44KRrb8gHffUUr4HVKkuXDKReZ5HyXg",  
  "mint": "67BmAvfRHoxGPxbSMArCgmsLHfZnHFEhs7tiQSiXstY",  
  "txSigner": "B2pbyEKzER21sJuKzTsAN6Ve2u6iaQ4fyS56Gf3zfRDL",  
  "initialBuy": 0.0,  
  "solAmount": 0.0,  
  "tokensInPool": 90000000.0,  
  "solInPool": 0.5,  
  "price": 5.555555555555556e-9,  
  "marketCapSol": 5.555555555555556,  
  "poolFeeRate": 0.003,  
  "supply": 1000000000,  
  "pool": "raydium-cpmm",  
  "poolCreatedBy": "custom",  
  "burnedLiquidity": "0%",  
  "mintAuthority": "B2pbyEKzER21sJuKzTsAN6Ve2u6iaQ4fyS56Gf3zfRDL",  
  "freezeAuthority": "B2pbyEKzER21sJuKzTsAN6Ve2u6iaQ4fyS56Gf3zfRDL",  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "B2pbyEKzER21sJuKzTsAN6Ve2u6iaQ4fyS56Gf3zfRDL": {}  
  },  
  "block": 388778410,  
  "timestamp": 1766552453146  
}
```

#### Meteora DAMM V2

```json
{  
  "signature": "1Xg2MAQ45srS1jEsimDe56cKxp6YhC2gKPq25zMgz9r11inJH8LFi7unX7443TXaGKV1FLsZvEVLyLyRN1DzsPN",  
  "txType": "createPool",  
  "poolId": "GBbDy9g2TrqS1n39D2CbfNmaUdMtzAahbpxvDirfmznH",  
  "mint": "GuMGpj1ATXZHfBQzdPiQCu464icCGt9b2FX9YqrqBAGS",  
  "txSigner": "5tnydcUMvUuc3a9UqmUHdyiiHN6u6EQynsK5M76zVfHo",  
  "initialBuy": 0.0,  
  "solAmount": 0.0,  
  "tokensInPool": 96888.172006218,  
  "solInPool": 0.54154636,  
  "price": 5.589396549855622e-6,  
  "marketCapSol": 5589.396393352518,  
  "poolFeeRate": 0.5,
  "supply": 999999972,  
  "pool": "meteora-damm-v2",  
  "poolCreatedBy": "custom",  
  "burnedLiquidity": "0%",  
  "minPrice": 5.421214630269582e-20,  
  "maxPrice": 1.844605071373595e19,  
  "mintAuthority": null,  
  "freezeAuthority": null,  
  "tokenProgram": "spl-token",  
  "tokenExtensions": {},  
  "tradersInvolved": {  
    "5tnydcUMvUuc3a9UqmUHdyiiHN6u6EQynsK5M76zVfHo": {}  
  },  
  "block": 400339554,  
  "timestamp": 1771124281945  
}
```

> ⚠️ `poolFeeRate: 0.5` = 50% fee per trade — that's a scam. The fee can change over time.


---

## Glossary

| Field | Description |
|---|---|
| `signature` | Transaction signature on the Solana blockchain. |
| `txType` | Transaction type — one of `transfer`, `create`, `buy`, `sell`, `migrate`, `createPool`, `add`, `remove`. |
| `poolId` | Unique pool address. You can view pool reserves by looking it up on-chain. **Tip 1:** Check if `poolId` equals `Gf7sXMoP8iRw4iiXmJ1nq4vxcRycbGXy5RL8a8LnTd3v` — this is the largest SOL–USDC pool on pump-amm, so you can read the Solana price from it without any external API. **Tip 2:** Pass this address to the trade API using `'poolId': 'address'` to trade a token from a specific pool. This is useful for arbitrage. If omitted, the API automatically chooses the best pool. |
| `mint` | Token mint address. |
| `quoteMint` | The second token used in the trade. Only sent if the quote token is **NOT** Solana. By default quoteMint is Solana, so it is omitted. Example: some pools only accept USDC, USDT, or another token. |
| `txSigner` | The public key of the account that sent the transaction and paid the priorityFee. **Important:** For copy trading, use `tradersInvolved`, not `txSigner`. Sometimes a transaction is signed by one account while funds come from another — the real trader will be in `tradersInvolved`. |
| `tokenAmount` | Amount of `mint` tokens involved in the transaction. |
| `solAmount` | Amount of SOL involved. Only returned when the quote token is Solana. Otherwise `quoteAmount` is returned. |
| `quoteAmount` | Amount of the `quoteMint` token involved. Only returned when the quote token is not Solana. |
| `tokensInPool` | Total amount of the main token (`mint`) currently in the liquidity pool. |
| `solInPool` | Total SOL currently locked in the pool. Present only when SOL is the quote token. |
| `quoteInPool` | Total amount of the quote token locked in the pool. Present only when the quote token is not SOL (e.g. USDC, USDT). |
| `vTokensInBondingCurve` | Virtual token reserves in the bonding curve pool. Present only when `pool` is `pump` or `raydium-launchpad`. |
| `vSolInBondingCurve` | Virtual SOL reserves in the bonding curve pool. Present only when `pool` is `pump` or `raydium-launchpad` and the quote token is SOL. |
| `vQuoteInBondingCurve` | Virtual Quote reserves in the bonding curve pool. Present only when `pool` is `pump` or `raydium-launchpad` and the quote token is NOT SOL (e.g. USDC/USDT). |
| `price` | Price in quoteMint (usually SOL) including this transaction's impact. |
| `marketCapSol` | Market capitalization in SOL. Only sent when quote mint is SOL. |
| `marketCapQuote` | Market capitalization in the quote token. Only sent when quote mint is NOT SOL (e.g. USDC, USDT). |
| `pool` | Liquidity source. Before migration: `pump` or `raydium-launchpad`. After migration: `pump` → `pump-amm`, `raydium-launchpad` → `raydium-cpmm`, `meteora-launchpad` → `meteora-damm-v1` / `meteora-damm-v2`. |
| `minPrice` | Available only in Meteora DAMM V2. Minimum price configured for the pool. |
| `maxPrice` | Available only in Meteora DAMM V2. Maximum price configured for the pool. |
| `curveType` | Present only in Meteora DAMM V1. Price formula used: `ConstantProduct` (most common, based on quote/base reserve ratio) or `StableSwap` (for stablecoin pairs, keeps price near 1:1). |
| `poolFeeRate` | Current fee rate in the pool. Range: 0 to 1 (e.g. `0.1` = 10%, `0.001` = 0.1%). |
| `poolCreatedBy` | Who created the pool on pump-amm, raydium-cpmm, meteora-damm-v1, or meteora-damm-v2. If via migration: `pump`, `raydium-launchpad`, or `meteora-launchpad`. If manually created: `custom`. Pools migrated from pump and raydium-launchpad are considered trusted. Pools migrated from meteora-launchpad can be risky — always check `lockedLiquidityAfterMigration`. |
| `lockedLiquidityAfterMigration` | Present only in Meteora Launchpad. Percentage of liquidity that will be locked after migration. Values below 100% risk a rug pull by the pool or launchpad creator. |
| `poolFeeRateAfterMigration` | Present only in Meteora Launchpad. Fee rate after migration. Meteora allows up to `0.1` (10%). |
| `migrationThreshholds` | Present only in Meteora Launchpad and Raydium Launchpad. Required `solInPool` or `quoteInPool` value to trigger migration. Pump.fun always uses a fixed 85 SOL. |
| `burnedLiquidity` | Percentage of liquidity that is burned (e.g. `"99%"`). Burned liquidity cannot be withdrawn — the pool is always available for trading. `0%` means the owner can drain the entire pool (rug pull). Higher burned liquidity = lower rug pull risk. Pump.fun and (partly) raydium-launchpad burn liquidity rights after migration. |
| `cashbackEnabled` | Whether you are accumulating cashback for trading in this pool. Exists on pump.fun and pumpswap pools. Claim accumulated cashback via the `claimCashback` endpoint. |
| `creatorFeeAddress` | Address receiving creator fees on pump.fun and pumpSwap (when `cashbackEnabled` is `false`). Can change — the real token creator can modify it. May be `null` if creator fees are not enabled. |
| `mayhemMode` | Whether "mayhem mode" is active for `pump` or `pump-amm` pools. `true` = on, `false` = off. Not present on other pool types. |
| `launchpadConfig` | Address where Meteora or Raydium launchpad settings are stored. Anyone can create their own config on these launchpads. |
| `mintAuthority` | Address with permission to mint new tokens. **Must always be `null`** — any other value is a red flag for a potential scam. Only stablecoins legitimately have a non-null value. |
| `freezeAuthority` | Address that can freeze token accounts. **Must always be `null`** — non-null may indicate a honeypot or scam. Stablecoins may have this set for regulatory reasons. |
| `tokenProgram` | Token program used to create the token: `spl-token` (legacy) or `spl-token-2022` (newer standard). |
| `tokenExtensions` | Token extensions — only present in `spl-token-2022` tokens. Some extensions can be used by scammers. This does **not** apply to tokens from pump.fun, Bonk, or other trusted launchpads. |
| `tradersInvolved` | Addresses that **actually executed the trade** (spent funds). Critical for copy trading and analytics. A transaction may be signed by one address (`txSigner`) while funds come from another. Always track by `tradersInvolved`, not `txSigner`. |
| `type` | Present only in transfer events. Shows which method was used (e.g. `token_account_closure`, `withdraw_from_nonce`). |
| `isSolana` | Present only in transfer events. `true` if the mint is native SOL or WSOL (Wrapped SOL); otherwise `false`. |
| `block` | Block number in which the transaction was included. New blocks are produced every ~400 ms. |
| `timestamp` | Blockchain timestamp of the transaction (milliseconds). |

---

*Source: [https://pumpapi.io/stream](https://pumpapi.io/stream)*
