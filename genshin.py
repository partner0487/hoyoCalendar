import requests
import re
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

def fetch_genshin():
    url = "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/a1b1f9d3315447cc/getContentList"
    params = {
        "iAppId": 32,
        "iChanId": 397,
        "iPageSize": 5,
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
    
    EVENT_PATTERNS = [
        {
            "title": "版本更新",
            "regex": r"〓更新時間〓\s*(\d{4}/\d{2}/\d{2})",
            "fmt": "%Y/%m/%d"
        },
        {
            "title": "幻想真境劇詩 更新", 
            "regex": r"幻想真境劇詩將於(\d{4}年\d{1,2}月\d{1,2}日)", 
            "fmt": "%Y年%m月%d日"
        }
    ]

    for post in posts:
        raw_title = post.get("sTitle") or ""
        raw_content = post.get("sContent") or ""
        if not raw_title or not raw_content:
            continue

        # ✔ 解析圖片 URL（重點）
        img_url = None
        try:
            ext = json.loads(post.get("sExt", "{}"))
            img_url = ext.get("banner", [{}])[0].get("url")
        except (ValueError, TypeError, AttributeError, IndexError) as e:
            print(f"Genshin 圖片解析失敗（{raw_title}）：{e}")

        # HTML → 純文字
        content_text = BeautifulSoup(raw_content, "html.parser").get_text()
        
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
                        "title": clean_title + " 更新" if rule["title"] == "版本更新" else rule["title"],
                        "dates": dt.strftime("%Y-%m-%d"),
                        "image": img_url if rule["title"] == "版本更新" else None,
                    })
                except ValueError:
                    print(f"Genshin 日期格式錯誤，已略過：{d}")
                    continue
        
        if version_date:
            second_half_date = version_date + timedelta(days=20)
            second_half_title = clean_title.replace("更新", "").strip() + " 下半池"
            all_matches.append({
                "game": "原神",
                "title": second_half_title,
                "dates": second_half_date.strftime("%Y-%m-%d"),
                "image": None
            })  

        # 2. 深境螺旋
        spiral_matches = re.findall(r"深境螺旋將於(\d{1,2})月(\d{1,2})日更新", content_text)
        for month, day in spiral_matches:
            if version_date:
                # 公告只寫「X月X日」：月份比版本月份小代表跨年（例如 12 月版本、1 月螺旋）
                year = version_date.year + (1 if int(month) < version_date.month else 0)
                try:
                    dt = datetime(year=year, month=int(month), day=int(day))
                except ValueError:
                    print(f"Genshin 深境螺旋日期錯誤，已略過：{month}月{day}日")
                    continue
                all_matches.append({
                    "game": "原神",
                    "title": "深境螺旋 更新",
                    "dates": dt.strftime("%Y-%m-%d"),
                    "image": None
                })

    return all_matches

if __name__ == "__main__":
    print(fetch_genshin())