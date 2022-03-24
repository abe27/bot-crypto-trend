import os
import requests
import urllib.parse


class Notification:
    def __init__(self):
        self.__LINE_TOKEN__ = os.getenv('LINE_NOTI_TOKEN')

    def line(self, msg):
        url = "https://notify-api.line.me/api/notify"
        txt = f"{msg}\nแจ้งเตือนจากระบบ {os.getenv('APP_NAME')}"
        payload = urllib.parse.urlencode({"message": (txt).encode('utf-8')})
        headers = {
            'Authorization': f'Bearer {self.__LINE_TOKEN__}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
