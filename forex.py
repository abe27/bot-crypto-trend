import sys
from libs.TimeFrame import TimeFrame
from tradingview_ta import TA_Handler, Exchange


def main():
    quote_asset = "EURUSD"
    if len(sys.argv) > 1: quote_asset = str(sys.argv[1]).strip()
    time_frame = TimeFrame().INTERVAL_5_MINUTES
    handler = TA_Handler(symbol=quote_asset,
                         screener="forex",
                         exchange=Exchange.FOREX,
                         interval=time_frame)
    analysis = handler.get_analysis()
    print(analysis.indicators["RSI"])
    print(analysis.indicators["MACD.macd"])
    print(analysis.summary)


if __name__ == '__main__':
    main()
    sys.exit(0)