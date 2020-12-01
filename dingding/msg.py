import requests
import json
def send_msg(text):
    headers = {'Content-Type': 'application/json;charset=utf-8'}
    api_url = "https://oapi.dingtalk.com/robot/send?access_token=219216f8e47df88e102c91d545fb24fe55ba996ae9b51a05568698f91ce4b827" #jump
    # api_url = "https://oapi.dingtalk.com/robot/send?access_token=b905ca4350378328948b4a3eaa7dd0a91f442ef05ee9545c600268a4c690b374"
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
