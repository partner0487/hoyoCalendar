import json
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


def fetch_all():
    results = []

    # 每個遊戲各自處理錯誤：其中一個官網改版壞掉，其他遊戲仍能正常顯示
    for name, fetch in FETCHERS:
        try:
            results.extend(fetch())
        except Exception as e:
            print(f"{name} 抓取失敗，已略過：{e}")

    return results

def generate_events():
    data = fetch_all()

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ events.json 已更新")

if __name__ == "__main__":
    generate_events()