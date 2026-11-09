import requests
import re
import json
from datetime import datetime, timedelta
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
        version_matches = re.findall(
            r"■更新時間\s*(\d{4}/\d{2}/\d{2})",
            content_text
        )

        version_date = None

        for d in version_matches:
            version_date = datetime.strptime(d, "%Y/%m/%d")

            all_matches.append({
                "game": "鐵道",
                "title": clean_title,
                "dates": version_date.strftime("%Y-%m-%d"),
                "image": img_url
            })

            # 下半池
            second_half_date = version_date + timedelta(days=20)

            all_matches.append({
                "game": "鐵道",
                "title": clean_title.replace("更新", "").strip() + " 下半池",
                "dates": second_half_date.strftime("%Y-%m-%d"),
                "image": None
            })

        # ===== 2. 版本更新後立即開啟的副本 =====
        version_after_matches = re.findall(
            r"「([^」]+)」\s*將於\s*\d+(?:\.\d+)?版本更新後開啟",
            content_text
        )

        handled_dungeons = set()

        if version_date:
            for dungeon in version_after_matches:
                handled_dungeons.add(dungeon)

                all_matches.append({
                    "game": "鐵道",
                    "title": dungeon.strip(),
                    "dates": version_date.strftime("%Y-%m-%d"),
                    "image": None
                })

        # ===== 3. 其他副本日期 =====
        dungeon_matches = re.findall(
            r"(虛構敘事[•·][^\s\n]+|"
            r"混沌回憶[•·][^\s\n]+|"
            r"末日幻影[•·][^\s\n]+)"
            r"[\s\S]*?(\d{4}/\d{2}/\d{2})",
            content_text
        )

        for dungeon, d in dungeon_matches:

            # 避免已經使用版本更新日期的副本再次被加入
            if dungeon.strip() in handled_dungeons:
                continue

            dt = datetime.strptime(d, "%Y/%m/%d")

            all_matches.append({
                "game": "鐵道",
                "title": dungeon.strip(),
                "dates": dt.strftime("%Y-%m-%d"),
                "image": None
            })

    return all_matches