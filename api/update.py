import os
import sys
import json

# 修正路徑問題
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main

def handler(request):
    # 這裡確保能同時處理 GET 或 POST
    # 如果你只是要拿資料，其實用 GET 就夠了
    
    try:
        # 執行爬蟲邏輯
        data = main.fetch_all()
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "GET, POST, OPTIONS"
            },
            "body": json.dumps(data, ensure_ascii=False)
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": { "Content-Type": "application/json" },
            "body": json.dumps({"error": str(e)}, ensure_ascii=False)
        }