import requests
from bs4 import BeautifulSoup

# 台南市政府行程
def get_tainan_schedule():
    url = "https://www.tainan.gov.tw/News.aspx?n=15694&sms=14512"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")

    data = []
    for item in soup.select(".list-group-item"):
        text = item.get_text(strip=True)
        if text:
            data.append(text)

    return data


# 總統府行程（API）
def get_president_schedule():
    url = "https://www.president.gov.tw/Handler/GetSchedules.ashx"
    res = requests.get(url)
    json_data = res.json()

    data = []
    for item in json_data:
        title = item.get("Title", "")
        date = item.get("StartDate", "")
        data.append(f"{date} {title}")

    return data
