# api/update.py
import main

def handler(request):
    try:
        main.generate_events()
        return {
            "statusCode": 200,
            "body": "✅ events.json 已更新"
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": f"❌ 更新失敗: {str(e)}"
        }