# api/update.py
import json
import traceback
from http.server import BaseHTTPRequestHandler
from main import fetch_all

# 讓 Vercel CDN 快取成功的結果 10 分鐘，期間內的請求不會再去爬官網；
# 過期後的一天內先回舊資料、背景再更新。避免有人狂打 API 消耗額度或讓官網封鎖 Vercel IP。
CACHE_OK = "public, max-age=0, s-maxage=600, stale-while-revalidate=86400"


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            data = fetch_all()
            self._send(200, data, CACHE_OK)
        except Exception:
            # 細節只記在 Vercel log，不回傳給前端，避免洩漏內部路徑或錯誤內容
            traceback.print_exc()
            self._send(500, {"error": "資料抓取失敗，請稍後再試"}, "no-store")

    def _send(self, status, body, cache_control):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", cache_control)
        self.end_headers()
        self.wfile.write(json.dumps(body, ensure_ascii=False).encode("utf-8"))
