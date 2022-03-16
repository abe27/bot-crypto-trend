import os
from nanoid import generate
import mysql.connector
from libs.Logging import Logging
from libs.BitKub import BitKub

bitkub = BitKub()
key_generate = '1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'


class MysqlService:
    def __init__(self):
        self.MYSQL_DB = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST'),
            user=os.getenv('MYSQL_USER'),
            password=os.getenv('MYSQL_PASSWORD'),
            database=os.getenv('MYSQL_DBNAME'))

    def logs(self, symbol, price, percent):
        if price > 0:
            mycursor = self.MYSQL_DB.cursor(buffered=True)
            sql = f"INSERT INTO tbt_signals(id, `date`, symbol, price, percent)VALUES('{str(generate(key_generate, 21))}', current_timestamp, '{symbol}', {price}, {percent})"
            mycursor.execute(sql)
            self.MYSQL_DB.commit()

    def update(self, symbol='None'):
        bb = bitkub.price(symbol=symbol)
        price = float(bb[0])
        percent = float(bb[1])
        mycursor = self.MYSQL_DB.cursor(buffered=True)
        sql = f"select id,price,last_price from tbt_investments where symbol='{symbol}' and is_activate=1"
        mycursor.execute(sql)
        myresult = mycursor.fetchone()
        txt = 'UPDATE PRICE'
        is_stats = 1
        is_trend = 1
        
        if myresult != None:
            current_price = float(str(myresult[1]))
            # last_price = float(str(myresult[2]))
            ## ตรวจเปอร์เซ็นต์สูงสุดตามกำหนดในนี้กำหนดที่ 4%
            profit_limit = float(os.getenv('PROFIT_PERCENT', 10))
            pog = abs(profit_limit)
            neg = profit_limit * (-1)
            percent_profit = (pog * current_price) / 100
            profit = price - current_price
            if profit < 0 or price < float(str(myresult[1])):is_trend = 0

            ## ตรวจเปอร์เซ็นต์สูงสุดตามกำหนดในนี้กำหนดที่ 4%
            ## ถ้าตรงตามเงื่อนไขให้ทำการปิดออร์เดอร์ในทันที
            if profit > percent_profit or percent > pog or (
                    price - float(str(myresult[1]))) < neg:
                is_stats = 0
                txt = 'CLOSE ORDER'

            sql = f"""update tbt_investments set 
                last_price='{price}',
                percent_change='{percent}',
                is_activate={is_stats},
                is_trend={is_trend},
                last_update=current_timestamp
                where id='{str(myresult[0])}'"""

            # print(sql)
            mycursor.execute(sql)
            self.MYSQL_DB.commit()
            print(f'{txt} {symbol}:=> {myresult[0]}')
            Logging(
                symbol=symbol,
                msg=
                f'SUBSCIBE {txt} :=> {myresult[0]} PROFIT: {(price-myresult[1])} STATUS: {is_stats}'
            )

        ### บันทึกราคาทุกๆ 30นาที
        self.logs(symbol, price, percent)
        return True

    def insert(self,
               symbol='None',
               price=0,
               percent=0,
               is_trend=1,
               avg_score=0,
               momemtum='None'):
        mycursor = self.MYSQL_DB.cursor(buffered=True)
        sql = f"select id,price from tbt_investments where symbol='{symbol}' and momemtum='{momemtum}' and is_activate=1"
        mycursor.execute(sql)
        myresult = mycursor.fetchone()
        uid = str(generate(key_generate, 21))
        sql = f"""INSERT INTO tbt_investments(id,momemtum,symbol,price,percent,last_price,percent_change,is_activate, is_trend, avg_score,created_on,last_update) VALUES ('{uid}','{momemtum}','{symbol}', '{price}','{percent}','{price}', '{percent}', 1, {is_trend}, {avg_score},current_timestamp, current_timestamp)"""
        if myresult is None:
            mycursor.execute(sql)
            self.MYSQL_DB.commit()
            Logging(symbol=symbol, msg=f'NEW {momemtum} RECORD :=> {uid}')
            print(f'insert db :=> {symbol}')

        # ## update ราคาปัจจุบัน
        # self.update(symbol=symbol, price=price, percent=percent)
        return True
