import requests
import re
from datetime import datetime

url = "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/113fe6d3b4514cdd/getContentList"
params = {
    "iPageSize": 10,
    "sLangKey": "zh-tw",
    "isPreview": 0,
    "iChanId": 250
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

for post in all_posts:
    raw_title = post["sTitle"]

    if "版本更新說明" not in raw_title:
        continue

    content = post["sContent"]

    clean_title = raw_title.split("版")[0] + "版" + raw_title.split("版")[1]

    # ===== 版本更新 =====
    matches = re.findall(
        r"(?:■更新時間)</p><p[^>]*>(\d{4}/\d{2}/\d{2})",
        content
    )

    for d in matches:
        dt = datetime.strptime(d, "%Y/%m/%d")

        all_matches.append({
            "game": "鐵道",
            "title": clean_title,
            "dates": dt.strftime("%Y-%m-%d")
        })

    # ===== 高難副本（虛構敘事 / 混沌回憶 / 末日幻影）=====
    dungeon_matches = re.findall(
        r"(虛構敘事•[^\n<]+|混沌回憶•[^\n<]+|末日幻影•[^\n<]+)[\s\S]*?(\d{4}/\d{2}/\d{2})",
        content
    )

    for dungeon, d in dungeon_matches:
        dt = datetime.strptime(d, "%Y/%m/%d")

        all_matches.append({
            "game": "鐵道",
            "title": dungeon,
            "dates": dt.strftime("%Y-%m-%d")
        })

'''
import json
print(json.dumps(all_matches, ensure_ascii=False, indent=2))
'''

def fetch_starrail():
    return all_matches