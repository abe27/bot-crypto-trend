import sys
from termcolor import colored
from dotenv import load_dotenv

load_dotenv()
from libs.BitKub import BitKub
from libs.Service import MysqlService

# initialize environ
bitkub = BitKub()
mydb = MysqlService()


def main():
    server_time = bitkub.timestamps()
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    # get net trend
    symbols = bitkub.symbols()
    for s in symbols:
        print(colored(f"start new order loop {s}", "green"))
        x = bitkub.check_trend(symbol=s)
        if x['interesting']:
            mydb.insert(symbol=x['symbol'],
                        price=x['price'],
                        percent=x['percent'],
                        is_trend=1,
                        avg_score=x['avg_score'])

    server_time = bitkub.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}",
                "red"))
    print("******************************")


if __name__ == '__main__':
    main()
    sys.exit(0)
