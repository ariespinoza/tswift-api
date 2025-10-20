from flask import Flask, jsonify, request, abort
import os, json
from datetime import datetime

app = Flask(__name__)

BASE_DIR = os.path.dirname(__file__)
ALBUMS_PATH = os.path.join(BASE_DIR, "albums.json")
FAVS_PATH   = os.path.join(BASE_DIR, "favorites.json")

def read_json(path, default):
    if not os.path.exists(path):
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default

def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# --------- ÁLBUMES (solo lectura desde albums.json) ----------
@app.get("/albums")
def get_albums():
    raw = read_json(ALBUMS_PATH, [])
    out = []
    for i, a in enumerate(raw, start=1):
        image = a.get("imageName")
        image_arr = image if isinstance(image, list) else ([image] if image else [])
        tracks = a.get("trackList")
        if not isinstance(tracks, list):
            tracks = []
        out.append({
            "id": i,
            "name": a.get("name"),
            "imageName": image_arr,
            "releaseDate": a.get("releaseDate"),
            "trackList": tracks
        })
    return jsonify(out)

@app.get("/albums/<int:album_id>")
def get_album(album_id):
    items = get_albums().json
    for a in items:
        if a["id"] == album_id:
            return jsonify(a)
    abort(404, description="Album not found")

# --------- FAVORITOS (CRUD en favorites.json) ----------
def load_favs():
    data = read_json(FAVS_PATH, [])
    return data if isinstance(data, list) else []

def save_favs(items):
    write_json(FAVS_PATH, items)

def next_id(items):
    return (max((it.get("id", 0) for it in items), default=0) + 1) if items else 1

@app.get("/favorites")
def list_favorites():
    return jsonify(load_favs())

@app.post("/favorites")
def create_favorite():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    artist = (data.get("artist") or "").strip()
    if not name or not artist:
        abort(400, description="Fields 'name' and 'artist' are required")

    items = load_favs()
    new_item = {
        "id": next_id(items),
        "name": name,
        "artist": artist,
        "dateAdded": datetime.utcnow().isoformat(),
        "favoriteSong": data.get("favoriteSong"),
        "listenCompleted": bool(data.get("listenCompleted", False)),
        "commented": bool(data.get("commented", False)),
        "comment": data.get("comment")
    }
    items.append(new_item)
    save_favs(items)
    return jsonify(new_item), 201

@app.patch("/favorites/<int:fav_id>")
def update_favorite(fav_id):
    data = request.get_json(silent=True) or {}
    items = load_favs()
    for it in items:
        if it.get("id") == fav_id:
            if "name" in data and isinstance(data["name"], str) and data["name"].strip():
                it["name"] = data["name"].strip()
            if "artist" in data and isinstance(data["artist"], str) and data["artist"].strip():
                it["artist"] = data["artist"].strip()
            if "favoriteSong" in data: it["favoriteSong"] = data["favoriteSong"]
            if "comment" in data: it["comment"] = data["comment"]
            if "listenCompleted" in data: it["listenCompleted"] = bool(data["listenCompleted"])
            if "commented" in data: it["commented"] = bool(data["commented"])
            save_favs(items)
            return jsonify(it)
    abort(404, description="Favorite not found")

@app.delete("/favorites/<int:fav_id>")
def delete_favorite(fav_id):
    items = load_favs()
    new_items = [it for it in items if it.get("id") != fav_id]
    if len(new_items) == len(items):
        abort(404, description="Favorite not found")
    save_favs(new_items)
    return jsonify({"ok": True, "deletedId": fav_id})

@app.get("/")
def root():
    return jsonify({"ok": True, "mode": "json", "endpoints": ["/albums","/albums/<id>","/favorites"]})

if __name__ == "__main__":
    # Render asigna el puerto en la var PORT; en local puedes ignorarlo
    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
