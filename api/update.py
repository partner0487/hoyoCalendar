# api/update.py
import os
import sys
import json

# --- 關鍵修正：將根目錄加入 Python 搜尋路徑 ---
# 這讓 api/ 內的腳本可以找到根目錄的 main, genshin, starrail, ww
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

import main

def handler(request):
    # 判斷請求方法 (前端是用 POST)
    if request.method != "POST" and request.method != "GET":
        return {
            "statusCode": 405,
            "body": "Method Not Allowed"
        }

    try:
        # 取得最新事件列表
        data = main.fetch_all()
        
        return {
            "statusCode": 200,
            "headers": { 
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, GET, OPTIONS"
            },
            "body": json.dumps(data, ensure_ascii=False)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": { "Content-Type": "application/json" },
            "body": json.dumps({"error": str(e)})
        }