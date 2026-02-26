import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup

def fetch_starrail():
    url = "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/113fe6d3b4514cdd/getContentList"
    params = {
        "iPageSize": 5, # 抓最近 5 則，通常就包含最新的版本更新說明
        "sLangKey": "zh-tw",
        "isPreview": 0,
        "iChanId": 250,
        "iPage": 1
    }

    try:
        # 設定 timeout 防止 API 沒反應拖垮整個部署
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

        # 清洗標題，例如 "2.1版本「深淵到彼端」版本更新說明" -> "2.1版本更新說明"
        clean_title = raw_title.replace("說明", "").strip()
        
        # 轉成純文字，讓正規表示式更好抓
        content_text = BeautifulSoup(post["sContent"], "html.parser").get_text(separator="\n")

        # ===== 1. 版本更新時間 =====
        # 鐵道的公告通常是：■更新時間 2024/03/27 06:00
        matches = re.findall(r"■更新時間\s*(\d{4}/\d{2}/\d{2})", content_text)
        for d in matches:
            dt = datetime.strptime(d, "%Y/%m/%d")
            all_matches.append({
                "game": "鐵道",
                "title": clean_title,
                "dates": dt.strftime("%Y-%m-%d")
            })

        # ===== 2. 高難副本（虛構、混沌、末日）=====
        # 鐵道公告會列出後續好幾個版本的內容
        dungeon_matches = re.findall(
            r"(虛構敘事[•·][^ \n]+|混沌回憶[•·][^ \n]+|末日幻影[•·][^ \n]+)[\s\S]*?(\d{4}/\d{2}/\d{2})",
            content_text
        )

        for dungeon, d in dungeon_matches:
            dt = datetime.strptime(d, "%Y/%m/%d")
            all_matches.append({
                "game": "鐵道",
                "title": dungeon.strip(),
                "dates": dt.strftime("%Y-%m-%d")
            })

    return all_matches