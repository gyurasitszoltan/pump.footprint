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