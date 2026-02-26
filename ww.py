import requests, re
from bs4 import BeautifulSoup
from datetime import datetime

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
        dates = "TBD" 
        
        url_detail = f"https://media-cdn-mingchao.kurogame.com/akiwebsite/website2.0/json/G152/zh/article/{post['articleId']}.json"
        try:
            det = requests.get(url_detail, timeout=10).json()
            content = det.get("articleContent", "")
            soup = BeautifulSoup(content, "html.parser")
            text = soup.get_text(separator="\n")

            matches = re.findall(r"✦更新维护时间：\s*(\d{4}年\d{1,2}月\d{1,2}日)", text)
            if matches:
                dt = datetime.strptime(matches[0], "%Y年%m月%d日")
                dates = dt.strftime("%Y-%m-%d")

            results.append({
                "game": "鳴潮",
                "title": f"{post['articleTitle'].split('更')[0].split('》')[-1]}",
                "dates": dates
            })
        except Exception as e:
            print(f"Detail parsing error: {e}")
            continue
            
    return results