import requests
import re
import json
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_starrail():
    url = "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/113fe6d3b4514cdd/getContentList"
    params = {
        "iPageSize": 5,
        "sLangKey": "zh-tw",
        "isPreview": 0,
        "iChanId": 250,
        "iPage": 1
    }

    try:
        data = requests.get(url, params=params, timeout=10).json()
        posts = data.get("data", {}).get("list", [])
    except Exception as e:
        print(f"HSR API Error: {e}")
        return []

    all_matches = []

    for post in posts:
        raw_title = post["sTitle"]
        if "版本更新說明" not in raw_title:
            continue

        # ✔ 抓圖片（重點）
        img_url = None
        try:
            ext = json.loads(post.get("sExt", "{}"))
            img_url = ext.get("news-poster", [{}])[0].get("url")
        except:
            pass

        clean_title = raw_title.replace("說明", "").strip()
        
        content_text = BeautifulSoup(
            post["sContent"], "html.parser"
        ).get_text(separator="\n")

        # ===== 1. 版本更新 =====
        matches = re.findall(r"■更新時間\s*(\d{4}/\d{2}/\d{2})", content_text)
        for d in matches:
            dt = datetime.strptime(d, "%Y/%m/%d")
            all_matches.append({
                "game": "鐵道",
                "title": clean_title,
                "dates": dt.strftime("%Y-%m-%d"),
                "image": img_url
            })

        # ===== 2. 副本 =====
        dungeon_matches = re.findall(
            r"(虛構敘事[•·][^ \n]+|混沌回憶[•·][^ \n]+|末日幻影[•·][^ \n]+)[\s\S]*?(\d{4}/\d{2}/\d{2})",
            content_text
        )

        for dungeon, d in dungeon_matches:
            dt = datetime.strptime(d, "%Y/%m/%d")
            all_matches.append({
                "game": "鐵道",
                "title": dungeon.strip(),
                "dates": dt.strftime("%Y-%m-%d"),
                "image": None
            })

    return all_matches