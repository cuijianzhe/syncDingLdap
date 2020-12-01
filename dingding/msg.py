import requests
import json
def send_msg(text):
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    api_url = "https://oapi.dingtalk.com/robot/send?access_token=access_token" #jump
    json_text= {
        "actionCard": {
            "title": "LDAP账号操作通知",
            "text":
             text,
            "hideAvatar": "0",
            "btnOrientation": "0",
            "btns": [
                {
                    "title": "权限系统链接",
                    "actionURL": "http://auth.limixuexi.com/login"
                },
            ]
        },
        "msgtype": "actionCard"
    }
    requests.post(api_url,data=json.dumps(json_text),headers=headers).json()
