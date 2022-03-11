import os
import requests
import json
import hmac
import hashlib
from datetime import datetime


class BitKub:
    def __init__(self):
        # Initial envs.
        self.API_HOST = os.getenv('BITKUB_HOST')
        self.API_KEY = os.getenv('BITKUB_KEY')
        self.API_SECRET = os.getenv('BITKUB_SECRET')
        self.API_HEADER = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'X-BTK-APIKEY': self.API_KEY,
        }

        # initialize timeframe
        # self.INTERVAL_1_MINUTE = "1m"
        # self.INTERVAL_5_MINUTES = "5m"
        self.INTERVAL_15_MINUTES = "15m"
        self.INTERVAL_30_MINUTES = "30m"
        self.INTERVAL_1_HOUR = "1h"
        self.INTERVAL_2_HOURS = "2h"
        self.INTERVAL_4_HOURS = "4h"
        self.INTERVAL_1_DAY = "1d"
        # self.INTERVAL_1_WEEK = "1W"
        # self.INTERVAL_1_MONTH = "1M"

    def timeframe(self):
        return [
            # self.INTERVAL_1_MINUTE,
            # self.INTERVAL_5_MINUTES,
            self.INTERVAL_15_MINUTES,
            self.INTERVAL_30_MINUTES,
            self.INTERVAL_1_HOUR,
            self.INTERVAL_2_HOURS,
            self.INTERVAL_4_HOURS,
            self.INTERVAL_1_DAY,
            # self.INTERVAL_1_WEEK,
            # self.INTERVAL_1_MONTH,
        ]

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

    def ticket(self, product='BTC'):
        ticker = requests.get(self.API_HOST + '/api/market/ticker')
        ticker = ticker.json()
        return ticker[f'THB__{product}']

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
                doc.append(str(i['symbol'])[4:])

        doc.sort()
        return doc

    def price(self, product='BTC'):
        ticker = requests.get(self.API_HOST + '/api/market/ticker')
        ticker = ticker.json()
        try:
            return [
                float(ticker[f'THB_{product}']['last']),
                float(ticker[f'THB_{product}']['percentChange'])
            ]

        except:
            pass

        return [0, 0]
