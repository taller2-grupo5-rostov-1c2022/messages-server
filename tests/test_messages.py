import time

from src.constants import STORAGE_PATH
from tests import utils
from tests.utils import post_user
from tests.utils import API_VERSION_PREFIX
from urllib.parse import urlparse
from urllib.parse import parse_qs


def test_post_message(client):
    post_user(client, "sergio")
    post_user(client, "guido")

    response = utils.post_message(
        client, "sergio", "guido", "hola soy sergio [REDACTED]"
    )

    assert response.status_code == 200
    assert response.json()["text"] == "hola soy sergio [REDACTED]"
    assert response.json()["sender"]["id"] == "sergio"
    assert response.json()["receiver"]["id"] == "guido"


def test_get_messages_with_zero_messages(client):
    post_user(client, "sergio")
    post_user(client, "guido")

    response = utils.get_messages(client, "sergio", "guido")
    print(response.json())
    assert response.status_code == 200
    assert response.json() == []


def test_get_messages_with_invalid_user_1_should_fail(client):
    post_user(client, "sergio")
    post_user(client, "guido")

    response = utils.get_messages(client, "invalid", "guido")
    assert response.status_code == 404


def test_get_messages_with_invalid_user_2_should_fail(client):
    post_user(client, "sergio")
    post_user(client, "guido")

    response = utils.get_messages(client, "sergio", "invalid")
    assert response.status_code == 404


def test_get_messages_with_one_message(client):
    post_user(client, "sergio")
    post_user(client, "guido")

    message_id = utils.post_message(
        client, "sergio", "guido", "hola soy sergio [REDACTED]"
    ).json()["id"]

    response = utils.get_messages(client, "sergio", "guido")
    messages = response.json()

    assert response.status_code == 200
    assert len(messages) == 1
    assert messages[0]["id"] == message_id
    assert messages[0]["text"] == "hola soy sergio [REDACTED]"
    assert messages[0]["sender"]["id"] == "sergio"
    assert messages[0]["receiver"]["id"] == "guido"


def test_get_messages_with_many_messages(client):
    post_user(client, "sergio")
    post_user(client, "guido")

    utils.post_message(client, "sergio", "guido", "hola soy sergio [REDACTED]")
    utils.post_message(client, "sergio", "guido", "falta la [REDACTED]")
    utils.post_message(client, "sergio", "guido", "eso es detalle de [REDACTED]")

    response = utils.get_messages(client, "sergio", "guido")
    messages = response.json()

    assert response.status_code == 200
    assert len(messages) == 3
    assert messages[0]["text"] == "hola soy sergio [REDACTED]"
    assert messages[1]["text"] == "falta la [REDACTED]"
    assert messages[2]["text"] == "eso es detalle de [REDACTED]"


def test_get_messages_only_returns_messages_from_conversation(client):
    post_user(client, "sergio")
    post_user(client, "guido")
    post_user(client, "tomas")

    utils.post_message(client, "sergio", "guido", "hola soy sergio [REDACTED]")
    utils.post_message(client, "sergio", "tomas", "punto extra para [REDACTED]")

    response = utils.get_messages(client, "sergio", "guido")
    messages = response.json()

    assert response.status_code == 200
    assert len(messages) == 1
    assert messages[0]["text"] == "hola soy sergio [REDACTED]"
    assert messages[0]["sender"]["id"] == "sergio"
    assert messages[0]["receiver"]["id"] == "guido"
    assert messages[0]["created_at"] is not None


def test_delete_message(client):
    post_user(client, "sergio")
    post_user(client, "guido")

    message_id = utils.post_message(
        client, "sergio", "guido", "hola soy sergio [REDACTED]"
    ).json()["id"]

    response = utils.delete_message(client, message_id)
    assert response.status_code == 200

    response = utils.get_messages(client, "sergio", "guido")
    messages = response.json()
    assert response.status_code == 200
    assert len(messages) == 0


def test_delete_invalid_message_should_fail(client):
    post_user(client, "sergio")
    post_user(client, "guido")

    response = utils.delete_message(client, 42)
    assert response.status_code == 404
