import sys
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()
from libs.BitKub import BitKub
from libs.Service import MysqlService
from libs.Logging import Logging

# initialize environ
bitkub = BitKub()
mydb = MysqlService()


def main():
    server_time = bitkub.timestamps()
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    Logging(symbol='SEARCH', msg=f"START AT: {server_time['timestamp']}")
    # get net trend
    symbols = bitkub.symbols()
    for s in symbols:
        print(colored(f"start new order loop {s}", "green"))
        # momemtum = ['SUM', 'MA', 'OSCI']
        momemtum = ['MA']
        for m in momemtum:
            x = bitkub.check_trend(symbol=s, momemtum=m)
            if x['trend'] == 'Buy' and x['interesting'] is True:
                mydb.insert(symbol=x['symbol'],
                            price=x['price'],
                            percent=x['percent'],
                            is_trend=0,
                            avg_score=x['avg_score'],
                            momemtum=x['momemtum'])
        
        ## บันทึกข้อมูลราคา
        last_price = bitkub.price(symbol=s)
        mydb.logs(symbol=s, price=last_price[0], percent=last_price[1])
    server_time = bitkub.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}",
                "red"))
    print("******************************")
    Logging(symbol='SEARCH', msg=f"END AT: {server_time['timestamp']}")


if __name__ == '__main__':
    main()
    sys.exit(0)
