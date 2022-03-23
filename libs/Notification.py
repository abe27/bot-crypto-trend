import os
import requests
import urllib.parse


class Notification:
    def __init__(self):
        self.__LINE_TOKEN = os.getenv('LINE_NOTI_TOKEN')

    def line(self, msg):
        url = "https://notify-api.line.me/api/notify"

        payload = urllib.parse.urlencode({"message": (msg).encode('utf-8')})
        headers = {
            'Authorization': f'Bearer {self.__LINE_TOKEN}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
