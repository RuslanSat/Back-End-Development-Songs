"""Songs REST API backed by the lab's real MongoDB service."""
import json
import os
from pathlib import Path
from urllib.parse import quote_plus
from bson import json_util
from flask import jsonify, request
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from . import app

host = os.environ.get("MONGODB_SERVICE", "localhost")
port = int(os.environ.get("MONGODB_PORT", "27017"))
username = os.environ.get("MONGODB_USERNAME")
password = os.environ.get("MONGODB_PASSWORD")
credentials = f"{quote_plus(username)}:{quote_plus(password)}@" if username and password else ""
uri = os.environ.get("MONGODB_URI", f"mongodb://{credentials}{host}:{port}/?authSource=admin")
client = MongoClient(uri, serverSelectionTimeoutMS=5000)
db = client[os.environ.get("MONGODB_DATABASE", "songs")]
db.songs.create_index("id", unique=True)
# Seed an empty collection only; never discard changes on restart.
if db.songs.count_documents({}) == 0:
    with (Path(__file__).parent / "data" / "songs.json").open(encoding="utf-8") as source:
        db.songs.insert_many(json.load(source))

def parse_json(data):
    return json.loads(json_util.dumps(data))

def song_payload(require_id=False):
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or not data or set(data) - {"id", "title", "lyrics"}:
        return None
    if require_id and not all(key in data for key in ("id", "title", "lyrics")):
        return None
    if "id" in data and (type(data["id"]) is not int or data["id"] < 0):
        return None
    if any(key in data and not isinstance(data[key], str) for key in ("title", "lyrics")):
        return None
    return data

@app.get("/health")
def health():
    client.admin.command("ping")
    return jsonify(status="OK"), 200

@app.get("/count")
def count():
    return jsonify(count=db.songs.count_documents({})), 200

@app.get("/song")
def get_songs():
    return jsonify(songs=parse_json(list(db.songs.find().sort("id", 1)))), 200

@app.get("/song/<int:id>")
def get_song(id):
    song = db.songs.find_one({"id": id})
    if song is None:
        return jsonify(message="song with id not found"), 404
    return jsonify(parse_json(song)), 200

@app.post("/song")
def create_song():
    song = song_payload(require_id=True)
    if song is None:
        return jsonify(message="valid integer id, title and lyrics are required"), 400
    try:
        result = db.songs.insert_one(song)
    except DuplicateKeyError:
        return jsonify(Message=f"song with id {song['id']} already present"), 302
    return jsonify(parse_json({"inserted id": result.inserted_id})), 201

@app.put("/song/<int:id>")
def update_song(id):
    changes = song_payload()
    if changes is None or ("id" in changes and changes["id"] != id):
        return jsonify(message="valid song fields and matching id are required"), 400
    result = db.songs.update_one({"id": id}, {"$set": changes})
    if result.matched_count == 0:
        return jsonify(message="song not found"), 404
    if result.modified_count == 0:
        return jsonify(message="song found, but nothing updated"), 200
    # Changed PUT returns 201, as demonstrated by the official exercise.
    return jsonify(parse_json(db.songs.find_one({"id": id}))), 201

@app.delete("/song/<int:id>")
def delete_song(id):
    result = db.songs.delete_one({"id": id})
    if result.deleted_count == 0:
        return jsonify(message="song not found"), 404
    return "", 204
