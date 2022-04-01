import sys
from libs.TimeFrame import TimeFrame
from tradingview_ta import TA_Handler


def main():
    quote_asset = "EURUSD"
    if len(sys.argv) > 1: quote_asset = str(sys.argv[1]).strip()
    time_frame = TimeFrame().INTERVAL_5_MINUTES
    handler = TA_Handler(symbol="EURUSD",
                         screener="forex",
                         exchange="BINANCE",
                         interval=time_frame)
    analysis = handler.get_analysis()
    print(analysis.indicators["RSI"])
    print(analysis.indicators["MACD.macd"])


if __name__ == '__main__':
    main()
    sys.exit(0)