import os
import requests
import json
import hmac
import hashlib
from datetime import datetime
from termcolor import colored
from tradingview_ta import TA_Handler


class BitKub:
    def __init__(self):
        # Initial envs.
        self.API_HOST = os.getenv('BITKUB_HOST', 'https://api.bitkub.com')
        self.API_KEY = os.getenv('BITKUB_KEY')
        self.API_SECRET = os.getenv('BITKUB_SECRET')
        self.API_HEADER = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-BTK-APIKEY': self.API_KEY,
        }

    def json_encode(data):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)

    def sign(self, data):
        j = self.json_encode(data)
        # print('Signing payload: ' + j)
        h = hmac.new(self.API_SECRET, msg=j.encode(), digestmod=hashlib.sha256)
        return h.hexdigest()

    def timestamps(self):
        url = f"{self.API_HOST}/api/servertime"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        return {
            'timestamp': response.text,
            'datetime': datetime.fromtimestamp(int(response.text))
        }

    def ticker(self, product='BTC'):
        ticker = requests.get(self.API_HOST + '/api/market/ticker?sym=' +
                              f'THB_{product}')
        ticker = ticker.json()
        if len(ticker) > 0:
            return ticker[f'THB_{product}']
        
        return False

    def symbols(self):
        url = f"{self.API_HOST}/api/market/symbols"

        payload = {}
        headers = {}

        response = requests.request("GET", url, headers=headers, data=payload)

        doc = []
        obj = response.json()
        if obj['error'] == 0:
            data = obj['result']
            for i in data:
                symbol = str(i['symbol'])[4:]
                stable_coin = ['DAI', 'USDC', 'USDT', 'BUSD', 'UST', 'TUSD', 'DGX']
                ticker = self.ticker(product=str(symbol))
                if ticker:
                    # print(f"{symbol} :=> {int(ticker['baseVolume'])} is {(int(ticker['baseVolume']) >= 500000)}")
                    if int(ticker['baseVolume']) > 100000 and int(ticker['quoteVolume']) > 20000000:
                        if (symbol in stable_coin) is False:
                            doc.append(str(symbol))

        # doc.sort()
        return doc

    def price(self, symbol='BTC', quotes="THB"):
        ticker = requests.get(self.API_HOST + '/api/market/ticker?sym=' +
                              f'{quotes}_{symbol}')
        ticker = ticker.json()
        try:
            return [
                float(ticker[f'{quotes}_{symbol}']['last']),
                float(ticker[f'{quotes}_{symbol}']['percentChange']),
                float(ticker[f'{quotes}_{symbol}']['quoteVolume'])
            ]
        except:
            pass

        return [0, 0, 0]