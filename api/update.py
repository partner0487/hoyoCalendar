# api/update.py
import main  # 根目錄的 main.py

def handler(request):
    # 取得最新事件列表
    data = main.fetch_all()  # fetch_genshin + fetch_starrail + fetch_ww
    
    # 直接回傳 JSON 給前端
    return {
        "statusCode": 200,
        "headers": { "Content-Type": "application/json" },
        "body": main.json_dumps(data)  # 使用 main 裡的 json.dumps
    }