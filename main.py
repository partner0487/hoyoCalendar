# main.py
import json
from genshin import fetch_genshin
from starrail import fetch_starrail
from ww import fetch_ww

def fetch_all():
    # 同時調用三個抓取函式
    results = []
    results.extend(fetch_genshin())
    results.extend(fetch_starrail())
    results.extend(fetch_ww())
    
    # 這裡可以按日期排序 (Optional)
    # results.sort(key=lambda x: x['dates'])
    
    return results

def json_dumps(data):
    return json.dumps(data, ensure_ascii=False)