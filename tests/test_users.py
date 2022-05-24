from src.main import API_VERSION_PREFIX


def test_post_user(client):
    response = client.post(
        f"{API_VERSION_PREFIX}/users/",
        json={"id": "test_user_id"},
        headers={"api_key": "key"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == "test_user_id"


def test_post_already_existing_user(client):
    response = client.post(
        f"{API_VERSION_PREFIX}/users/",
        json={"id": "test_user_id"},
        headers={"api_key": "key"},
    )
    assert response.status_code == 200
    response = client.post(
        f"{API_VERSION_PREFIX}/users/",
        json={"id": "test_user_id"},
        headers={"api_key": "key"},
    )
    assert response.status_code == 409


def test_delete_user(client):
    response = client.post(
        f"{API_VERSION_PREFIX}/users/",
        json={"id": "test_user_id"},
        headers={"api_key": "key"},
    )
    assert response.status_code == 200
    response = client.delete(
        f"{API_VERSION_PREFIX}/users/test_user_id/",
        headers={"api_key": "key"},
    )
    assert response.status_code == 200


def test_delete_already_deleted_user(client):
    response = client.post(
        f"{API_VERSION_PREFIX}/users/",
        json={"id": "test_user_id"},
        headers={"api_key": "key"},
    )
    assert response.status_code == 200
    response = client.delete(
        f"{API_VERSION_PREFIX}/users/test_user_id/",
        headers={"api_key": "key"},
    )
    assert response.status_code == 200
    response = client.delete(
        f"{API_VERSION_PREFIX}/users/test_user_id/",
        headers={"api_key": "key"},
    )
    assert response.status_code == 404
