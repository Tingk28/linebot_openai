from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

import os,csv

app = Flask(__name__)

# 替换为你自己的 Channel Access Token 和 Channel Secret
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text
    print(user_message)
    reply_message = user_message
    if user_message == "最近":
        reply_message = return_recent()
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )
def return_recent():
    try:
        with open("history.csv", 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            lines = list(reader)
            result = lines[-5:]
            reply_message = ""
            for row in result:
                row = row.split(",")
                result_message += row[1] +"("+ row[0] +"期)"
                result_message += row[2] + ","+row[3] + ","+row[4] + ","+row[5] + ","+row[6]
            return reply_message
    except Exception as e:
        return f"發生錯誤{e}"


if __name__ == "__main__":
    app.run()
