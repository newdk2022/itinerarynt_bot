import requests
from bs4 import BeautifulSoup
import time


# ========= 共用請求工具 =========

def safe_get(url, headers=None, retries=2):
    headers = headers or {
        "User-Agent": "Mozilla/5.0"
    }

    for i in range(retries):
        try:
            res = requests.get(url, headers=headers, timeout=10)

            if res.status_code == 200:
                return res

        except Exception:
            time.sleep(1)

    return None


# ========= 台南市政府 =========

def get_tainan_schedule():
    url = "https://www.tainan.gov.tw/News.aspx?n=15694&sms=14512"

    res = safe_get(url)
    if not res:
        return []

    soup = BeautifulSoup(res.text, "html.parser")

    data = set()  # 去重用

    # ✔ 優先抓列表結構（最穩）
    items = soup.select(".list-group-item a")

    if not items:
        # fallback：避免結構變動直接死
        items = soup.find_all("a")

    for item in items:
        text = item.get_text(strip=True)

        if text and len(text) > 5:
            data.add(text)

    return list(data)


# ========= 總統府 =========

def get_president_schedule():
    url = "https://www.president.gov.tw/Handler/GetSchedules.ashx"

    res = safe_get(url)

    if not res:
        return []

    try:
        json_data = res.json()
    except:
        return []

    if not isinstance(json_data, list):
        return []

    data = set()

    for item in json_data:
        title = item.get("Title")
        date = item.get("StartDate")

        if title and date:
            data.add(f"{date} {title}")

    return list(data)
