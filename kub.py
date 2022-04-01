import sys
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()
from libs.BitKub import BitKub
from libs.Service import MysqlService
from libs.Logging import Logging
from libs.Notification import Notification
from libs.Trend import Trend

# initialize environ
bitkub = BitKub()
mydb = MysqlService()
notf = Notification()
td = Trend()


def main():
    exchange = "Bitkub"
    server_time = bitkub.timestamps()
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    Logging(exchange=exchange, symbol='KUB', quotes="THB", msg=f"START AT: {server_time['timestamp']}")
    # ดึงข้อมูลรายการ symbol ใน bitkub
    symbols = bitkub.symbols()
    for s in symbols:
        print(colored(f"start new order loop {s}", "green"))
        momentums = ['MA']
        ## ตรวจสอบข้อมูล momentum MA
        # momentums = ['MA']
        for m in momentums:
            ## ตรวจสอบ Trend ด้วย momentum
            x = td.check_trend(symbol=s, quotes="THB", momentum=m, exchange=exchange, market="SPOT")
            if x['interesting'] is True:
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
                    notf.line(x['message'])
                print(f"end check momentum :=> {m}")

        print('***********************************************\n')

    server_time = bitkub.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}",
                "red"))
    print("******************************")
    Logging(exchange=exchange, symbol='KUB', quotes="THB", msg=f"END AT: {server_time['timestamp']}")


if __name__ == '__main__':
    main()
    sys.exit(0)
