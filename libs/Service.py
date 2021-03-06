import os
from nanoid import generate
import mysql.connector
from libs.Logging import Logging
from libs.BitKub import BitKub
from libs.Binance import Binance
from libs.Notification import Notification

notf = Notification()
bitkub = BitKub()
bnb = Binance()
key_generate = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


class MysqlService:
    def __init__(self):
        self.MYSQL_DB = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DBNAME'))

    def logs(self,
             symbol,
             quotes='THB',
             price=0,
             percent=0,
             exchange='BITKUB'):
        if price > 0:
            mycursor = self.MYSQL_DB.cursor(buffered=True)
            sql = f"INSERT INTO tbt_signals(id, exchange, `date`, symbol, quotes, price, percent)VALUES('{str(generate(key_generate, 21))}', '{exchange}',current_timestamp, '{symbol}', '{quotes}', {price}, {percent})"
            mycursor.execute(sql)
            self.MYSQL_DB.commit()

    def update(self,
               symbol='None',
               exchange='Bitkub',
               quotes="THB",
               market="SPOT",
               update_price=True):
        bb = [0, 0, 0]
        if exchange == 'Bitkub':bb = bitkub.price(symbol=symbol, quotes=quotes)
        elif exchange == 'Binance':bnb.price(symbol=symbol, quotes=quotes)

        price = float(bb[0])
        percent = float(bb[1])
        mycursor = self.MYSQL_DB.cursor(buffered=True)
        sql = f"select id,price,last_price from tbt_investments where symbol='{symbol}' and exchange='{exchange}' and quotes='{quotes}' and is_activate=1 order by price"
        mycursor.execute(sql)
        myresult = mycursor.fetchone()
        txt = 'UPDATE PRICE'
        is_stats = 1
        is_trend = 1

        msg = None
        if myresult != None:
            current_price = float(str(myresult[1]))
            ## ????????????????????????????????????????????????????????????????????????
            profit_percent = float("{:.2f}".format(
                float(((price - current_price) * 100) / current_price)))
            # last_price = float(str(myresult[2]))
            ## ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????? 4%

            profit_limit = float(os.getenv('PROFIT_PERCENT', 10))
            pog = abs(profit_limit)

            ### ??????????????????????????? stoploss
            stop_loss = float(os.getenv('STOP_LOSS', 4))
            neg = stop_loss * (-1)

            profit = price - current_price
            emoji = '????'
            if profit < 0 or price < float(str(myresult[1])):
                is_trend = 0
                emoji = '????'

            ## ?????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????? {pog}%
            ## ????????????????????????????????????????????????????????????????????????????????? {neg}
            ## ????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????
            last_price = 0
            profit_price = 0
            profit_pt = 0
            if update_price is False:
                if profit_percent > pog or (price -
                                            float(str(myresult[1]))) < neg:
                    is_stats = 0
                    txt = 'CLOSE ORDER'
                    last_price = f"{price:,}"
                    profit_price = "{:.2f}".format(profit)
                    profit_pt = "{:.2f}".format(profit_percent)
                    msg = f"""????????????: {exchange}({market})\n????????????????????????????????????: {symbol}/{quotes}\n????????????: {last_price} {quotes}\n??????????????????: {emoji} {profit_price} {quotes}\n?????????????????????????????????: {profit_pt}%"""

            sql = f"""update tbt_investments set 
                last_price='{price}',
                percent_change='{percent}',
                avg_score={profit_percent},
                is_activate={is_stats},
                is_trend={is_trend},
                last_update=current_timestamp
                where symbol='{symbol}' and exchange='{exchange}' and quotes='{quotes}' and is_activate=1"""

            last_price = "{:.2f}".format(price)
            profit_pt = "{:.2f}".format(profit_percent)
            # print(sql)
            mycursor.execute(sql)
            self.MYSQL_DB.commit()
            print(f'{txt} {symbol}:=> {myresult[0]} last: {last_price}')
            txt_status = '-'
            if is_stats == 0:
                txt_status = 'CLOSED'

            txt_percent = f"{profit_pt}%"
            Logging(
                exchange=exchange,
                symbol=symbol,
                quotes=quotes,
                msg=
                f'SUBSCIBE {txt} :=> {myresult[0]} PROFIT: {str(txt_percent).ljust(10)} STATUS: {txt_status}'
            )

        ### ?????????????????????????????????????????? 30????????????
        self.logs(symbol, exchange, price, percent)
        if msg != None: notf.line(msg)
        return True

    def insert(self,
               symbol='None',
               quotes='THB',
               price=0,
               percent=0,
               is_trend=1,
               avg_score=0,
               momentum='None',
               exchange='BITKUB'):
        mycursor = self.MYSQL_DB.cursor(buffered=True)
        sql = f"select id,price from tbt_investments where symbol='{symbol}' and quotes='{quotes}' and momentum='{momentum}' and is_activate=1"
        mycursor.execute(sql)
        myresult = mycursor.fetchone()
        uid = str(generate(key_generate, 21))
        is_new = False
        if myresult is None:
            sql = f"""INSERT INTO tbt_investments(id,exchange,momentum,symbol,quotes,price,percent,last_price,percent_change,is_activate, is_trend, avg_score,created_on,last_update) VALUES ('{uid}','{exchange}','{momentum}','{symbol}', '{quotes}','{price}','{percent}','{price}', '{percent}', 1, {is_trend}, {avg_score},current_timestamp, current_timestamp)"""
            Logging(exchange=exchange,
                    symbol=symbol,
                    quotes=quotes,
                    msg=f'NEW {momentum} RECORD :=> {uid}')
            print(f'insert db :=> {symbol}')
            mycursor.execute(sql)
            self.MYSQL_DB.commit()
            is_new = True

        else:
            # ## update ????????????????????????????????????
            self.update(symbol=symbol, exchange=exchange, quotes=quotes)

        return is_new
