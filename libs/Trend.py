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
        score = 0
        obj_trend = []
        check_lower_profit = -1
        check_top_profit = 1
        ### ตึงราคาและเปอร์เซนต์การเปลี่ยนแปลงล่าสุด
        last_price = self.price(exchange=exchange,
                                symbol=symbol,
                                quotes=quotes)
        ### loop ด้วย timeframe
        time_array = ["1h", "2h", "4h", "1d", "1W", "1M"]
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
            time_match = t in time_array
            if time_match:
                txt_time = "BUY"
                if last_price[1] > check_lower_profit and last_price[
                        1] < check_top_profit:
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
        last_price = self.price(exchange=exchange,
                                symbol=symbol,
                                quotes=quotes)
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
                    if last_price[1] > check_lower_profit and last_price[
                            1] < check_top_profit:
                        trend = True
                        txt_msg = "ขาขึ้น ☝️"

            msg = f"""ตลาด {exchange}({market})\nเหรียญ: {symbol}/{quotes}\nอยู่ในช่วง: {txt_msg}\nราคาล่าสุด: {price} {quotes}\nการเปลี่ยนแปลง: {last_price[1]}%\nMomentum: {momentum}"""
            print(
                f"[{colored(exchange, exchange_color)}]:=> {symbol} is {colored(interesting, txt_color)}({score}-{total_timeframe} = {colored(score-total_timeframe, txt_color)}) price: {colored(price, txt_color)} {quotes} percent: {colored(last_price[1], txt_color)} % avg: {colored(score, txt_color)}"
            )

        else:
            trend = False
            interesting = "-"
            score = 0
            total_timeframe = 0
            msg = f"""Not Respone"""

        if str(summ) == "STRONG_SELL" or str(summ) == "BUY":
            #### check confirm_timeframes
            txt_trend = "BUY"
            # if str(summ) == "BUY": txt_trend = "STRONG_SELL"

            obj_trend = []
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
                    if str(summ).find(txt_trend): obj_trend.append(summ)

                elif str(c) == '5m':
                    if str(summ).find(txt_trend): obj_trend.append(summ)

                elif str(c) == '15m':
                    if str(summ).find(txt_trend): obj_trend.append(summ)

                elif str(c) == '30m':
                    if str(summ).find(txt_trend): obj_trend.append(summ)

                elif str(c) == '1h':
                    if str(summ).find(txt_trend): obj_trend.append(summ)

                elif str(c) == '2h':
                    if txt_trend == "STRONG_SELL": txt_trend = "BUY"
                    if str(summ).find(txt_trend): obj_trend.append(summ)

                elif str(c) == '4h':
                    if txt_trend == "STRONG_SELL": txt_trend = "BUY"
                    if str(summ).find(txt_trend): obj_trend.append(summ)

                # txt_filter = txt_trend
                # if (c in time_array): txt_filter = "BUY"
                # if summ == txt_filter: obj_trend.append(summ)
                print(
                    f"TIME: {colored(str(c).ljust(15), 'red')}TREND: {colored(str(summ).ljust(15), 'red')}FILTER: {colored(str(txt_trend).ljust(15), 'red')}IS: {colored(str(summ).find(txt_trend) >= 0, 'red')}"
                )

            trend = False
            interesting = "Sell"
            txt_color = "red"
            if len(obj_trend) > len(TimeFrame().confirm_timeframes()):
                trend = True
                interesting = "Buy"
                txt_color = "green"
            
            txt_exchange = f"[{exchange}]"
            print(f"EXC: {colored(str(txt_exchange).ljust(15), txt_color)}] SYMBOL: {colored(str(symbol).ljust(15), txt_color)} IS: {colored(str(interesting).ljust(15), txt_color)}")

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
