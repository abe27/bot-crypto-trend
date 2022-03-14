import os
import uuid
import mysql.connector

class MysqlService:
    def __init__(self):
        self.MYSQL_DB = mysql.connector.connect(host=os.getenv('MYSQL_HOST'),
                               user=os.getenv('MYSQL_USER'),
                               password=os.getenv('MYSQL_PASSWORD'),
                               database=os.getenv('MYSQL_DBNAME'))
        
    def insert(self, symbol='None', price=0, percent=0, is_trend=1, avg_score=0):
        # etd = datetime.now().strftime('%Y-%m-%d')
        mycursor = self.MYSQL_DB.cursor()
        sql = f"select id,on_price from tbt_subscribe where symbol='{symbol}' and is_activate=1"
        mycursor.execute(sql)
        myresult = mycursor.fetchone()

        sql = f"""INSERT INTO tbt_subscribe(id,etd,symbol,on_price,on_percent,last_price,percent_change,is_activate, is_trend, avg_score,created_on,last_update) VALUES ('{str(uuid.uuid4())}',current_timestamp,'{symbol}', '{price}','{percent}','{price}', '{percent}', 1, {is_trend}, {avg_score},current_timestamp, current_timestamp)"""
        if myresult is None:
            mycursor.execute(sql)
            self.MYSQL_DB.commit()
        
        print(f'insert db :=> {symbol}')
        return True
        
    def update(self, symbol='None', price=0, percent=0, avg_score=0, up_price=False):
        mycursor = self.MYSQL_DB.cursor()
        sql = f"select id,on_price from tbt_subscribe where symbol='{symbol}' and is_activate=1"
        mycursor.execute(sql)
        myresult = mycursor.fetchone()
        txt = 'price'
        if myresult != None:
            sql = f"""update tbt_subscribe set 
                last_price='{price}',
                percent_change='{percent}',
                last_update=current_timestamp
                where id='{myresult[0]}'"""
                
            if up_price:
                is_stats = 1
                txt = 'update order'
                ## ตรวจเปอร์เซ็นต์สูงสุดตามกำหนดในนี้กำหนดที่ 4%
                ## ถ้าตรงตามเงื่อนไขให้ทำการปิดออร์เดอร์ในทันที
                if percent >= 4:
                    is_stats = 0
                    txt = 'close order'
                    
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
            print(f'update {txt} {symbol}:=> {myresult[0]}')
        return True
        