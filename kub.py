import sys
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()
from libs.BitKub import BitKub
from libs.Service import MysqlService
from libs.Logging import Logging
from libs.Notification import Notification

# initialize environ
bitkub = BitKub()
mydb = MysqlService()
notf = Notification()


def main():
    server_time = bitkub.timestamps()
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    Logging(symbol='BITKUB', msg=f"START AT: {server_time['timestamp']}")
    # ดึงข้อมูลรายการ symbol ใน bitkub
    symbols = bitkub.symbols()
    for s in symbols:
        print(colored(f"start new order loop {s}", "green"))
        # momentum = ['SUM', 'MA', 'OSCI']
        ## ตรวจสอบข้อมูล momentum MA
        momentum = ['MA']
        for m in momentum:
            ## ตรวจสอบ Trend ด้วย momentum
            x = bitkub.check_trend(symbol=s, momentum=m)
            if x['trend'] == 'Buy' and x['interesting'] is True:
                ### ถ้าเป็นขาขึ้นให้บันทึกข้อมูล
                is_new = mydb.insert(symbol=x['symbol'],
                                     quotes=x['quotes'],
                                     price=x['price'],
                                     percent=x['percent'],
                                     is_trend=0,
                                     avg_score=x['avg_score'],
                                     momentum=x['momentum'],
                                     exchange='BITKUB')

                #### ส่งข้อความผ่านทางไลน์
                if is_new:
                    notf.line(x['message'])

    server_time = bitkub.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}",
                "red"))
    print("******************************")
    Logging(symbol='BITKUB', msg=f"END AT: {server_time['timestamp']}")


if __name__ == '__main__':
    main()
    sys.exit(0)
