from genshin import fetch_genshin
from starrail import fetch_starrail
from ww import fetch_ww

all_events = []
all_events.extend(fetch_genshin())
all_events.extend(fetch_starrail())
all_events.extend(fetch_ww())

import json
print(json.dumps(all_events, ensure_ascii=False, indent=2))

with open("events.json", "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)

print("✅ events.json 產生完成")
