import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_genshin():
    url = "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/a1b1f9d3315447cc/getContentList"
    params = {
        "iAppId": 32,
        "iChanId": 397,
        "iPageSize": 5,  # 抓最近的 5 則公告通常就夠了
        "iPage": 1,
        "sLangKey": "zh-tw"
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        data = res.json()
        posts = data.get("data", {}).get("list", [])
    except Exception as e:
        print(f"Genshin API Error: {e}")
        return []

    all_matches = []
    
    # 預期匹配規則
    EVENT_PATTERNS = [
        {"title": "版本更新", "regex": r"更新時間[：\s]*(\d{4}/\d{2}/\d{2})", "fmt": "%Y/%m/%d"},
        {"title": "幻想真境劇詩", "regex": r"幻想真境劇詩將於(\d{4}年\d{1,2}月\d{1,2}日)", "fmt": "%Y年%m月%d日"}
    ]

    for post in posts:
        raw_title = post["sTitle"]
        # 先用 BeautifulSoup 轉純文字，避免 HTML 標籤干擾正則
        content_text = BeautifulSoup(post["sContent"], "html.parser").get_text()
        
        clean_title = raw_title.split("更")[0].strip()
        version_date = None

        # 1. 抓版本更新與劇詩
        for rule in EVENT_PATTERNS:
            matches = re.findall(rule["regex"], content_text)
            for d in matches:
                try:
                    dt = datetime.strptime(d, rule["fmt"])
                    if rule["title"] == "版本更新":
                        version_date = dt
                    
                    all_matches.append({
                        "game": "原神",
                        "title": clean_title if rule["title"] == "版本更新" else rule["title"],
                        "dates": dt.strftime("%Y-%m-%d")
                    })
                except: continue

        # 2. 抓深境螺旋 (依賴上面抓到的 version_date 年份)
        spiral_matches = re.findall(r"深境螺旋將於(\d{1,2})月(\d{1,2})日更新", content_text)
        for month, day in spiral_matches:
            if version_date:
                # 假設螺旋跟版本更新是在同一年
                dt = datetime(year=version_date.year, month=int(month), day=int(day))
                all_matches.append({
                    "game": "原神",
                    "title": "深境螺旋",
                    "dates": dt.strftime("%Y-%m-%d")
                })

    return all_matches