"""Exercise the running HTTP service and its real MongoDB persistence."""
import os
import requests


def test_real_http_lifecycle():
    base = os.environ.get("SONGS_BASE_URL", "http://localhost:5000")
    session = requests.Session()
    assert session.get(base + "/health", timeout=10).json() == {"status": "OK"}
    songs = session.get(base + "/song", timeout=10)
    assert songs.status_code == 200
    assert isinstance(songs.json()["songs"], list)
    count_before = session.get(base + "/count", timeout=10).json()["count"]
    sample_id = 900001
    resource = f"{base}/song/{sample_id}"
    # Only this explicitly named disposable test resource is removed.
    session.delete(resource, timeout=10)
    payload = {"id": sample_id, "title": "Capstone integration song", "lyrics": "Original test lyrics"}
    try:
        assert session.post(base + "/song", json=payload, timeout=10).status_code == 201
        assert session.post(base + "/song", json=payload, timeout=10).status_code == 302
        response = session.get(resource, timeout=10)
        assert response.status_code == 200
        assert response.json()["title"] == payload["title"]
        change = {"title": "Updated integration song", "lyrics": "Updated test lyrics"}
        response = session.put(resource, json=change, timeout=10)
        assert response.status_code == 201
        assert response.json()["title"] == change["title"]
        assert session.get(resource, timeout=10).json()["lyrics"] == change["lyrics"]
        assert session.put(resource, json=change, timeout=10).status_code == 200
        assert session.put(resource, json={"id": sample_id + 1}, timeout=10).status_code == 400
        assert session.post(base + "/song", json={"id": "bad"}, timeout=10).status_code == 400
        deleted = session.delete(resource, timeout=10)
        assert deleted.status_code == 204
        assert deleted.content == b""
        assert session.get(resource, timeout=10).status_code == 404
        assert session.delete(resource, timeout=10).status_code == 404
        assert session.put(resource, json=change, timeout=10).status_code == 404
        assert session.get(base + "/count", timeout=10).json()["count"] == count_before
    finally:
        session.delete(resource, timeout=10)
