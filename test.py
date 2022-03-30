import asyncio
import websockets


@asyncio.coroutine
def get(symbol):
    websocket = yield from websockets.connect(f'wss://api.bitkub.com/websocket-api/market.trade.{symbol}')
    result = yield from websocket.recv()
    print(result)


asyncio.get_event_loop().run_until_complete(get('thb_bch'))