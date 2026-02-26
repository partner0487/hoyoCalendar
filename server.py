from flask import Flask, jsonify
import subprocess
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ⭐ 關鍵一行

@app.route("/update", methods=["POST"])
def update_calendar():
    try:
        # 執行 main.py
        subprocess.run(
            ["python", "main.py"],
            check=True
        )
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "msg": str(e)}), 500

if __name__ == "__main__":
    app.run(port=5000, debug=True)