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

try:
    with open("history.csv", 'r', encoding='utf-8') as file:
        reader = csv.reader(file)
        lines = list(reader)
except Exception as e:
    print(f"發生錯誤{e}")


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
    if reply_message == "最近":
        reply_message = return_recent()
    else :
        user_message = user_message.replace(","," ").split()
        if len(user_message)>1:
            result = return_pair(user_message)
            reply_message = result if result else reply_message
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_message)
    )
def return_recent():
    try:
        result = lines[-5:]
        reply_message = ""
        for row in result:
            reply_message += row[1] +"("+ row[0] +"期)\n"
            reply_message += row[2] + ","+row[3] + ","+row[4] + ","+row[5] + ","+row[6]+"\n"
        return reply_message
    except Exception as e:
        return f"發生錯誤"

def return_pair(pair):
    specified_numbers = []
    try:
        for i in pair:
            specified_numbers.append(int(i))
        matching_periods = []
        for i in range(1,len(lines) - 1):
            current_record = lines[i]
            next_record = lines[i + 1]

            current_numbers = list(map(int, current_record[2:7]))
            next_numbers = list(map(int, next_record[2:7]))

            if all(number in current_numbers for number in specified_numbers) :
                matching_periods.append((current_record[0:7], next_record[0:7]))
        reply_message = ""
        for current_period, next_period in matching_periods[min(-40,len(matching_periods)):]:
            reply_message += current_period[1] + "(" + current_period[0] + "期)\n"
            reply_message += current_period[2] + "," + current_period[3] + "," + current_period[4] + "," + current_period[5] + "," + current_period[6] + "\n"
            reply_message += next_period[1] + "(" + next_period[0] + "期)\n"
            reply_message += next_period[2] + "," + next_period[3] + "," + next_period[4] + "," + next_period[5] + "," + next_period[6] + "\n"
            reply_message+="===================\n"
        
        return reply_message
    except Exception as e:
        return f"發生錯誤{e}"




if __name__ == "__main__":
    app.run()
