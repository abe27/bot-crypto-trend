import sys
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()
from libs.Binance import Binance
from libs.Service import MysqlService
from libs.Logging import Logging
from libs.Notification import Notification

# initialize environ
bnb = Binance()
mydb = MysqlService()
notf = Notification()
def main():
    server_time = bnb.timestamps()
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    Logging(symbol='BNB', msg=f"START AT: {server_time['timestamp']}")
    # ดึงข้อมูลรายการ symbol ใน bitkub
    symbols = bnb.symbols()
    for sym in symbols:
        bal = bnb.price(symbol=sym)
        if bal != None:
            x = bnb.check_trend(symbol=sym)
            if x['trend'] == 'Buy' and x['interesting'] is True:
                ### ถ้าเป็นขาขึ้นให้บันทึกข้อมูล
                is_new = mydb.insert(symbol=x['symbol'],
                                     quotes=x['quotes'],
                                     price=x['price'],
                                     percent=x['percent'],
                                     is_trend=0,
                                     avg_score=x['avg_score'],
                                     momentum=x['momentum'],
                                     exchange='BNB')
            
                #### ส่งข้อความผ่านทางไลน์
                if is_new:
                    notf.line(x['message'])
        
    server_time = bnb.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}",
                "red"))
    print("******************************")
    Logging(symbol='BNB', msg=f"END AT: {server_time['timestamp']}")
    
if __name__ == '__main__':
    main()
    sys.exit(0)