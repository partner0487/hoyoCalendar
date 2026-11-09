import time
import requests, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor

DETAIL_WORKERS = 4  # 同時抓詳細頁的數量，不要開太多以免被官網擋

def get_ww_periodic_events():
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_limit = today + timedelta(days=42)
    
    periodic_configs = [
        {"title": "逆境深塔 更新", "base_date": datetime(2025, 2, 3)},
        {"title": "冥歌海墟 更新", "base_date": datetime(2025, 2, 17)}
    ]
    
    periodic_events = []
    for config in periodic_configs:
        current_pointer = config["base_date"]
        while current_pointer <= end_limit:
            if current_pointer >= today:
                periodic_events.append({
                    "game": "鳴潮",
                    "title": config["title"],
                    "dates": current_pointer.strftime("%Y-%m-%d"),
                    "image": None
                })
            current_pointer += timedelta(days=28) 
            
    return periodic_events

def parse_version_tuple(title):
    match = re.search(r"(\d+)\.(\d+)", title)
    if match:
        return (int(match.group(1)), int(match.group(2)))
    return (0, 0)

def _fetch_version_post(post, headers):
    """抓單篇更新公告的詳細頁，回傳版本與下半卡池事件（失敗回傳空清單）。"""
    clean_title = post['articleTitle'].split('更')[0].split('》')[-1].strip()
    url_detail = f"https://media-cdn-mingchao.kurogame.com/akiwebsite/website2.0/json/G152/zh/article/{post['articleId']}.json"

    det = None
    for _ in range(2):
        try:
            det = requests.get(url_detail, headers=headers, timeout=10).json()
            break
        except Exception:
            time.sleep(0.3)

    if not det:
        return []

    try:
        content = det.get("articleContent", "")
        soup = BeautifulSoup(content, "html.parser")

        text = soup.get_text(separator="\n")
        matches = re.findall(r"✦更新维护时间：\s*(\d{4}年\d{1,2}月\d{1,2}日)", text)
        if not matches:
            # 沒有日期的事件無法放上行事曆（前端會拿到 null）
            print(f"鳴潮公告找不到更新日期，已略過：{post['articleTitle']}")
            return []
        dt = datetime.strptime(matches[0], "%Y年%m月%d日")

        img_url = None
        img_tag = soup.find("img")
        if img_tag and img_tag.get("src"):
            img_url = img_tag["src"]

        second_half_date = dt + timedelta(days=21)
        second_half_title = clean_title.replace("版本", "").strip() + " 下半卡池"
        return [
            {
                "game": "鳴潮",
                "title": clean_title,
                "dates": dt.strftime("%Y-%m-%d"),
                "image": img_url
            },
            {
                "game": "鳴潮",
                "title": second_half_title,
                "dates": second_half_date.strftime("%Y-%m-%d"),
                "image": None
            },
        ]
    except Exception as e:
        print(f"Detail parsing error: {e}")
        return []


def fetch_ww(target_count=7):
    url_list = "https://media-cdn-mingchao.kurogame.com/akiwebsite/website2.0/json/G152/zh/ArticleMenu.json"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://mingchao.kurogame.com/"
    }

    try:
        posts = requests.get(url_list, headers=headers, timeout=15).json()
    except Exception as e:
        print(f"Fetch list failed: {e}")
        return []

    # 1. 篩選出所有更新維護公告
    all_version_posts = [
        p for p in posts
        if re.search(r"\d+\.\d+", p.get("articleTitle", "")) and "更新维护预告" in p.get("articleTitle", "")
    ]

    # 2. 依照版本號進行數字排序（例如 3.6 > 3.5 > 3.4 ...），不受 JSON 原始順序影響
    all_version_posts.sort(key=lambda x: parse_version_tuple(x.get("articleTitle", "")), reverse=True)

    # 3. 精準只取最新排序的前 target_count 篇
    filtered = all_version_posts[:target_count]

    # 4. 同時抓各篇詳細頁（依序抓每篇要等前一篇，7 篇加起來好幾秒）
    with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as pool:
        per_post = list(pool.map(lambda p: _fetch_version_post(p, headers), filtered))

    results = [event for events in per_post for event in events]

    periodic_events = get_ww_periodic_events()
    results.extend(periodic_events)
    
    return results

if __name__ == "__main__":
    import pprint
    pprint.pprint(fetch_ww())