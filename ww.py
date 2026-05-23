import requests, re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

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
        clean_title = post['articleTitle'].split('更')[0].split('》')[-1]
        
        url_detail = f"https://media-cdn-mingchao.kurogame.com/akiwebsite/website2.0/json/G152/zh/article/{post['articleId']}.json"
        try:
            det = requests.get(url_detail, timeout=10).json()
            content = det.get("articleContent", "")
            soup = BeautifulSoup(content, "html.parser")
            
            # 抓文字日期
            text = soup.get_text(separator="\n")
            matches = re.findall(r"✦更新维护时间：\s*(\d{4}年\d{1,2}月\d{1,2}日)", text)
            if matches:
                dt = datetime.strptime(matches[0], "%Y年%m月%d日")
                dates = dt.strftime("%Y-%m-%d")
            
            # 抓文章裡第一張圖片
            img_tag = soup.find("img")
            if img_tag and img_tag.get("src"):
                img_url = img_tag["src"]

            results.append({
                "game": "鳴潮",
                "title": clean_title + " 更新",
                "dates": dates,
                "image": img_url
            })
            
            if dt:
                second_half_date = dt + timedelta(days=21)
                second_half_title = clean_title + " 下半卡池"
                results.append({
                    "game": "鳴潮",
                    "title": second_half_title,
                    "dates": second_half_date.strftime("%Y-%m-%d"),
                    "image": None
                })  
        except Exception as e:
            print(f"Detail parsing error: {e}")
            continue
    
    return results