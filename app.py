from flask import Flask, jsonify, abort
import json, os

app = Flask(__name__)
data_path = os.path.join(os.path.dirname(__file__), "albums.json")
with open(data_path, "r", encoding="utf-8") as f:
    raw = json.load(f)
albums = [{**item, "id": i+1} for i, item in enumerate(raw)]

@app.get("/")
def index():
    return jsonify({"endpoints": ["/albums", "/albums/<id>"], "count": len(albums)})

@app.get("/albums")
def list_albums():
    return jsonify({"count": len(albums), "items": albums})

@app.get("/albums/<int:item_id>")
def get_album(item_id: int):
    for a in albums:
        if a["id"] == item_id:
            return jsonify(a)
    abort(404, description="Album not found")

if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=3000)
