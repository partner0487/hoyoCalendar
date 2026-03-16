import json
from genshin import fetch_genshin
from starrail import fetch_starrail
from ww import fetch_ww

def fetch_all():
    results = []

    results.extend(fetch_genshin())
    results.extend(fetch_starrail())
    results.extend(fetch_ww())

    return results


def generate_events():
    data = fetch_all()

    with open("events.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("✅ events.json 已更新")


if __name__ == "__main__":
    generate_events()