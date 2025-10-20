from flask import Flask, jsonify, abort, request
from flask_cors import CORS
from datetime import datetime
import os, json, threading, tempfile, shutil

app = Flask(__name__)
CORS(app)

# ========= Rutas de archivos =========
BASE_DIR = os.path.dirname(__file__)
ALBUMS_PATH = os.path.join(BASE_DIR, "albums.json")
FAVORITES_PATH = os.path.join(BASE_DIR, "favorites.json")

# Lock para operaciones de lectura/escritura de favorites.json
_fav_lock = threading.Lock()

# ========= Utilidades JSON (favoritos) =========
def _read_json(path):
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def _atomic_write_json(path, payload):
    # Escritura atómica: escribe a un temp y luego reemplaza
    dirpath = os.path.dirname(path)
    fd, tmp_path = tempfile.mkstemp(dir=dirpath, prefix=".tmp_", suffix=".json")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as tmp:
            json.dump(payload, tmp, ensure_ascii=False, indent=2)
        # Reemplazo atómico (posix)
        shutil.move(tmp_path, path)
    finally:
        # por si algo falla antes del move
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass

def load_favorites():
    with _fav_lock:
        data = _read_json(FAVORITES_PATH)
        if not isinstance(data, list):
            data = []
        return data

def save_favorites(items):
    with _fav_lock:
        _atomic_write_json(FAVORITES_PATH, items)

def next_id(items):
    # siguiente id = max + 1, o 1 si está vacío
    return (max((it.get("id", 0) for it in items), default=0) + 1) if items else 1

def iso_now():
    return datetime.utcnow().isoformat()

# ========= ÁLBUMES (solo lectura desde albums.json) =========
def load_albums():
    data = _read_json(ALBUMS_PATH)
    # Normalizamos a la forma que ya consume tu app (imageName como arreglo)
    norm = []
    for i, a in enumerate(data, start=1):
        name = a.get("name")
        image = a.get("imageName")
        image_arr = image if isinstance(image, list) else ([image] if image else [])
        track_list = a.get("trackList")
        if not isinstance(track_list, list):
            track_list = []
        norm.append({
            "id": i,  # si tu JSON ya trae id, puedes respetarlo
            "name": name,
            "imageName": image_arr,
            "releaseDate": a.get("releaseDate"),
            "trackList": track_list
        })
    return norm

@app.get("/")
def index():
    return jsonify({
        "ok": True,
        "mode": "JSON storage",
        "endpoints": ["/albums", "/albums/<id>", "/favorites"],
    })

@app.get("/albums")
def list_albums():
    return jsonify(load_albums())

@app.get("/albums/<int:album_id>")
def get_album(album_id):
    for a in load_albums():
        if a["id"] == album_id:
            return jsonify(a)
    abort(404, description="Album not found")

# ========= FAVORITOS (CRUD sobre favorites.json) =========

@app.get("/favorites")
def list_favorites():
    return jsonify(load_favorites())

@app.post("/favorites")
def create_favorite():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    artist = (data.get("artist") or "").strip()
    if not name or not artist:
        abort(400, description="Fields 'name' and 'artist' are required")

    items = load_favorites()
    new_item = {
        "id": next_id(items),
        "name": name,
        "artist": artist,
        "dateAdded": iso_now(),
        "favoriteSong": data.get("favoriteSong"),
        "listenCompleted": bool(data.get("listenCompleted", False)),
        "commented": bool(data.get("commented", False)),
        "comment": data.get("comment")
    }
    items.append(new_item)
    save_favorites(items)
    return jsonify(new_item), 201

@app.patch("/favorites/<int:fav_id>")
@app.put("/favorites/<int:fav_id>")
def update_favorite(fav_id):
    data = request.get_json(silent=True) or {}
    items = load_favorites()
    for it in items:
        if it.get("id") == fav_id:
            # Campos de texto
            if "name" in data and isinstance(data["name"], str) and data["name"].strip():
                it["name"] = data["name"].strip()
            if "artist" in data and isinstance(data["artist"], str) and data["artist"].strip():
                it["artist"] = data["artist"].strip()
            if "favoriteSong" in data:
                it["favoriteSong"] = data["favoriteSong"]
            if "comment" in data:
                it["comment"] = data["comment"]
            # Booleanos
            if "listenCompleted" in data:
                it["listenCompleted"] = bool(data["listenCompleted"])
            if "commented" in data:
                it["commented"] = bool(data["commented"])
            save_favorites(items)
            return jsonify(it)
    abort(404, description="Favorite not found")

@app.delete("/favorites/<int:fav_id>")
def delete_favorite(fav_id):
    items = load_favorites()
    new_items = [it for it in items if it.get("id") != fav_id]
    if len(new_items) == len(items):
        abort(404, description="Favorite not found")
    save_favorites(new_items)
    return jsonify({"ok": True, "deletedId": fav_id})

if __name__ == "__main__":
    # Importante: en local se escribirá favorites.json junto a app.py
    app.run(debug=True)
