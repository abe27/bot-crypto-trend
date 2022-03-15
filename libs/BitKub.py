import os
import requests
import json
import hmac
import hashlib
from datetime import datetime
from termcolor import colored
from tradingview_ta import TA_Handler, Interval, Exchange
from libs.Logging import Logging

def get_recomment(obj):
    recomm = "-"
    if obj != None:
        recomm = obj['RECOMMENDATION']
        
    return recomm

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

    def price(self, symbol='BTC'):
        ticker = requests.get(self.API_HOST + '/api/market/ticker?sym=' +
                              f'THB_{symbol}')
        ticker = ticker.json()
        try:
            return [
                float(ticker[f'THB_{symbol}']['last']),
                float(ticker[f'THB_{symbol}']['percentChange'])
            ]
        except:pass
        # except Exception as e:
        #     Logging(symbol='ERROR', msg=f'{symbol} ERR:{e}')
        #     pass

        return [0, 0]
    
    def check_subscibe(self, symbol='None'):
        x = False
        try:
            ta = TA_Handler(symbol=f"{symbol}THB",
                            screener="crypto",
                            exchange="Bitkub",
                            interval=self.INTERVAL_30_MINUTES)
            summary = ta.get_analysis().moving_averages
            mv_avg = get_recomment(summary)
            if str(mv_avg).find('BUY') >= 0:
                x = True
        except:pass
        # except Exception as e:
        #     Logging(symbol='ERROR', msg=f'{symbol} ERR:{e}')
        #     pass
        
        last_price = self.price(symbol=symbol)
        
        return {
            'close': x,
            "symbol": symbol,
            "price": last_price[0],
            "percent": last_price[1],
        }
    
    
    def check_trend(self, symbol, momemtum='SUM'):
        score = 0
        for t in self.timeframe():
            ta = TA_Handler(symbol=f"{symbol}THB",
                            screener="crypto",
                            exchange="Bitkub",
                            interval=t)
            summ = '-'
            # mv_avg = '-'
            # oscillator = '-'
            summary = []
            try:
                if momemtum == 'SUM':
                    summary = ta.get_analysis().summary
                    summ = get_recomment(summary)
                
                elif momemtum == 'MA':
                    summary = ta.get_analysis().moving_averages
                    summ = get_recomment(summary)
                
                elif momemtum == 'OSCI':
                    summary = ta.get_analysis().oscillators
                    summ = get_recomment(summary)
                    
                summary['SYMBOL'] = symbol
                summary['QOUTE'] = "THB"
                summary['ON_TIME'] = t
                
            except:pass
            # except Exception as e:
            #     Logging(symbol='ERROR', msg=f'{symbol} {momemtum}:{e}')
            #     pass
            
            if len(summary) > 0:
                x = 0
                if str(summ).find('SELL') > 0: 
                    x = 1
                
                txt_color = "green"
                if x == 0: txt_color = "red"
                print(f"{symbol} {momemtum}: {colored(summ, txt_color)} ON:{t} SCORE: {x}")
                score += x
                
        last_price = self.price(symbol=symbol)
        interesting = "Sell"
        txt_color = "red"
        if score >= len(self.timeframe()):
            interesting = "Buy"
            txt_color = "green"
        
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
        trend = False
        profit_limit = float(os.getenv('PROFIT_PERCENT', 10))
        neg = profit_limit * (-1)
        if last_price[1] < neg:
            trend = True
            
        print(
            f"{symbol} is {colored(interesting, txt_color)}({score}-{total_timeframe} = {colored(score-total_timeframe, txt_color)}) price: {colored(price, txt_color)}THB percent: {colored(last_price[1], txt_color)} % avg: {colored(total_avg, txt_color)}"
        )
        Logging(symbol=symbol,msg=f'{momemtum} IS {interesting}({last_price[1]})%')
            
        return {
            "interesting": trend,
            'trend': interesting,
            "symbol": symbol,
            "price": last_price[0],
            "percent": last_price[1],
            "avg_score": (score - total_timeframe),
            "momemtum": momemtum
        }
