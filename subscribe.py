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
    price = False
    if len(sys.argv) > 1:price = True
    server_time = bitkub.timestamps()
    print(
        colored(f"start run datetime on server: {server_time['datetime']}",
                "red"))
    # update subscribe
    mycursor = mydb.MYSQL_DB.cursor()
    sql = f"select id,symbol,exchange,quotes,last_update from tbt_investments where is_activate=1 order by exchange desc,quotes,last_update"
    mycursor.execute(sql)
    myresult = mycursor.fetchall()
    for i in myresult:
        print(colored(f"start subscribe loop {i[0]}", "blue"))
        mydb.update(key_id=i[0], symbol=i[1], exchange=i[2], quotes=i[3], update_price=price)

    server_time = bitkub.timestamps()
    print(
        colored(f"end run datetime on server: {server_time['datetime']}",
                "red"))
    print("******************************")


if __name__ == '__main__':
    main()
    sys.exit(0)
