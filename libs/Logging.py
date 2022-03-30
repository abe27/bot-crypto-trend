import os
from datetime import datetime

class Logging:
    def __init__(self, exchange, symbol, msg):
        dte = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        symb = str(f'[{symbol}]').ljust(10)
        txt = f'{dte} {symb} {msg}'
        filename = f'bot-{exchange}-{symbol}-{datetime.now().strftime("%Y-%m-%d")}.log'
        
        if os.path.exists('logs') is False:
            os.mkdir('logs')
            
        full_path = f"logs/{filename}"
        f = open(full_path, 'a')
        f.write(f'{txt}\n')
        f.close()
            
        