import sys
import os
from termcolor import colored
from datetime import datetime
from tradingview_ta import TA_Handler, Interval, Exchange
from dotenv import load_dotenv

load_dotenv()
from libs.BitKub import BitKub
from libs.Service import MysqlService

# initialize environ
bitkub = BitKub()
mydb = MysqlService()


def loop_for_trend(s):
    score = 0
    for t in bitkub.timeframe():
        ta = TA_Handler(symbol=f"{s}THB",
                        screener="crypto",
                        exchange="Bitkub",
                        interval=t)
        summary = []
        try:
            summary = ta.get_analysis().summary
            summary['SYMBOL'] = s
            summary['QOUTE'] = "THB"
            summary['ON_TIME'] = t
        except:
            pass
        if len(summary) > 0:
            recomm = summary['RECOMMENDATION']
            x = 0
            if str(recomm).find('BUY') >= 0: x = 1
            if recomm == "NEUTRAL": x = 1
            txt_color = "green"
            if x == 0: txt_color = "red"
            print(f"{s} is {colored(recomm, txt_color)} on {t} score: {x}")
            score += x
    print(colored(f"end loop {s}", "blue"))
    interesting = "Sell"
    txt_color = "red"
    if score >= len(bitkub.timeframe()):
        interesting = "Buy"
        txt_color = "green"
    last_price = bitkub.price(product=s)
    if last_price[0] == 0:
        interesting = "-"
        txt_color = "magenta"
    total_timeframe = len(bitkub.timeframe())
    total_avg = 0
    if (score - total_timeframe) >= 0:
        interesting = "Buy"
        txt_color = "green"
        total_avg = 1

    print(
        f"{s} is {colored(interesting, txt_color)}({score}-{total_timeframe} = {colored(score-total_timeframe, txt_color)}) price: {last_price[0]:,}THB percent: {last_price[1]}% avg: {total_avg}"
    )

    return {
        "symbol": s,
        "price": last_price[0],
        "percent": last_price[1],
        "avg_score": (score - total_timeframe)
    }


def main():
    server_time = bitkub.timestamps()
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    # update subscribe
    mycursor = mydb.MYSQL_DB.cursor()
    sql = f"select symbol  from tbt_subscribe where is_activate=1 order by symbol "
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for i in myresult:
        print(colored(f"start subscribe loop {i[0]}", "blue"))
        x = loop_for_trend(s=i[0])
        mydb.update(symbol=x['symbol'], price=x['price'], percent=x['percent'])

    # get net trend
    symbols = bitkub.symbols()
    for s in symbols:
        print(colored(f"start subscribe loop {i[0]}", "green"))
        x = loop_for_trend(s=s)
        mydb.insert(symbol=x['symbol'], price=x['price'], percent=x['percent'], is_trend=1, avg_score=x['avg_score'])
        
    server_time = bitkub.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}","red"))
    print("******************************")

if __name__ == '__main__':
    main()
    sys.exit(0)
