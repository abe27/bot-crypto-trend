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
    Logging(symbol='SUBSCRIBE', msg=f"RUN AT: {server_time['timestamp']}")
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    # update subscribe
    mycursor = mydb.MYSQL_DB.cursor()
    sql = f"select symbol  from tbt_subscribe where is_activate=1 order by symbol "
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for i in myresult:
        print(colored(f"start subscribe loop {i[0]}", "blue"))
        x = bitkub.check_subscibe(symbol=i[0])
        ## update last price and check trend
        mydb.update(symbol=x['symbol'],
                        price=x['price'],
                        percent=x['percent'],
                        up_price=x['close'])

    server_time = bitkub.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}",
                "red"))
    print("******************************")
    Logging(symbol='SUBSCRIBE', msg=f"END AT: {server_time['timestamp']}")


if __name__ == '__main__':
    main()
    sys.exit(0)
