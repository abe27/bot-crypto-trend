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
        self.__URL__ = os.getenv('ฺBINANCE_HOST')
        self.__KEY__ = os.getenv('ฺBINANCE_KEY')
        self.__SECRET__ = os.getenv('ฺBINANCE_SECRET')
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

    def price(self, symbol='BTC'):
        url = f"{self.__URL__}/api/v3/ticker/24hr?symbol={symbol}BUSD"
        payload = {}
        headers = {'Content-Type': 'application/json'}

        response = requests.request("GET", url, headers=headers, data=payload)

        res = response.json()
        try:
            return [float(res['lastPrice']), float(res['priceChangePercent'])]
        except:
            pass

        return [0, 0]

    def symbols(self):
        url = f"{self.__URL__}/api/v3/exchangeInfo"

        payload = {}
        response = requests.request("GET",
                                    url,
                                    headers=self.__HEADER__,
                                    data=payload)
        res = response.json()
        symbols = []
        for i in res['symbols']:
            # print(str(i['permissions']))
            if str(i['permissions']).find(
                    'SPOT') >= 0 and i['quoteAsset'] == "BUSD":
                symbols.append(i['baseAsset'])

        symbols.sort()
        return symbols

    ### function ตรวจสอบ Trend
    def check_trend(self, symbol, momentum='MA'):
        trend = False
        score = 0
        ### loop ด้วย timeframe
        for t in TimeFrame().timeframe():
            ### ตรวจสอบ trend จาก web tradingview
            ta = TA_Handler(symbol=f"{symbol}BUSD",
                            screener="crypto",
                            exchange="Binance",
                            interval=t)
            summ = '-'
            try:
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
        # trend = False
        profit_limit = float(os.getenv('STRONG_BNB_PERCENT', 10))
        # neg = profit_limit * (-1)
        positive_limit = abs(profit_limit)
        # # ### ตรวจสอบเปอร์เซนต์การเปลี่ยนแปลงต้อง < 0 กำหนดเป็นขาขึ้น
        txt_msg = "ขาลง 👇"
        if interesting == "Buy" and last_price[1] < positive_limit:
            trend = True
            txt_msg = "ขาขึ้น ☝️"

        msg = f"""ตลาด BNB\nเหรียญ {symbol} อยู่ในช่วง{txt_msg}\nราคาล่าสุด {price} ดอลล่า\nการเปลี่ยนแปลง({last_price[1]}%)\nMomentum ที่ใช้ {momentum}"""
        print(
            f"{symbol} is {colored(interesting, txt_color)}({score}-{total_timeframe} = {colored(score-total_timeframe, txt_color)}) price: {colored(price, txt_color)}THB percent: {colored(last_price[1], txt_color)} % avg: {colored(score, txt_color)}"
        )
        Logging(symbol=symbol,
                msg=f'{momentum} IS {interesting}({last_price[1]})%')

        return {
            "interesting": trend,
            "exchange": "BNB",
            'trend': interesting,
            "symbol": symbol,
            "quotes": "BUSD",
            "price": last_price[0],
            "percent": last_price[1],
            "avg_score": (score - total_timeframe),
            "momentum": momentum,
            "timeframe": t,
            "message": msg
        }
