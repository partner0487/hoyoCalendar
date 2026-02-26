import json
from genshin import fetch_genshin
from starrail import fetch_starrail
from ww import fetch_ww

def fetch_all():
    return fetch_genshin() + fetch_starrail() + fetch_ww()

def generate_events():
    data = fetch_all()
    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("events.json 產生完成")

if __name__ == "__main__":
    generate_events()