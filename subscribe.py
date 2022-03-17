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
    # Logging(symbol='ORDER', msg=f"RUN AT: {server_time['timestamp']}")
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    
    server_time = bitkub.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}",
                "red"))
    print("******************************")
    # Logging(symbol='ORDER', msg=f"END AT: {server_time['timestamp']}")
    
def subscribe():
    server_time = bitkub.timestamps()
    Logging(symbol='SUBSCRIBE', msg=f"RUN AT: {server_time['timestamp']}")
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    # update subscribe
    mycursor = mydb.MYSQL_DB.cursor()
    sql = f"select symbol  from tbt_investments where is_activate=1 group by symbol order by symbol"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for i in myresult:
        print(colored(f"start subscribe loop {i[0]}", "blue"))
        mydb.update(symbol=i[0])

    server_time = bitkub.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}",
                "red"))
    print("******************************")
    Logging(symbol='SUBSCRIBE', msg=f"END AT: {server_time['timestamp']}")


if __name__ == '__main__':
    main()
    subscribe()
    sys.exit(0)
