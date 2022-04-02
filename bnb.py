import sys
import os
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()
from libs.Binance import Binance
from libs.Service import MysqlService
from libs.Logging import Logging
from libs.Notification import Notification
from libs.Trend import Trend

# initialize environ
bnb = Binance()
mydb = MysqlService()
notf = Notification()
td = Trend()


def main():
    exchange = "Binance"
    server_time = bnb.timestamps()
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    # ดึงข้อมูลรายการ symbol ใน bitkub
    market = "SPOT"  ### MARGIN, SPOT
    quotes = "BUSD"
    if len(sys.argv) > 1: quotes = sys.argv[1]  ### BUSD,USDT,BNB
    Logging(exchange=exchange,
            symbol='BNB',
            quotes=quotes,
            msg=f"START AT: {server_time['timestamp']}")
    symbols = bnb.symbols(permissions=market, quotes=quotes)
    for sym in symbols:
        bal = bnb.price(symbol=sym, quotes=quotes)
        if bal != None:
            momentums = ['MA']
            for m in momentums:
                print(f"start check momentum :=> {m}")
                x = td.check_trend(symbol=sym,
                                   quotes=quotes,
                                   momentum=m,
                                   exchange=exchange,
                                   market=market,
                                   exchange_color="yellow")
                if x['trend'] == 'Buy' and x['interesting'] is True:
                    ### ถ้าเป็นขาขึ้นให้บันทึกข้อมูล
                    is_new = mydb.insert(symbol=x['symbol'],
                                         quotes=x['quotes'],
                                         price=x['price'],
                                         percent=x['percent'],
                                         is_trend=0,
                                         avg_score=x['avg_score'],
                                         momentum=x['momentum'],
                                         exchange=exchange)

                    #### ส่งข้อความผ่านทางไลน์
                    if is_new:
                        notf.line(msg=x['message'], token=os.getenv('LINE_BNB_TOKEN'))

                print(f"end check momentum :=> {m}")
        print('***********************************************\n')

    server_time = bnb.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}",
                "red"))
    print("******************************")
    Logging(exchange=exchange,
            symbol='BNB',
            quotes=quotes,
            msg=f"END AT: {server_time['timestamp']}")


if __name__ == '__main__':
    main()
    sys.exit(0)