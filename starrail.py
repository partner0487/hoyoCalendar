import requests
import re
import json
from datetime import datetime, timedelta
from bs4 import BeautifulSoup

MAX_VERSIONS = 3  # 只保留最新幾個版本的更新說明
DUNGEON_LINE =re.compile(r"(?:虛構敘事|混沌回憶|末日幻影)[•·][^\s」』，。、]+")


def _parse_date(s):
    """把 'YYYY/MM/DD' 轉成 datetime；公告打錯日期時回傳 None，不讓整個流程崩潰。"""
    try:
        return datetime.strptime(s, "%Y/%m/%d")
    except ValueError:
        print(f"HSR 日期格式錯誤，已略過：{s}")
        return None


def fetch_starrail():
    url = "https://sg-public-api-static.hoyoverse.com/content_v2_user/app/113fe6d3b4514cdd/getContentList"
    params = {
        # 頻道裡也有抽卡機率、服裝等公告，抓多一點避免版本更新說明被擠到第 2 頁
        "iPageSize": 20,
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
    version_posts = 0

    for post in posts:
        raw_title = post.get("sTitle") or ""
        if "版本更新說明" not in raw_title:
            continue
        if version_posts >= MAX_VERSIONS:
            break
        version_posts += 1
        raw_content = post.get("sContent") or ""
        if not raw_content:
            continue

        # ✔ 抓圖片
        img_url = None
        try:
            ext = json.loads(post.get("sExt", "{}"))
            img_url = ext.get("news-poster", [{}])[0].get("url")
        except (ValueError, TypeError, AttributeError, IndexError) as e:
            print(f"HSR 圖片解析失敗（{raw_title}）：{e}")

        clean_title = raw_title.replace("說明", "").strip()
        
        content_text = BeautifulSoup(
            raw_content, "html.parser"
        ).get_text(separator="\n")

        # ===== 1. 版本更新與下半池 =====
        # 只取第一個「■更新時間」，避免同一篇公告重複產生版本 / 下半池事件
        version_match = re.search(
            r"■更新時間\s*(\d{4}/\d{2}/\d{2})",
            content_text
        )
        version_date = _parse_date(version_match.group(1)) if version_match else None

        if version_date:
            all_matches.append({
                "game": "鐵道",
                "title": clean_title,
                "dates": version_date.strftime("%Y-%m-%d"),
                "image": img_url
            })

            # 下半池：版本更新說明裡沒有寫下半池日期，只能用版本日 + 20 天推估
            second_half_date = version_date + timedelta(days=20)

            all_matches.append({
                "game": "鐵道",
                "title": clean_title.replace("更新", "").strip() + " 下半池",
                "dates": second_half_date.strftime("%Y-%m-%d"),
                "image": None
            })

        # ===== 2. 副本日期 =====
        # 公告格式：副本名稱獨佔一行，下一行是開放期間，例如
        #   混沌回憶•來生泅渡
        #   4.6版本更新後 - 2026/11/02 03:59 (伺服器時間)
        #   末日幻影•支配遺忘
        #   2026/10/05 04:00 - 2026/11/16 03:59 (伺服器時間)
        # 只認「整行就是副本名稱」的行，前言句子裡提到的副本不會被誤抓。
        lines = [ln.strip() for ln in content_text.splitlines() if ln.strip()]
        handled_dungeons = set()

        for name, period in zip(lines, lines[1:]):
            if not DUNGEON_LINE.fullmatch(name) or name in handled_dungeons:
                continue

            start = re.match(r"(\d{4}/\d{2}/\d{2})", period)
            if start:
                dt = _parse_date(start.group(1))
            elif "版本更新後" in period:
                dt = version_date
            else:
                dt = None

            if not dt:
                continue

            handled_dungeons.add(name)
            all_matches.append({
                "game": "鐵道",
                "title": name,
                "dates": dt.strftime("%Y-%m-%d"),
                "image": None
            })

    return all_matches

if __name__ == "__main__":
    import pprint
    pprint.pprint(fetch_starrail())