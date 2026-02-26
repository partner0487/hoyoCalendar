import requests
import re
from datetime import datetime

url = "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/a1b1f9d3315447cc/getContentList"
params = {
    "iAppId": 32,
    "iChanId": 397,
    "iPageSize": 10,   # 一頁多抓一點
    "sLangKey": "zh-tw"
}

all_posts = []
page = 1

while True:
    params["iPage"] = page
    data = requests.get(url, params=params).json()

    posts = data["data"]["list"]
    if not posts:
        break   # 👈 沒資料 = 翻完了

    all_posts.extend(posts)
    page += 1
    
all_matches = []
version_date = None

EVENT_PATTERNS = [
    {
        "title": "版本更新",
        "regex": r"(?:〓更新時間〓)</p><p[^>]*>(\d{4}/\d{2}/\d{2})",
        "date_fmt": "%Y/%m/%d"
    },
    {
        "title": "幻想真境劇詩",
        "regex": r"幻想真境劇詩將於(\d{4}年\d{1,2}月\d{1,2}日)更新",
        "date_fmt": "%Y年%m月%d日"
    }
]
for post in all_posts:
    raw_title = post["sTitle"]
    content = post["sContent"]

    clean_title = raw_title.split("更")[0]
    version_date = None

    #版本更新 & 劇詩
    for rule in EVENT_PATTERNS:
        matches = re.findall(rule["regex"], content)

        for d in matches:
            dt = datetime.strptime(d, rule["date_fmt"])

            if rule["title"] == "版本更新":
                version_date = dt

            all_matches.append({
                "game": "原神",
                "title": clean_title if rule["title"] == "版本更新" else rule["title"],
                "dates": dt.strftime("%Y-%m-%d")
            })

    #深境螺旋+
    spiral_matches = re.findall(
        r"深境螺旋將於(\d{1,2})月(\d{1,2})日更新",
        content
    )

    for month, day in spiral_matches:
        if version_date is None:
            continue

        dt = datetime(
            year=version_date.year,
            month=int(month),
            day=int(day)
        )

        all_matches.append({
            "game": "原神",
            "title": "深境螺旋",
            "dates": dt.strftime("%Y-%m-%d")
        })
'''
import json
print(json.dumps(all_matches, ensure_ascii=False, indent=2))
'''
def fetch_genshin():
    return all_matches