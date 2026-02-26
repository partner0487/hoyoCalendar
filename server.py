from flask import Flask, jsonify
import main 

app = Flask(__name__)

@app.route("/events.json")
def get_events():
    data = main.fetch_all()
    return jsonify(data)

@app.route("/update", methods=["POST"])
def update_events():
    main.generate_events()
    return "events.json 已更新"

if __name__ == "__main__":
    app.run(debug=True)