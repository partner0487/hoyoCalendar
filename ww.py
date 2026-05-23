import requests, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

def get_ww_periodic_events():
    # 1. 定義今天與 42 天後的限制範圍
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_limit = today + timedelta(days=42)
    
    # 2. 定義兩個副本的名稱與各自的歷史第一次更新日
    periodic_configs = [
        {"title": "逆境深塔 更新", "base_date": datetime(2025, 2, 3)},
        {"title": "冥歌海墟 更新", "base_date": datetime(2025, 2, 17)}
    ]
    
    periodic_events = []
    
    # 3. 依據設定檔進行 28 天滾動推算
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
    try:
        posts = requests.get(url_list, timeout=10).json()
    except Exception as e:
        print(f"Fetch list failed: {e}")
        return []

    filtered = [
        p for p in posts
        if re.search(r"\d+\.\d+", p["articleTitle"]) and "更新维护预告" in p["articleTitle"]
    ]

    results = []
    for post in filtered:
        dates = None
        img_url = None
        # 例如從「《鳴潮》1.1版本「XXX」更新維護預告」切出「1.1版本「XXX」」
        clean_title = post['articleTitle'].split('更')[0].split('》')[-1].strip()
        
        url_detail = f"https://media-cdn-mingchao.kurogame.com/akiwebsite/website2.0/json/G152/zh/article/{post['articleId']}.json"
        try:
            det = requests.get(url_detail, timeout=10).json()
            content = det.get("articleContent", "")
            soup = BeautifulSoup(content, "html.parser")
            
            # 抓文字日期
            text = soup.get_text(separator="\n")
            matches = re.findall(r"✦更新维护时间：\s*(\d{4}年\d{1,2}月\d{1,2}日)", text)
            
            dt = None
            if matches:
                dt = datetime.strptime(matches[0], "%Y年%m月%d日")
                dates = dt.strftime("%Y-%m-%d")
            
            # 抓文章裡第一張圖片
            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                img_url = img_tag["src"]

            # 放入版本更新主事件 (移除原本結尾多加的 " 更新")
            results.append({
                "game": "鳴潮",
                "title": clean_title,
                "dates": dates,
                "image": img_url
            })
            
            # 推算下半卡池
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
            
    # ─── 💡 整合：將自動生成的兩個高難度副本事件 extend 進去 ───
    periodic_events = get_ww_periodic_events()
    results.extend(periodic_events)
    # ─────────────────────────────────────────────────────────
    
    return results

if __name__ == "__main__":
    import pprint
    pprint.pprint(fetch_ww())