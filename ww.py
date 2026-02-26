import requests, re
from bs4 import BeautifulSoup
from datetime import datetime

url_list = "https://media-cdn-mingchao.kurogame.com/akiwebsite/website2.0/json/G152/zh/ArticleMenu.json"
posts = requests.get(url_list).json()

# 篩選版本更新維護預告
filtered = [
    p for p in posts
    if re.search(r"\d+\.\d+", p["articleTitle"]) and "更新维护预告" in p["articleTitle"]
]

results = []

for post in filtered:
    url_detail = f"https://media-cdn-mingchao.kurogame.com/akiwebsite/website2.0/json/G152/zh/article/{post['articleId']}.json"
    det = requests.get(url_detail).json()
    content = det.get("articleContent", "")

    # 解析 HTML
    soup = BeautifulSoup(content, "html.parser")
    text = soup.get_text(separator="\n")  # 把所有文字抽出，不管標籤

    # 用正則抓日期範圍
    matches = re.findall(r"✦更新维护时间：\s*(\d{4}年\d{1,2}月\d{1,2}日)", text)   
    for d in matches:
        dt = datetime.strptime(d, "%Y年%m月%d日")
        dates = dt.strftime("%Y-%m-%d")

    # 加上完整 title
    results.append({
        "game": "鳴潮",
        "title": f"{post['articleTitle'].split('更')[0].split('》')[1]}",
        "dates": dates
    })

def fetch_ww():
    return results