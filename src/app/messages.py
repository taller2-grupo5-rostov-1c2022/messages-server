import pytz
from datetime import datetime
from typing import List, Optional
from fastapi import Depends, APIRouter, HTTPException, Header, Query

from src.firebase.access import get_auth
from src.mongo import schemas

from src.mongo.database import get_db
from src.repositories import message_utils

utc = pytz.utc

router = APIRouter(tags=["messages"])


"""
def get_collection(db, sender_id, receiver_id):
    uid_1, uid_2 = sorted([sender_id, receiver_id])
    collection_name = f"messages_{uid_1}_{uid_2}"
    return db.get_collection(collection_name)
"""


@router.post("/messages/", response_model=schemas.MessageGet)
async def post_message(
    receiver_id: str,
    message_text: schemas.MessageText,
    uid: str = Header(...),
    db=Depends(get_db),
    auth=Depends(get_auth),
):

    messages = db.get_collection("messages")

    message = schemas.MessagePost(
        receiver_id=receiver_id,
        sender_id=uid,
        text=message_text.text,
        created_at=utc.localize(datetime.now()),
    )

    messages_between_users = await messages.find_one(
        {"users": {"$all": [uid, receiver_id]}}
    )

    if messages_between_users is None:
        messages_between_users = {
            "users": [uid, receiver_id],
            "user_msgs": [message.dict()],
        }
        await messages.insert_one(messages_between_users)
    else:
        messages_between_users["user_msgs"].append(message.dict())
        await messages.replace_one(
            {"_id": messages_between_users["_id"]}, messages_between_users
        )

    message_id = len(messages_between_users["user_msgs"]) - 1
    message_dict = message.dict()
    message_dict["id"] = message_id

    message_utils.send_notification(uid, receiver_id, message_dict, auth)

    return schemas.MessageGet.from_orm(message_dict)


@router.get("/messages/{other_id}/", response_model=List[schemas.MessageGet])
async def get_messages(
    other_id: str,
    uid: str = Header(...),
    date_start: Optional[datetime] = Query(None),
    db=Depends(get_db),
):
    messages = db.get_collection("messages")

    queries = {}
    if date_start:
        queries["created_at"] = {"$gte": date_start}

    chat_doc = await messages.find_one({"users": {"$all": [uid, other_id]}})
    if chat_doc is None:
        return []
    else:
        messages_between_users = chat_doc["user_msgs"]
        messages_list_with_id = []
        for i, message in enumerate(messages_between_users):
            message["id"] = i
            messages_list_with_id.append(message)

        messages_between_users = messages_list_with_id
        if date_start:
            messages_between_users = [
                msg for msg in messages_between_users if msg["created_at"] >= date_start
            ]

        return [schemas.MessageGet.from_orm(msg) for msg in messages_between_users]


@router.delete("/messages/{message_id}/")
async def delete_message(
    message_id: int, receiver_id: str, uid: str = Header(...), db=Depends(get_db)
):

    messages = db.get_collection("messages")
    chat_doc = await messages.find_one({"users": {"$all": [uid, receiver_id]}})
    if chat_doc is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    if message_id >= len(chat_doc["user_msgs"]):
        raise HTTPException(status_code=404, detail="Message not found")

    if chat_doc["user_msgs"][message_id]["sender_id"] != uid:
        raise HTTPException(
            status_code=403, detail="You are not the sender of this message"
        )

    chat_doc["user_msgs"].pop(message_id)
    await messages.replace_one({"_id": chat_doc["_id"]}, chat_doc)
