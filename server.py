from flask import Flask, jsonify
import main  # 你的爬蟲程式

app = Flask(__name__)

@app.route("/events.json")
def get_events():
    data = main.fetch_all()  # 包含原神/鐵道/鳴潮
    return jsonify(data)

@app.route("/update", methods=["POST"])
def update_events():
    main.generate_events()  # 執行爬蟲，更新 events.json
    return "✅ events.json 已更新"

if __name__ == "__main__":
    app.run(debug=True)