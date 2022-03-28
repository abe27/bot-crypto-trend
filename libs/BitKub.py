import os
import requests
import json
import hmac
import hashlib
from datetime import datetime
from termcolor import colored
from tradingview_ta import TA_Handler
from libs.TimeFrame import TimeFrame
from libs.Logging import Logging


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

        # doc.sort()
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
        except:
            pass
        # except Exception as e:
        #     Logging(symbol='ERROR', msg=f'{symbol} ERR:{e}')
        #     pass

        return [0, 0]

    def check_subscribe(self, symbol='None'):
        x = False
        try:
            ta = TA_Handler(symbol=f"{symbol}THB",
                            screener="crypto",
                            exchange="Bitkub",
                            interval=self.INTERVAL_15_MINUTES)

            mv_avg = ta.get_analysis().moving_averages['RECOMMENDATION']
            if str(mv_avg).find('BUY') >= 0:
                x = True
        except:
            pass
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

    ### function ตรวจสอบ Trend
    def check_trend(self, symbol, momentum='MA'):
        trend = False
        score = 0
        ### loop ด้วย timeframe
        for t in TimeFrame().timeframe():
            ### ตรวจสอบ trend จาก web tradingview
            ta = TA_Handler(symbol=f"{symbol}THB",
                            screener="crypto",
                            exchange="Bitkub",
                            interval=t)
            summ = '-'
            try:
                ### เช็คเงื่อนไข
                ### เช็คเงื่อนไข
                recommendation = None
                if momentum == 'SUM':
                    recommendation = ta.get_analysis().summary
                elif momentum == 'OSCI':
                    recommendation = ta.get_analysis().oscillators

                ### กรณีไม่ได้กำหนดค่า momentum ให้ใช้ MA
                else:
                    recommendation = ta.get_analysis().moving_averages

                # print(recommendation)
                summ = recommendation['RECOMMENDATION']
            except:
                pass

            x = 0
            txt_color = "red"
            ### กรอง recomment ที่เป็น strong sell
            if str(summ) == "STRONG_SELL" or str(summ).find('BUY') == 0:
                x = 1
                txt_color = "green"

            print(
                f"{symbol} {momentum}: {colored(summ, txt_color)} ON:{t} SCORE: {x}"
            )
            ### ทำคะแนน avg
            score += x

        ### ตึงราคาและเปอร์เซนต์การเปลี่ยนแปลงล่าสุด
        last_price = self.price(symbol=symbol)
        interesting = "Sell"
        txt_color = "red"
        total_timeframe = len(TimeFrame().timeframe())
        ### ตรวจสอบคะแนน avg > timeframe.length
        if score >= len(
                TimeFrame().timeframe()) or (score - total_timeframe) >= 0:
            interesting = "Buy"
            txt_color = "green"
            # trend = True

        ### ตรวจสอบราคาล่าสุด
        if last_price[0] == 0:
            interesting = "-"
            txt_color = "magenta"

        price = f"{last_price[0]:,}"
        # # ### ตรวจสอบเปอร์เซนต์การเปลี่ยนแปลงต้อง < 0 กำหนดเป็นขาขึ้น
        txt_msg = "ขาลง 👇"
        if str(summ) == "STRONG_SELL":
            # trend = False
            # profit_limit = float(os.getenv('STRONG_BNB_PERCENT', 10))
            # positive_limit = profit_limit * (-1)
            if interesting == "Buy" and last_price[1] < -4:
                trend = True
                txt_msg = "ขาขึ้น ☝️"
                
        elif str(summ).find('BUY') == 0:
            if interesting == "Buy" and last_price[1] < 1:
                trend = True
                txt_msg = "ขาขึ้น ☝️"

        msg = f"""ตลาด Bitkub\nเหรียญ {symbol} อยู่ในช่วง{txt_msg}\nราคาล่าสุด {price} บาท\nการเปลี่ยนแปลง({last_price[1]}%)\nMomentum ที่ใช้ {momentum}"""
        print(
            f"{symbol} is {colored(interesting, txt_color)}({score}-{total_timeframe} = {colored(score-total_timeframe, txt_color)}) price: {colored(price, txt_color)}THB percent: {colored(last_price[1], txt_color)} % avg: {colored(score, txt_color)}"
        )
        Logging(symbol=symbol,
                msg=f'{momentum} IS {interesting}({last_price[1]})%')

        return {
            "interesting": trend,
            "exchange": "Bitkub",
            'trend': interesting,
            "symbol": symbol,
            "quotes": "THB",
            "price": last_price[0],
            "percent": last_price[1],
            "avg_score": (score - total_timeframe),
            "momentum": momentum,
            "timeframe": t,
            "message": msg
        }
