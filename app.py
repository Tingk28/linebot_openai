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

import threading
import time
import requests
from bs4 import BeautifulSoup

def update(lines):
    print("程式已執行！")
    
    url = "http://www.9800.com.tw/lotto539/statistics.html"  # 替換成你要爬取的網頁的URL

    try:
        response = requests.get(url)
        response.raise_for_status()  # 檢查是否有錯誤的回應

        # 如果回應狀態碼是 200 OK，則解析網頁
        if response.status_code == 200:
            response.encoding = "utf-8"  # 替換成適合的編碼
            soup = BeautifulSoup(response.text, "html.parser")

            # 使用 Beautiful Soup 提取元素
            # 使用 CSS 選擇器選取元素
            tbody_elements = soup.select('table tbody')
            new_data = []
            target_rows = tbody_elements[2].find_all('tr')
            for row in target_rows:
                row_data = []
                td_elements = row.select('td')
                for td in td_elements:
                    text = td.text.replace("\n0","")
                    text = text.replace("\n","").replace("\xa0","").replace("-0","/").replace("-","/")
                    row_data.append(text)
                new_data.append(row_data)
    except requests.exceptions.RequestException as e:
        print("發生錯誤:", e)
    
    new_rows = []
    print(lines[-5:])
    for new_row in new_data:
        new_row_exists = any(new_row == row for row in lines)

        # 如果新行不存在，則將其寫入到 CSV 的最後
        if not new_row_exists:
            print(new_row)
            new_rows.append(new_row)
    print("new_rows")
    print(new_rows)
    # 寫入新行到 history.csv
    if new_rows:
        with open("history.csv", 'a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerows(new_rows)
        print("已寫入新行到 history.csv")
        try:
            with open("history.csv", 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                lines = list(reader)
        except Exception as e:
            print(f"讀取新檔案時發生錯誤{e}")
        return "已寫入新行到 history.csv"
    else:
        print("所有資料均已存在")
        return "所有資料均已存在"

def schedule_thread():
    while True:
        now = time.localtime()
        if now.tm_hour == 20 and now.tm_min >= 35:
            update()
        time.sleep(60)  # 每隔一分鐘檢查一次



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
    elif reply_message == "更新":
        reply_message = update(lines)
    elif "次數" in reply_message:
        reply_message = get_count(reply_message)
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
        if reply_message =="":
            reply_message = "沒有符合的開獎結果"
        return reply_message
    except Exception as e:
        return f"發生錯誤{e}"

def get_count(message):
    from collections import Counter
    from itertools import combinations
    message = message[2:].replace(","," ").split()#去除"次數"兩個字
    specified_numbers = []
    reply_message = ""
    try:
        for i in message:
            specified_numbers.append(int(i))
            matching_periods = []
        for i in range(1,len(lines) - 1):
            current_record = lines[i]
            next_record = lines[i + 1]

            current_numbers = list(map(int, current_record[2:7]))
            next_numbers = list(map(int, next_record[2:7]))

            if all(number in current_numbers for number in specified_numbers) :
                matching_periods.append((current_record[0:7], next_record[0:7]))
        # return reply_message
    except Exception as e:
        return f"發生錯誤{e}"
    
    # 將每一期的數字組合轉換為數字列表
    number_lists = [list(map(int, record[1][2:7])) for record in matching_periods]

    # 用來統計所有倆倆組合中出現的次數
    pair_counter = Counter()

    # 遍歷每一期的數字組合
    for numbers in number_lists:
        # 生成這一期的所有倆倆組合
        pairs = combinations(numbers, 2)

        # 將這一期的組合加入統計
        pair_counter.update(pairs)

    # 將 pair_counter.items() 以出現次數從大到小排序
    sorted_pairs = sorted(pair_counter.items(), key=lambda item: item[1], reverse=True)

    # 輸出排序後的每組組合以及出現次數
    for pair, count in sorted_pairs:
        if count<2:
            break
        reply_message += f"組合 {pair} 出現次數：{count}\n"
    if reply_message == "":
        reply_message = "沒有出現過兩次以上的組合"
    return reply_message


if __name__ == "__main__":
    # 創建一個執行緒來執行 schedule_thread 函數
    thread = threading.Thread(target=schedule_thread)
    thread.daemon = True  # 設定為守護執行緒，程式結束時自動停止執行緒
    thread.start()
    app.run()
