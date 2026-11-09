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
    
    # 版本內排程的玩法：公告寫「將於X月X日更新」，年份有時會寫、有時不寫
    SCHEDULED_EVENTS = [
        ("幻想真境劇詩 更新", r"幻想真境劇詩將於(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日"),
        ("深境螺旋 更新", r"深境螺旋將於(?:(\d{4})年)?(\d{1,2})月(\d{1,2})日"),
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

        # 1. 版本更新
        for d in re.findall(r"〓更新時間〓\s*(\d{4}/\d{2}/\d{2})", content_text):
            try:
                version_date = datetime.strptime(d, "%Y/%m/%d")
            except ValueError:
                print(f"Genshin 日期格式錯誤，已略過：{d}")
                continue
            all_matches.append({
                "game": "原神",
                "title": clean_title + " 更新",
                "dates": version_date.strftime("%Y-%m-%d"),
                "image": img_url,
            })

        if version_date:
            second_half_date = version_date + timedelta(days=20)
            second_half_title = clean_title.replace("更新", "").strip() + " 下半池"
            all_matches.append({
                "game": "原神",
                "title": second_half_title,
                "dates": second_half_date.strftime("%Y-%m-%d"),
                "image": None
            })  

        # 2. 幻想真境劇詩、深境螺旋
        for title, pattern in SCHEDULED_EVENTS:
            for year, month, day in re.findall(pattern, content_text):
                month, day = int(month), int(day)
                if year:
                    year = int(year)
                elif version_date:
                    # 公告只寫「X月X日」：月份比版本月份小代表跨年（例如 12 月版本、1 月螺旋）
                    year = version_date.year + (1 if month < version_date.month else 0)
                else:
                    continue
                try:
                    dt = datetime(year=year, month=month, day=day)
                except ValueError:
                    print(f"Genshin {title}日期錯誤，已略過：{month}月{day}日")
                    continue
                all_matches.append({
                    "game": "原神",
                    "title": title,
                    "dates": dt.strftime("%Y-%m-%d"),
                    "image": None
                })

    return all_matches

if __name__ == "__main__":
    print(fetch_genshin())