import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database import save_draw

LATEST_URL = "https://lotto.auzonet.com/bingobingoV1.php"
HISTORY_URL = "https://www.pilio.idv.tw/bingo/list_history.asp"

def fetch_latest():
    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(
        LATEST_URL,
        headers=headers,
        timeout=15
    )

    r.encoding = "utf-8"

    soup = BeautifulSoup(r.text, "lxml")
    text = soup.get_text(" ", strip=True)

    pattern = re.compile(
        r"(115\d{6})\s+(\d{2}:\d{2})\s+"
        r"((?:\d{1,2}\s+){20})(\d{1,2})"
    )

    rows = []

    for m in pattern.finditer(text):
        period = m.group(1)
        draw_time = m.group(2)
        nums = [int(x) for x in re.findall(r"\d{1,2}", m.group(3))]
        super_num = int(m.group(4))

        if len(nums) == 20:
            rows.append({
                "period": period,
                "draw_time": draw_time,
                "nums": nums,
                "super_num": super_num
            })

    return rows

def update_latest():
    rows = fetch_latest()

    for r in rows:
        save_draw(
            r["period"],
            r["draw_time"],
            r["nums"],
            r["super_num"]
        )

    return len(rows)

def fetch_history_by_date(date_obj):
    """
    抓指定日期歷史資料。
    若網站格式不同，會回傳空 list，不會讓整個網站壞掉。
    """
    headers = {"User-Agent": "Mozilla/5.0"}

    date_formats = [
        date_obj.strftime("%Y/%m/%d"),
        date_obj.strftime("%Y-%m-%d"),
        date_obj.strftime("%Y%m%d"),
    ]

    all_rows = []

    for date_str in date_formats:
        try:
            params = {
                "indexpage": "1",
                "orderby": "old",
                "date": date_str
            }

            r = requests.get(
                HISTORY_URL,
                headers=headers,
                params=params,
                timeout=15
            )

            r.encoding = "utf-8"

            soup = BeautifulSoup(r.text, "lxml")
            text = soup.get_text(" ", strip=True)

            rows = parse_history_text(text)

            if rows:
                all_rows.extend(rows)
                break

        except Exception:
            continue

    return all_rows

def parse_history_text(text):
    rows = []

    # 格式 1：接近使用者常貼的格式
    pattern1 = re.compile(
        r"期別[:：]?\s*(\d{8,9}).*?"
        r"((?:\d{1,2}[,，、\s]+){19}\d{1,2}).*?"
        r"超級獎號[:：]?\s*(\d{1,2}).*?"
        r"(\d{2}:\d{2})",
        re.S
    )

    for m in pattern1.finditer(text):
        period = m.group(1)
        nums = [int(x) for x in re.findall(r"\d{1,2}", m.group(2))]
        super_num = int(m.group(3))
        draw_time = m.group(4)

        if len(nums) == 20:
            rows.append({
                "period": period,
                "draw_time": draw_time,
                "nums": nums,
                "super_num": super_num
            })

    if rows:
        return rows

    # 格式 2：表格純文字格式
    pattern2 = re.compile(
        r"(115\d{6})\s+(\d{2}:\d{2})\s+"
        r"((?:\d{1,2}\s+){20})(\d{1,2})"
    )

    for m in pattern2.finditer(text):
        period = m.group(1)
        draw_time = m.group(2)
        nums = [int(x) for x in re.findall(r"\d{1,2}", m.group(3))]
        super_num = int(m.group(4))

        if len(nums) == 20:
            rows.append({
                "period": period,
                "draw_time": draw_time,
                "nums": nums,
                "super_num": super_num
            })

    return rows

def update_history_days(days=7):
    total = 0
    today = datetime.now().date()

    for i in range(days):
        day = today - timedelta(days=i)

        rows = fetch_history_by_date(day)

        for r in rows:
            save_draw(
                r["period"],
                r["draw_time"],
                r["nums"],
                r["super_num"]
            )

        total += len(rows)

    return total