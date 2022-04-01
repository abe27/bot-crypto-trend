import hashlib
import hmac
import json
import os
import requests
from datetime import datetime
from termcolor import colored
from tradingview_ta import TA_Handler
from libs.TimeFrame import TimeFrame
from libs.Logging import Logging


class Binance:
    def __init__(self):
        self.__URL__ = os.getenv('BINANCE_HOST', 'https://api.binance.com')
        self.__KEY__ = os.getenv('BINANCE_KEY')
        self.__SECRET__ = os.getenv('BINANCE_SECRET')
        self.__HEADER__ = {
            'Content-Type': 'application/json',
            'X-MBX-APIKEY': self.__KEY__
        }

    def json_encode(self, data):
        return json.dumps(data, separators=(',', ':'), sort_keys=True)

    def sign(self, data):
        signature = hmac.new(self.__SECRET__.encode('utf-8'),
                             data.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def timestamps(self):
        url = f"{self.__URL__}/api/v3/time"
        payload = {}
        headers = {'Content-Type': 'application/json'}

        response = requests.request("GET", url, headers=headers, data=payload)

        res = response.json()['serverTime']
        return {
            'timestamp': res,
            'datetime': datetime.fromtimestamp(int(str(res)[:-3]))
        }

    def price(self, symbol='BTC', quotes="BUSD"):
        url = f"{self.__URL__}/api/v3/ticker/24hr?symbol={symbol}{quotes}"
        payload = {}
        headers = {'Content-Type': 'application/json'}

        response = requests.request("GET", url, headers=headers, data=payload)

        res = response.json()
        try:
            return [float(res['lastPrice']), float(res['priceChangePercent']), float(res['volume']), float(res['quoteVolume'])]
        except:
            pass

        return [0, 0, 0]

    def symbols(self, permissions="SPOT",quotes="BUSD"):
        url = f"{self.__URL__}/api/v3/exchangeInfo"
        payload = {}
        response = requests.request("GET",
                                    url,
                                    headers=self.__HEADER__,
                                    data=payload)
        res = response.json()
        symbols = []
        for i in res['symbols']:
            print(f"check {str(i['baseAsset'])} quote: {str(i['quoteAsset'])} market: {str(i['permissions'])}")
            if str(i['permissions']).find(permissions) >= 0 and i['quoteAsset'] == quotes:
                # symbols.append(i['baseAsset'])
                bal = self.price(symbol=i['baseAsset'], quotes=quotes)
                if bal[2] > 90000:
                    symbols.append(i['baseAsset'])

        # symbols.sort()
        print("\n")
        return symbols
