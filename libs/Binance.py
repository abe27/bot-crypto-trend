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
        signature = hmac.new(self.__SECRET__.encode('utf-8'), data.encode('utf-8'), hashlib.sha256).hexdigest()
        return signature

    def timestamp(self):
        url = f"{self.__URL__}/api/v3/time"
        payload = {}
        headers = {'Content-Type': 'application/json'}

        response = requests.request("GET", url, headers=headers, data=payload)

        res = response.json()['serverTime']
        return {
            'timestamp': res,
            'datetime': datetime.fromtimestamp(int(str(res)[:-3]))
        }
        
    def ticker(self, symbol='BTC'):
        url = f"{self.__URL__}/api/v3/ticker/24hr?symbol={symbol}USDT"
        payload={}
        headers = {
            'Content-Type': 'application/json'
        }

        response = requests.request("GET", url, headers=headers, data=payload)

        res = response.json()
        data = None
        try:
            data = res
        except :
            code = res['code']
            print(f"error :=> {code}")
            
        return data
        
    def symbols(self):
        timestamp = self.timestamp()
        sign = self.sign(f"timestamp={timestamp['timestamp']}")
        url = f"{self.__URL__}/sapi/v1/capital/config/getall?timestamp={timestamp['timestamp']}&signature={sign}"
        payload={}
        response = requests.request("GET", url, headers=self.__HEADER__, data=payload)
        res = response.json()
        symbols = []
        for i in res:
            symbols.append(i['coin'])
        
        symbols.sort()
        return symbols
    
    ### function ตรวจสอบ Trend
    def check_trend(self, symbol, momentum='MA'):
        trend = False
        score = 0
        ### loop ด้วย timeframe
        for t in TimeFrame().timeframe():
            ### ตรวจสอบ trend จาก web tradingview
            ta = TA_Handler(symbol=f"{symbol}USDT",
                            screener="crypto",
                            exchange="Binance",
                            interval=t)
            summ = '-'
            try:
                ### เช็คเงื่อนไข
                if momentum == 'SUM':summ = ta.get_analysis().summary['RECOMMENDATION']
                elif momentum == 'OSCI':summ = ta.get_analysis().oscillators['RECOMMENDATION']
                ### กรณีไม่ได้กำหนดค่า momentum ให้ใช้ MA
                else:summ = ta.get_analysis().moving_averages['RECOMMENDATION']
            except:pass
            
            x = 0
            txt_color = "red"
            ### กรอง recomment ที่เป็น strong sell
            if str(summ) == "STRONG_SELL" or str(summ).find('BUY') == 0:
                x = 1
                txt_color = "green"
                
            print(f"{symbol} {momentum}: {colored(summ, txt_color)} ON:{t} SCORE: {x}")
            ### ทำคะแนน avg
            score += x
            
        ### ตึงราคาและเปอร์เซนต์การเปลี่ยนแปลงล่าสุด     
        last_price = self.price(symbol=symbol)
        interesting = "Sell"
        txt_color = "red"
        total_timeframe = len(self.timeframe())
        ### ตรวจสอบคะแนน avg > timeframe.length
        if score >= len(self.timeframe()) or (score - total_timeframe) >= 0:
            interesting = "Buy"
            txt_color = "green"
            # trend = True
        
        ### ตรวจสอบราคาล่าสุด
        if last_price[0] == 0:
            interesting = "-"
            txt_color = "magenta"
            
        price = f"{last_price[0]:,}"
        # trend = False
        profit_limit = float(os.getenv('STRONG_PERCENT', 10))
        neg = profit_limit * (-1)
        # # ### ตรวจสอบเปอร์เซนต์การเปลี่ยนแปลงต้อง < 0 กำหนดเป็นขาขึ้น
        txt_msg = "ขาลง 👇"
        if last_price[1] < neg:
            trend = True
            txt_msg = "ขาขึ้น ☝️"
        
        msg = f"""ตลาด Bitkub\nเหรียญ {symbol} อยู่ในช่วง{txt_msg}\nราคาล่าสุด {price}บาท\nการเปลี่ยนแปลง {last_price[1]}%""" 
        print(
            f"{symbol} is {colored(interesting, txt_color)}({score}-{total_timeframe} = {colored(score-total_timeframe, txt_color)}) price: {colored(price, txt_color)}THB percent: {colored(last_price[1], txt_color)} % avg: {colored(score, txt_color)}"
        )
        Logging(symbol=symbol,msg=f'{momentum} IS {interesting}({last_price[1]})%')
            
        return {
            "interesting": trend,
            "exchange": "Bitkub",
            'trend': interesting,
            "symbol": symbol,
            "price": last_price[0],
            "percent": last_price[1],
            "avg_score": (score - total_timeframe),
            "momentum": momentum,
            "timeframe": t,
            "message": msg
        }