import time
import requests, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

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

def fetch_ww():
    url_list = "https://media-cdn-mingchao.kurogame.com/akiwebsite/website2.0/json/G152/zh/ArticleMenu.json"
    
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://mingchao.kurogame.com/"
    })

    try:
        posts = session.get(url_list, timeout=15).json()
    except Exception as e:
        print(f"Fetch list failed: {e}")
        return []

    filtered = [
        p for p in posts
        if re.search(r"\d+\.\d+", p.get("articleTitle", "")) and "更新维护预告" in p.get("articleTitle", "")
    ]

    results = []
    for post in filtered:
        dates = None
        img_url = None
        clean_title = post['articleTitle'].split('更')[0].split('》')[-1].strip()
        url_detail = f"https://media-cdn-mingchao.kurogame.com/akiwebsite/website2.0/json/G152/zh/article/{post['articleId']}.json"
        
        # 加入簡單重試機制
        det = None
        for _ in range(2):
            try:
                time.sleep(0.2)  # 適度間隔
                resp = session.get(url_detail, timeout=15)
                det = resp.json()
                break
            except Exception:
                time.sleep(0.5)

        if not det:
            continue

        try:
            content = det.get("articleContent", "")
            soup = BeautifulSoup(content, "html.parser")
            
            text = soup.get_text(separator="\n")
            matches = re.findall(r"✦更新维护时间：\s*(\d{4}年\d{1,2}月\d{1,2}日)", text)
            
            dt = None
            if matches:
                dt = datetime.strptime(matches[0], "%Y年%m月%d日")
                dates = dt.strftime("%Y-%m-%d")
            
            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                img_url = img_tag["src"]

            results.append({
                "game": "鳴潮",
                "title": clean_title,
                "dates": dates,
                "image": img_url
            })
            
            if dt:
                second_half_date = dt + timedelta(days=21)
                second_half_title = clean_title.replace("版本", "").strip() + " 下半卡池"
                results.append({
                    "game": "鳴潮",
                    "title": second_half_title,
                    "dates": second_half_date.strftime("%Y-%m-%d"),
                    "image": None
                })  
        except Exception as e:
            print(f"Detail parsing error: {e}")
            continue
            
    periodic_events = get_ww_periodic_events()
    results.extend(periodic_events)
    
    return results

if __name__ == "__main__":
    import pprint
    pprint.pprint(fetch_ww())