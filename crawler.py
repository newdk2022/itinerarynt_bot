import requests
from bs4 import BeautifulSoup

# ========= 台南市政府 =========

def get_tainan_schedule():
    url = "https://www.tainan.gov.tw/News.aspx?n=15694&sms=14512"
    res = requests.get(url, timeout=10)
    soup = BeautifulSoup(res.text, "html.parser")

    data = []

    # 🔥 改用更通用 selector
    for item in soup.find_all("a"):
        text = item.get_text(strip=True)
        if text and len(text) > 5:
            data.append(text)

    return data


# ========= 總統府 =========

def get_president_schedule():
    url = "https://www.president.gov.tw/Handler/GetSchedules.ashx"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    res = requests.get(url, headers=headers, timeout=10)

    try:
        json_data = res.json()
    except:
        return []

    data = []

    for item in json_data:
        title = item.get("Title")
        date = item.get("StartDate")

        if title and date:
            data.append(f"{date} {title}")

    return data
