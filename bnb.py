import sys
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()
from libs.Binance import Binance
from libs.Logging import Logging

bnb = Binance()
def main():
    server_time = bnb.timestamp()
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    # Logging(symbol='BNB', msg=f"START AT: {server_time['timestamp']}")
    # ดึงข้อมูลรายการ symbol ใน bitkub
    symbols = bnb.symbols()
    for sym in symbols:
        bal = bnb.price(symbol=sym)
        if bal != None:
            x = bnb.check_trend(symbol=sym)
            print(x)
            
        print('\n')
    
if __name__ == '__main__':
    main()
    sys.exit(0)