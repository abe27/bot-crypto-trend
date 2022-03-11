import sys
from termcolor import colored
from tradingview_ta import TA_Handler, Interval, Exchange
from dotenv import load_dotenv

load_dotenv('./env')
from libs.BitKub import BitKub

# initialize environ
bitkub = BitKub()


def main():
    server_time = bitkub.timestamps()
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))

    symbols = bitkub.symbols()
    for s in symbols:
        # loop timeframe
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

        print(
            f"{s} is {colored(interesting, txt_color)}({score}-{len(bitkub.timeframe())} = {colored(score-len(bitkub.timeframe()), txt_color)}) price: {bitkub.price(product=s)}"
        )
        
        if interesting == "Buy":
            print('insert data')
            
        print("******************************")


if __name__ == '__main__':
    main()
    sys.exit(0)
