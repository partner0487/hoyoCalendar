import json
from concurrent.futures import ThreadPoolExecutor
from genshin import fetch_genshin
from starrail import fetch_starrail
from ww import fetch_ww
from nte import fetch_nte


FETCHERS = [
    ("原神", fetch_genshin),
    ("鐵道", fetch_starrail),
    ("鳴潮", fetch_ww),
    ("異環", fetch_nte),
]


def _safe_fetch(name, fetch):
    # 每個遊戲各自處理錯誤：其中一個官網改版壞掉，其他遊戲仍能正常顯示
    try:
        return fetch()
    except Exception as e:
        print(f"{name} 抓取失敗，已略過：{e}")
        return []


def fetch_all():
    # 四個遊戲同時抓，總時間約等於最慢的那一個，而不是全部相加
    with ThreadPoolExecutor(max_workers=len(FETCHERS)) as pool:
        futures = [pool.submit(_safe_fetch, name, fetch) for name, fetch in FETCHERS]
        results = []
        for f in futures:  # 依 FETCHERS 順序合併，輸出順序跟以前一樣
            results.extend(f.result())

    return results

def generate_events():
    data = fetch_all()

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ events.json 已更新")

if __name__ == "__main__":
    generate_events()