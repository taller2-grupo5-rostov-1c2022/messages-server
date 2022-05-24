from typing import Optional, List
import json

from src.main import API_VERSION_PREFIX


def post_user(client, user_id: str):
    response = client.post(
        f"{API_VERSION_PREFIX}/users/",
        json={"id": user_id},
        headers={"api_key": "key"},
    )
    return response


def post_message(client, sender_id: str, receiver_id: str, text: str):
    response = client.post(
        f"{API_VERSION_PREFIX}/messages/",
        json={
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "text": text,
        },
        headers={"api_key": "key"},
    )
    return response


def get_messages(client, user_1: str, user_2: str):
    response = client.get(
        f"{API_VERSION_PREFIX}/messages/?user_id_1={user_1}&user_id_2={user_2}",
        headers={"api_key": "key"},
    )
    return response


def delete_message(client, message_id: int):
    response = client.delete(
        f"{API_VERSION_PREFIX}/messages/{message_id}/",
        headers={"api_key": "key"},
    )
    return response
