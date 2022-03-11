import os
from dotenv import load_dotenv
load_dotenv()

class BitKub:
    def __init__(self):
        # Initial envs.
        self.API_HOST= os.getenv('BITKUB_HOST')
        self.API_KEY= os.getenv('BITKUB_KEY')
        self.API_SECRET= os.getenv('BITKUB_SECRET')