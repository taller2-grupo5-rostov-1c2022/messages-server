from datetime import datetime
from operator import and_
from typing import List

from fastapi import Depends, APIRouter, HTTPException, Header
from sqlalchemy import or_

from src.postgres import schemas, models
from src.postgres.database import get_db
from src.repositories import user_utils

router = APIRouter(tags=["messages"])


@router.post("/messages/", response_model=schemas.MessageBase)
def post_message(
    receiver_id: str,
    message_text: schemas.MessageText,
    pdb=Depends(get_db),
    uid: str = Header(...),
):
    sender = user_utils.get_user(pdb, uid)
    receiver = user_utils.get_user(pdb, receiver_id)

    message = models.MessageModel(
        receiver_id=receiver.id,
        sender_id=sender.id,
        text=message_text.text,
        read=False,
        created_at=datetime.now(),
    )
    pdb.add(message)
    pdb.commit()
    return message


@router.get("/messages/{other_id}/", response_model=List[schemas.MessageBase])
def get_messages(other_id: str, uid: str = Header(...), pdb=Depends(get_db)):

    user_1 = user_utils.get_user(pdb, uid)
    user_2 = user_utils.get_user(pdb, other_id)

    messages = (
        pdb.query(models.MessageModel)
        .filter(
            or_(
                and_(
                    models.MessageModel.receiver == user_1,
                    models.MessageModel.sender == user_2,
                ),
                and_(
                    models.MessageModel.receiver == user_2,
                    models.MessageModel.sender == user_1,
                ),
            )
        )
        .order_by(models.MessageModel.created_at)
        .all()
    )

    return messages


@router.delete("/messages/{message_id}/")
def delete_message(message_id: int, uid: str = Header(...), pdb=Depends(get_db)):
    message = pdb.get(models.MessageModel, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    if message.sender.id != uid:
        raise HTTPException(
            status_code=403, detail="Attempt to delete other user's message"
        )

    pdb.delete(message)
    pdb.commit()
    return message
