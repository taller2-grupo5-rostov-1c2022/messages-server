from src.mongo import schemas
import requests
import os
from dotenv import load_dotenv
import json
from datetime import date, datetime

load_dotenv()

NOTIFICATIONS_ENDPOINT = "https://rostov-notifs-server.herokuapp.com/api/v1/messages/"
NOTIFS_API_KEY = os.getenv("NOTIFS_API_KEY")


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type %s not serializable" % type(obj))


def get_display_name(uid: str, auth):
    return auth.get_user(uid).display_name


def send_notification(
    sender_id: str,
    receiver_id: str,
    message: dict,
    auth,
):

    sender_name = get_display_name(sender_id, auth)
    notif_title = f"{sender_name} sent you a message"
    notif_body = message["text"]
    notif_extra = json.dumps(message, default=json_serial)

    requests.post(
        NOTIFICATIONS_ENDPOINT,
        headers={
            "uid": sender_id,
            "target-uid": receiver_id,
            "api_key": NOTIFS_API_KEY,
        },
        json={"title": notif_title, "body": notif_body, "extra": notif_extra},
    )
