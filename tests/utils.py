from datetime import datetime
from typing import Optional, List
import json

from src.main import API_VERSION_PREFIX


def post_message(client, sender_id: str, receiver_id: str, text: str):
    response = client.post(
        f"{API_VERSION_PREFIX}/messages/?receiver_id={receiver_id}",
        json={"text": text},
        headers={"api_key": "key", "uid": sender_id},
    )
    return response


def get_messages(
    client, uid: str, other_id: str, start_id: Optional[int] = None
):
    if start_id is None:
        response = client.get(
            f"{API_VERSION_PREFIX}/messages/{other_id}/",
            headers={"api_key": "key", "uid": uid},
        )
    else:
        response = client.get(
            f"{API_VERSION_PREFIX}/messages/{other_id}/?start_id={start_id}",
            headers={"api_key": "key", "uid": uid},
        )
    return response


def delete_message(client, uid: str, receiver_id: str, message_id: str):
    response = client.delete(
        f"{API_VERSION_PREFIX}/messages/{message_id}/?receiver_id={receiver_id}",
        headers={"api_key": "key", "uid": uid},
    )
    return response
