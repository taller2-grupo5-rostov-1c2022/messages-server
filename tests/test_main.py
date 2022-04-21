import os
from fastapi.testclient import TestClient

os.environ["TESTING"] = "1"

from src.main import app

client = TestClient(app)


def test_unauthorized_get():
    response = client.get("/api/v1/users/")
    assert response.status_code == 403


def test_get_users():
    response = client.get("/api/v1/users/", headers={"api_key": "key"})
    assert response.status_code == 200


def test_post_user():
    response_post = client.post(
        "/api/v1/users/?user_name=New%20Username", headers={"api_key": "key"}
    )
    assert response_post.status_code == 200
    response_get = client.get(
        "/api/v1/users/" + str(response_post.json()["id"]), headers={"api_key": "key"}
    )
    assert response_get.status_code == 200
    assert response_get.json()["playlists"] == []
    assert response_get.json()["songs"] == []
