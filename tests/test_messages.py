import datetime

from src.repositories.message_utils import NOTIFICATIONS_ENDPOINT
from tests import utils


async def test_post_message(client, custom_requests_mock):
    response = utils.post_message(
        client, "sergio", "guido", "hola soy sergio [REDACTED]"
    )
    assert response.status_code == 200
    assert response.json()["text"] == "hola soy sergio [REDACTED]"
    assert response.json()["sender"]["id"] == "sergio"
    assert response.json()["receiver"]["id"] == "guido"


async def test_get_messages_with_zero_messages(client, custom_requests_mock):
    response = utils.get_messages(client, "sergio", "guido")
    assert response.status_code == 200
    assert response.json() == []


async def test_get_messages_creates_user_with_id_uid_if_not_exists(
    client, custom_requests_mock
):
    utils.post_message(client, "sergio", "guido", "hola soy sergio [REDACTED]")

    response = utils.get_messages(client, "does_not_exist", "guido")
    messages = response.json()

    assert response.status_code == 200
    assert len(messages) == 0


async def test_get_messages_creates_user_with_id_other_if_not_exists(
    client, custom_requests_mock
):
    utils.post_message(client, "sergio", "guido", "hola soy sergio [REDACTED]")

    response = utils.get_messages(client, "sergio", "does_not_exist")
    messages = response.json()

    assert response.status_code == 200
    assert len(messages) == 0


async def test_get_messages_with_one_message(client, custom_requests_mock):
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


async def test_get_messages_with_equal_sender_and_receiver_should_fail(
    client, custom_requests_mock
):
    response = utils.get_messages(client, "sergio", "sergio")
    assert response.status_code == 403


async def test_post_message_with_equal_sender_and_receiver_should_fail(
    client, custom_requests_mock
):
    response = utils.post_message(
        client, "sergio", "sergio", "hola soy sergio [REDACTED]"
    )
    assert response.status_code == 403


async def test_get_messages_with_many_messages(client, custom_requests_mock):
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


async def test_get_messages_only_returns_messages_from_conversation(
    client, custom_requests_mock
):
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


async def test_delete_message(client, custom_requests_mock):
    message_id = utils.post_message(
        client, "sergio", "guido", "hola soy sergio [REDACTED]"
    ).json()["id"]

    response = utils.delete_message(
        client, uid="sergio", receiver_id="guido", message_id=message_id
    )
    assert response.status_code == 200

    response = utils.get_messages(client, "sergio", "guido")
    messages = response.json()
    assert response.status_code == 200
    assert len(messages) == 0


async def test_delete_invalid_message_should_fail(client, custom_requests_mock):
    response = utils.delete_message(client, "sergio", "guido", "42")
    assert response.status_code == 404


async def test_receiver_cannot_delete_message_from_sender(client, custom_requests_mock):
    message_id = utils.post_message(
        client, "sergio", "guido", "hola soy sergio [REDACTED]"
    ).json()["id"]

    response = utils.delete_message(client, "guido", "sergio", message_id)
    assert response.status_code == 403


async def test_random_user_cannot_delete_message_from_sender(
    client, custom_requests_mock
):
    message_id = utils.post_message(
        client, "sergio", "guido", "hola soy sergio [REDACTED]"
    ).json()["id"]

    response = utils.delete_message(client, "tomas", "guido", message_id)

    assert response.status_code == 404


async def test_post_message_posts_message_even_if_notification_fails(
    client, custom_requests_mock
):
    custom_requests_mock.post(NOTIFICATIONS_ENDPOINT, status_code=500)
    response = utils.post_message(
        client, "sergio", "guido", "hola soy sergio [REDACTED]"
    )
    assert response.status_code == 200

    response = utils.get_messages(client, "sergio", "guido")
    messages = response.json()

    assert response.status_code == 200
    assert len(messages) == 1
    assert messages[0]["text"] == "hola soy sergio [REDACTED]"


async def test_get_messages_with_id_start(client, custom_requests_mock):
    utils.post_message(client, "sergio", "guido", "hola soy sergio [REDACTED]")
    second_message = utils.post_message(
        client, "sergio", "guido", "falta la [REDACTED]"
    ).json()
    utils.post_message(client, "sergio", "guido", "eso es detalle de [REDACTED]")

    response = utils.get_messages(
        client, "sergio", "guido", start_id=second_message["id"]
    )
    messages = response.json()

    assert response.status_code == 200
    assert len(messages) == 2
    assert messages[0]["text"] == "falta la [REDACTED]"
    assert messages[1]["text"] == "eso es detalle de [REDACTED]"
