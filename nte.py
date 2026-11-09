import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
from concurrent.futures import ThreadPoolExecutor

MAX_PAGES = 3  # 每頁約 4 則新聞，3 頁約涵蓋半年的角色卡池
DETAIL_WORKERS = 4  # 同時抓詳細頁圖片的數量，不要開太多以免被官網擋

def get_nte_orbital_events():
    # 1. 最初的起點
    current_pointer = datetime(2026, 5, 7)
    
    # 2. 計算「42天後」作為終點限制
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_limit = today + timedelta(days=42)

    orbital_events = []
    
    while current_pointer <= end_limit:
        orbital_events.append({
                "game": "異環",
                "title": "軌外之境 更新",
                "dates": current_pointer.strftime("%Y-%m-%d"),
                "image": None
            })
        current_pointer += timedelta(days=14)
        
    return orbital_events

def fetch_detail_image(detail_url, headers):
    """
    點進文章詳細頁面，精準抓取新聞大圖，自動排除 LOGO、導覽列等雜訊圖片
    """
    try:
        res = requests.get(detail_url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        
        # 1. 優先從 <picture> 標籤中尋找新聞大圖
        picture_tags = soup.find_all("picture")
        for pic in picture_tags:
            # 尋找電腦版 (desktop) 的 source
            desktop_source = pic.find("source", srcset=re.compile(r"/desktop/"))
            if desktop_source and desktop_source.get("srcset"):
                img_src = desktop_source["srcset"]
                # 確保這不是 logo 或導覽列圖片
                if "logo" not in img_src.lower() and "nav" not in img_src.lower():
                    if img_src.startswith("/"):
                        return "https://nte.iwplay.com.tw" + img_src
                    return img_src

        for img in soup.find_all("img"):
            img_src = img.get("src") or img.get("data-src")
            if not img_src:
                continue
            
            img_src_lower = img_src.lower()
            
            if any(x in img_src_lower for x in ["logo", "nav", "header", "footer", "icon", "aside"]):
                continue
                
            if "cmsnewsimg" in img_src_lower:
                if "/build/" in img_src:
                    img_src = img_src.replace("/build/", "/desktop/")
                if img_src.endswith(".png"):
                    img_src = img_src[:-4] + ".webp"
                
                if img_src.startswith("/"):
                    return "https://nte.iwplay.com.tw" + img_src
                return img_src

    except Exception as e:
        print(f"抓取詳細頁圖片失敗 ({detail_url}): {e}")
    return None

def parse_single_page(soup, headers):
    results = []
    news_elements = soup.find_all("div", class_="latestnews-single")
    
    for element in news_elements:
        title_tag = element.find(class_="latestnews-title")
        title = title_tag.text.strip() if title_tag else ""
        
        date_tag = element.find(class_="newstime")
        date_str = date_tag.text.strip() if date_tag else ""
        
        char_match = re.search(r"角色「([^」]+)」", title)

        if char_match:
            try:
                char_name = char_match.group(1)
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                
                version_match = re.search(r"(\d+\.\d+版本)", title)
                if version_match:
                    version_name = version_match.group(1)
                    clean_title = f"{version_name}「{char_name}」卡池"
                else:
                    clean_title = f"新角色「{char_name}」卡池"

                # 先記下詳細頁網址，圖片之後在 fetch_nte 裡一次同時抓
                detail_url = None
                a_tag = element.find("a", class_="latestnews-titleurl")
                if a_tag and a_tag.get("href"):
                    detail_url = "https://nte.iwplay.com.tw" + a_tag["href"]

                results.append({
                    "game": "異環",
                    "title": clean_title,
                    "dates": dt.strftime("%Y-%m-%d"),
                    "image": None,
                    "_detail_url": detail_url
                })

            except Exception as ex:
                print(f"異環新聞解析出錯: {ex} (標題: {title})")
                continue
                
    return results

def fetch_nte():
    """
    異環資料獲取主入口：爬取前 MAX_PAGES 頁並結合軌外之境日程
    （軌外之境官網不公告，日期由 get_nte_orbital_events 自行推算）
    """
    base_url = "https://nte.iwplay.com.tw/news/"
    first_page_url = f"{base_url}list_1_1.html"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    all_crawled_events = []

    try:
        # 抓取第一頁並動態獲取總頁數
        res = requests.get(first_page_url, headers=headers, timeout=10)
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "html.parser")
        
        total_pages = 1
        pagination = soup.find("div", class_="pagination")
        if pagination:
            page_links = pagination.find_all("a")
            page_numbers = [int(a.text.strip()) for a in page_links if a.text.strip().isdigit()]
            if page_numbers:
                total_pages = max(page_numbers)

        # 角色卡池新聞都在前幾頁；全爬會讓 /api/update 越來越慢，可能超過 Vercel 執行時間上限
        total_pages = min(total_pages, MAX_PAGES)
        print(f"開始爬取《異環》官方新聞前 {total_pages} 頁...")

        # 循環爬取每一頁
        for page in range(1, total_pages + 1):
            page_url = f"{base_url}list_1_{page}.html"
            try:
                if page == 1:
                    page_soup = soup
                else:
                    page_res = requests.get(page_url, headers=headers, timeout=10)
                    page_res.encoding = "utf-8"
                    page_soup = BeautifulSoup(page_res.text, "html.parser")
                
                # 傳入 headers 以利子網頁圖片獲取
                page_data = parse_single_page(page_soup, headers)
                all_crawled_events.extend(page_data)
                
                if page != 1:
                    time.sleep(0.3)  # 避免請求過快
                    
            except Exception as page_err:
                print(f"爬取第 {page} 頁失敗: {page_err}")
                continue

    except Exception as e:
        print(f"Fetch NTE total pages failed: {e}")

    # 同時進每則角色新聞的詳細頁抓大圖（依序抓會一則等一則）
    def fill_image(event):
        detail_url = event.pop("_detail_url", None)
        if detail_url:
            event["image"] = fetch_detail_image(detail_url, headers)

    with ThreadPoolExecutor(max_workers=DETAIL_WORKERS) as pool:
        list(pool.map(fill_image, all_crawled_events))

    # 獲取軌外之境副本更新日期
    orbital_events = get_nte_orbital_events()
    all_crawled_events.extend(orbital_events)

    all_crawled_events.sort(key=lambda x: x["dates"], reverse=True)

    return all_crawled_events

if __name__ == "__main__":
    import pprint
    pprint.pprint(fetch_nte())