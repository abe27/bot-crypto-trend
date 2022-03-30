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
from libs.BitKub import BitKub
from libs.Binance import Binance
class Trend:
    def price(self, exchange="Bitkub", symbol="BTC"):
        if exchange == "Bitkub":return BitKub().price(symbol=symbol)
        elif exchange == "Binance":return Binance().price(symbol=symbol)
        return [0, 0, 0]
    
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
    def check_trend(self, symbol="KUB", quotes="THB", momentum='MA', exchange="Bitkub", market='SPOT', screener="crypto", exchange_color="green", neg_positive_limit=-4):
        trend = False
        score = 0
        obj_trend = []
        ### ตึงราคาและเปอร์เซนต์การเปลี่ยนแปลงล่าสุด
        last_price = self.price(exchange=exchange,symbol=symbol)
        ### loop ด้วย timeframe
        for t in TimeFrame().timeframe():
            ### ตรวจสอบ trend จาก web tradingview
            ta = TA_Handler(symbol=f"{symbol}{quotes}",
                            screener=screener,
                            exchange=exchange,
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
            
            obj_trend.append(summ)
            x = 0
            txt_color = "red"
            ### กรอง recomment ที่เป็น strong sell
            txt_time = "STRONG_BUY"
            time_array = ["1h","2h","4h","1d","1W","1M"]
            time_match = t in time_array
            if time_match:
                txt_time = "BUY"
                if last_price[1] >  0 and last_price[1] < 2:
                    txt_time = "STRONG_BUY"
                    
            if str(summ) == "STRONG_SELL" or str(summ).find(txt_time) == 0:
                x = 1
                txt_color = "green"

            print(
                f"{symbol} {momentum}: {colored(summ, txt_color)} ON:{t} SCORE: {x}"
            )
            ### ทำคะแนน avg
            score += x
            
        ### ตึงราคาและเปอร์เซนต์การเปลี่ยนแปลงล่าสุด
        last_price = self.price(exchange=exchange,symbol=symbol)
        if market == "SPOT":
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
                if interesting == "Buy" and last_price[1] <= neg_positive_limit:
                    trend = True
                    txt_msg = "ขาขึ้น ☝️"
                    
            elif str(summ).find('BUY') >= 0:
                if interesting == "Buy":
                    if last_price[1] >= 0 and last_price[1] < 2:
                        trend = True
                        txt_msg = "ขาขึ้น ☝️"

            msg = f"""ตลาด {exchange}({market})\nเหรียญ: {symbol}/{quotes}\nอยู่ในช่วง: {txt_msg}\nราคาล่าสุด: {price} {quotes}\nการเปลี่ยนแปลง: {last_price[1]}%\nMomentum:{momentum}"""
            print(
                f"[{colored(exchange, exchange_color)}]:=> {symbol} is {colored(interesting, txt_color)}({score}-{total_timeframe} = {colored(score-total_timeframe, txt_color)}) price: {colored(price, txt_color)} {quotes} percent: {colored(last_price[1], txt_color)} % avg: {colored(score, txt_color)}"
            )
            
        else:
            trend = "-"
            interesting = False
            score = 0
            total_timeframe = 0
            msg = f"""Not Respone"""
            
        
        Logging(symbol=symbol,msg=f'{market} :=> {momentum} IS {interesting}({last_price[1]})%')
        return {
            "market": market,
            "interesting": trend,
            "exchange": exchange,
            'trend': interesting,
            "symbol": symbol,
            "quotes": quotes,
            "price": last_price[0],
            "percent": last_price[1],
            "avg_score": (score - total_timeframe),
            "momentum": momentum,
            "timeframe": t,
            "message": msg
        }
