import os
import requests
import urllib.parse


class Notification:
    # def __init__(self, msg, token):
    #     self.__LINE_TOKEN__ = token

    def line(self, msg, token):
        url = "https://notify-api.line.me/api/notify"
        txt = f"{msg}\nจากระบบ: {os.getenv('APP_NAME')}"
        payload = urllib.parse.urlencode({"message": (txt).encode('utf-8')})
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        print(response.text)
