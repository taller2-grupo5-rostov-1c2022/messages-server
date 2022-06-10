from src.postgres import models
import requests


NOTIFICATIONS_ENDPOINT = "https://rostov-notifs-server.herokuapp.com/api/v1/messages"


def get_display_name(uid: str, auth):
    return auth.get_user(uid)["display_name"]


def send_notification(sender: models.UserModel, receiver: models.UserModel, message_text: str, auth):

    sender_name = get_display_name(sender.id, auth)
    notif_title = f"{sender_name} sent you a message"
    notif_body = message_text

    requests.post(
        NOTIFICATIONS_ENDPOINT,
        headers={"uid": sender.id, "target_uid": receiver.id},
        json={"title": notif_title, "body": notif_body},
    )
