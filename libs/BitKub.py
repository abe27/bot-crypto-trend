import os
import requests
import json
import hmac
import hashlib
from datetime import datetime
from termcolor import colored
from tradingview_ta import TA_Handler, Interval, Exchange


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
        self.INTERVAL_1_MINUTE = "1m"
        self.INTERVAL_5_MINUTES = "5m"
        self.INTERVAL_15_MINUTES = "15m"
        self.INTERVAL_30_MINUTES = "30m"
        self.INTERVAL_1_HOUR = "1h"
        self.INTERVAL_2_HOURS = "2h"
        self.INTERVAL_4_HOURS = "4h"
        self.INTERVAL_1_DAY = "1d"
        self.INTERVAL_1_WEEK = "1W"
        self.INTERVAL_1_MONTH = "1M"

    def timeframe(self):
        return [
            # self.INTERVAL_1_MINUTE,
            # self.INTERVAL_5_MINUTES,
            # self.INTERVAL_15_MINUTES,
            self.INTERVAL_30_MINUTES,
            self.INTERVAL_1_HOUR,
            self.INTERVAL_2_HOURS,
            self.INTERVAL_4_HOURS,
            # self.INTERVAL_1_DAY,
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
        ticker = requests.get(self.API_HOST + '/api/market/ticker?sym=' +
                              f'THB_{product}')
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
        ticker = requests.get(self.API_HOST + '/api/market/ticker?sym=' +
                              f'THB_{product}')
        ticker = ticker.json()
        try:
            return [
                float(ticker[f'THB_{product}']['last']),
                float(ticker[f'THB_{product}']['percentChange'])
            ]

        except:
            pass

        return [0, 0]
    
    def check_trend(self, symbol):
        score = 0
        for t in self.timeframe():
            ta = TA_Handler(symbol=f"{symbol}THB",
                            screener="crypto",
                            exchange="Bitkub",
                            interval=t)
            summary = []
            try:
                summary = ta.get_analysis().summary
                summary['SYMBOL'] = symbol
                summary['QOUTE'] = "THB"
                summary['ON_TIME'] = t
            except:
                pass
            if len(summary) > 0:
                recomm = summary['RECOMMENDATION']
                x = 0
                if str(recomm).find('BUY') >= 0: x = 1
                # if recomm == "NEUTRAL": x = 1
                txt_color = "green"
                if x == 0: txt_color = "red"
                print(f"{symbol} is {colored(recomm, txt_color)} on {t} score: {x}")
                score += x

        interesting = "Sell"
        txt_color = "red"
        if score >= len(self.timeframe()):
            interesting = "Buy"
            txt_color = "green"
        last_price = self.price(product=symbol)
        if last_price[0] == 0:
            interesting = "-"
            txt_color = "magenta"
        total_timeframe = len(self.timeframe())
        total_avg = 0
        if (score - total_timeframe) >= 0:
            interesting = "Buy"
            txt_color = "green"
            total_avg = 1

        price = f"{last_price[0]:,}"
        print(
            f"{symbol} is {colored(interesting, txt_color)}({score}-{total_timeframe} = {colored(score-total_timeframe, txt_color)}) price: {colored(price, txt_color)}THB percent: {colored(last_price[1], txt_color)} % avg: {colored(total_avg, txt_color)}"
        )
        
        trend = False
        if last_price[1] <= 1:
            trend = True
            
        return {
            "interesting": trend,
            'trend': interesting,
            "symbol": symbol,
            "price": last_price[0],
            "percent": last_price[1],
            "avg_score": (score - total_timeframe)
        }
