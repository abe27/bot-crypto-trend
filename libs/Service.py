import os
import mysql.connector
from datetime import datetime

class MysqlService:
    def __init__(self):
        self.MYSQL_DB = mysql.connector.connect(host=os.getenv('MYSQL_HOST'),
                               user=os.getenv('MYSQL_USER'),
                               password=os.getenv('MYSQL_PASSWORD'),
                               database=os.getenv('MYSQL_DBNAME'))
        
    def insert_db(self, symbol, price, percent, is_trend, avg_score):
        etd = datetime.now().strftime('%Y-%m-%d')
        mycursor = self.MYSQL_DB.cursor()
        sql = f"select id,on_price from tbt_subscribe where symbol='{symbol}' and is_activate=1"
        mycursor.execute(sql)
        myresult = mycursor.fetchone()

        sql = f"""INSERT INTO tbt_subscribe (id,etd,symbol,on_price,on_percent,last_price,percent_change,is_activate, is_trend, avg_score,created_on,last_update) VALUES (uuid(),current_timestamp,'{symbol}', '{price}','{percent}','{price}', '{percent}', {is_trend}, {is_trend}, {avg_score},current_timestamp, current_timestamp)"""
        if myresult != None:
            is_stats = 0
            if price > float(myresult[1]):
                is_stats = 1
                
            sql = f"""update tbt_subscribe set 
            last_price='{price}',
            percent_change='{percent}',
            is_activate={is_stats},
            is_trend={is_stats},
            avg_score={avg_score},
            last_update=current_timestamp
            where id='{myresult[0]}'"""

        mycursor.execute(sql)
        self.MYSQL_DB.commit()
        print(self.MYSQL_DB)