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

# mydb = mysql.connector.connect(host=os.getenv('MYSQL_HOST'),
#                                user=os.getenv('MYSQL_USER'),
#                                password=os.getenv('MYSQL_PASSWORD'),
#                                database=os.getenv('MYSQL_DBNAME'))


# def insert_db(symbol, price, percent, is_trend, avg_score):
#     etd = datetime.now().strftime('%Y-%m-%d')
#     mycursor = mydb.cursor()
#     sql = f"select id,on_price from tbt_subscribe where symbol='{symbol}' and is_activate=1"
#     mycursor.execute(sql)
#     myresult = mycursor.fetchone()

#     sql = f"""INSERT INTO tbt_subscribe (id,etd,symbol,on_price,on_percent,last_price,percent_change,is_activate, is_trend, avg_score,created_on,last_update) VALUES (uuid(),current_timestamp,'{symbol}', '{price}','{percent}','{price}', '{percent}', {is_trend}, {is_trend}, {avg_score},current_timestamp, current_timestamp)"""
#     if myresult != None:
#         is_stats = 0
#         if price > float(myresult[1]):
#             is_stats = 1
            
#         sql = f"""update tbt_subscribe set 
#         last_price='{price}',
#         percent_change='{percent}',
#         is_activate={is_stats},
#         is_trend={is_stats},
#         avg_score={avg_score},
#         last_update=current_timestamp
#         where id='{myresult[0]}'"""

#     mycursor.execute(sql)
#     mydb.commit()
#     print(mydb)


def loop_for_trend(s):
    score = 0
    print(colored(f"start loop {s}", "blue"))
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

    is_trend = 0
    if interesting == 'Buy':
        is_trend = 1

    mydb.insert_db(s, last_price[0], last_price[1], is_trend,
                  score - total_timeframe)

    print("******************************")


def main():
    mycursor = mydb.MYSQL_DB.cursor()
    sql = f"select symbol  from tbt_subscribe where is_activate=1 order by symbol "
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for i in myresult:
        loop_for_trend(s=i[0])


if __name__ == '__main__':
    main()
    sys.exit(0)
