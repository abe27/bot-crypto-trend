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
    def price(self, exchange="Bitkub", symbol="BTC", quotes="THB"):
        if exchange == "Bitkub":
            return BitKub().price(symbol=symbol, quotes=quotes)
        elif exchange == "Binance":
            return Binance().price(symbol=symbol, quotes=quotes)
        return [0, 0, 0]

    def check_subscribe(self, symbol='None', quotes="THB"):
        x = False
        try:
            ta = TA_Handler(symbol=f"{symbol}{quotes}",
                            screener="crypto",
                            exchange="Bitkub",
                            interval=self.INTERVAL_15_MINUTES)

            mv_avg = ta.get_analysis().moving_averages['RECOMMENDATION']
            if str(mv_avg).find('BUY') >= 0:
                x = True
        except:
            pass

        last_price = self.price(symbol=symbol, quotes=quotes)

        return {
            'close': x,
            "symbol": symbol,
            "price": last_price[0],
            "percent": last_price[1],
        }

    ### function ตรวจสอบ Trend
    def check_trend(self,
                    symbol="KUB",
                    quotes="THB",
                    momentum='MA',
                    exchange="Bitkub",
                    market='SPOT',
                    screener="crypto",
                    exchange_color="green",
                    neg_positive_limit=-4):
        trend = False
        interesting = "-"
        score = 0
        total_timeframe = 0
        obj_trend = []
        ### ตึงราคาและเปอร์เซนต์การเปลี่ยนแปลงล่าสุด
        last_price = self.price(exchange=exchange,
                                symbol=symbol,
                                quotes=quotes)
        if market == 'SPOT':
            for t in TimeFrame().timeframe():
                ### ตรวจสอบ trend จาก web tradingview
                ta = TA_Handler(symbol=f"{symbol}{quotes}",
                                screener=screener,
                                exchange=exchange,
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
                    if summ == "STRONG_SELL" or str(summ).find("BUY") == 0:
                        trend = True
                except:
                    pass

        else:
            msg = f"""Not Respone"""

        txt_msg = f"{summ} 🚫⛔"
        if trend:  ###str(summ) == "STRONG_SELL" or str(summ) == "BUY":
            #### check confirm_timeframes
            txt_trend = summ
            # if str(summ) == "BUY": txt_trend = "STRONG_SELL"
            l = TimeFrame().confirm_timeframes()
            for c in l:
                ### ตรวจสอบ trend จาก web tradingview
                ta = TA_Handler(symbol=f"{symbol}{quotes}",
                                screener=screener,
                                exchange=exchange,
                                interval=c)
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

                if str(c) == '1m':
                    if str(summ).find(txt_trend) >= 0: obj_trend.append(summ)

                elif str(c) == '5m':
                    if str(summ).find(txt_trend) >= 0: obj_trend.append(summ)

                elif str(c) == '15m':
                    if str(summ).find(txt_trend) >= 0: obj_trend.append(summ)

                elif str(c) == '30m':
                    if str(summ).find(txt_trend) >= 0: obj_trend.append(summ)

                elif str(c) == '1h':
                    if str(summ).find(txt_trend) >= 0: obj_trend.append(summ)

                elif str(c) == '2h':
                    if summ == "STRONG_SELL": txt_trend = "BUY"
                    if str(summ).find(txt_trend) >= 0: obj_trend.append(summ)

                # elif str(c) == '4h':
                #     if summ == "STRONG_SELL": txt_trend = "BUY"
                #     else: txt_trend.replace("STRONG", "")
                #     if str(summ).find(txt_trend) == 0: obj_trend.append(summ)

                print(
                    f"TIME: {colored(str(c).ljust(15), 'red')}TREND: {colored(str(summ).ljust(15), 'red')}FILTER: {colored(str(txt_trend).ljust(15), 'red')}IS: {colored(str(summ).find(txt_trend) >= 0, 'red')}"
                )

            txt_msg = f"ขาลง 👇"
            trend = False
            interesting = "Sell"
            txt_color = "red"
            if len(obj_trend) >= len(TimeFrame().confirm_timeframes()):
                trend = True
                interesting = "Buy"
                txt_color = "green"
                txt_msg = f"ขาขึ้น ☝️"

            txt_exchange = f"[{exchange}]"
            print(
                f"EXC: {colored(str(txt_exchange).ljust(15), txt_color)}] SYMBOL: {colored(str(symbol).ljust(15), txt_color)} IS: {colored(str(interesting).ljust(15), txt_color)}"
            )

        price = f"{last_price[0]:,}"
        if str(txt_msg).find("SELL") == 0:
            txt_msg = f"ขาลง 🔻"
            
        elif str(txt_msg).find("BUY") == 0:
            txt_msg = f"ขาขึ้น 🔺"
            
        elif str(txt_msg).find("STRONG_BUY") == 0:
            txt_msg = f"ขาขึ้นอย่างรุนแรง 🔺🥶"
            
        elif str(txt_msg).find("STRONG_SELL") == 0:
            txt_msg = f"ขาลงอย่างรุ่นแรง 🔻😱"
        
        elif str(txt_msg).find("NEUTRAL") == 0:
            txt_msg = f"ตลาดผันผวนน้อย 😬"
        
        msg = f"""ตลาด {exchange}({market})\nเหรียญ: {symbol}/{quotes}\nอยู่ในช่วง: {txt_msg}\nราคาล่าสุด: {price} {quotes}\nการเปลี่ยนแปลง: {last_price[1]}%\nMomentum: {momentum}"""
        if trend is False:
            if last_price[1] < -5:
                trend = True
                
        msg += "\nหมายเหตุ: ** เช็คกราฟก่อนซื้อ-ขาย **"

        print(msg)

        Logging(
            exchange=exchange,
            symbol=symbol,
            quotes=quotes,
            msg=f'{market} :=> {momentum} IS {interesting}({last_price[1]})%')

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
