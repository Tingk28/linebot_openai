import os,csv
import requests
from bs4 import BeautifulSoup

def update():
    lines = []
    try:
        with open("history.csv", 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            lines = list(reader)
    except Exception as e:
        print(f"發生錯誤{e}")
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
        return "已寫入新行到 history.csv"
    else:
        print("所有資料均已存在")
        return "所有資料均已存在"
        
if __name__ == "__main__":
    update()