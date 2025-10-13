from flask import Flask, jsonify, abort, request
import json, os

app = Flask(__name__)
data_path = os.path.join(os.path.dirname(__file__), "albums.json")
with open(data_path, "r", encoding="utf-8") as f:
    raw = json.load(f)
albums = [{**item, "id": i+1} for i, item in enumerate(raw)]

@app.get("/")
def index():
    return jsonify({"endpoints": ["/albums", "/albums/<id>"], "count": len(albums)})

# Endpoint para mostrar todos los álbumes
@app.get("/albums")
def list_albums():
    return jsonify({"count": len(albums), "items": albums})

# Endpoint para obtener un álbum por ID
@app.get("/albums/<int:item_id>")
def get_album(item_id: int):
    for a in albums:
        if a["id"] == item_id:
            return jsonify(a)
    abort(404, description="Album not found")

# Endpoint para agregar un nuevo álbum
@app.post("/albums")
def create_album():
    data = request.get_json()
    if not data or "title" not in data or "artist" not in data or "year" not in data:
        abort(400, description="Missing required fields")
    
    # Crear un nuevo álbum con el siguiente ID disponible
    new_album = {
        "id": len(albums) + 1,
        "title": data["title"],
        "artist": data["artist"],
        "year": data["year"],
        "isFavorite": data.get("isFavorite", False),  # Default to False
    }
    albums.append(new_album)

    # Guardar el nuevo álbum en el archivo JSON
    with open(data_path, "w", encoding="utf-8") as f:
        json.dump(albums, f, indent=4)

    return jsonify(new_album), 201  # Retorna el álbum creado con el código 201

# Endpoint para actualizar un álbum
@app.patch("/albums/<int:item_id>")
def update_album(item_id: int):
    data = request.get_json()
    for a in albums:
        if a["id"] == item_id:
            if "title" in data:
                a["title"] = data["title"]
            if "artist" in data:
                a["artist"] = data["artist"]
            if "year" in data:
                a["year"] = data["year"]
            if "isFavorite" in data:
                a["isFavorite"] = data["isFavorite"]
            
            # Guardar el álbum actualizado en el archivo JSON
            with open(data_path, "w", encoding="utf-8") as f:
                json.dump(albums, f, indent=4)
            
            return jsonify(a)  # Retorna el álbum actualizado
    abort(404, description="Album not found")
    
if __name__ == "__main__":
    app.run(threaded=True, host="0.0.0.0", port=3000)
