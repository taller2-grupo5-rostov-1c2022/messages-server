from datetime import datetime
from operator import and_
from typing import List

from fastapi import Depends, APIRouter, HTTPException
from sqlalchemy import or_

from src.postgres import schemas, models
from src.postgres.database import get_db
from src.repositories import message_utils, user_utils

router = APIRouter(tags=["messages"])


@router.post("/messages/", response_model=schemas.MessageBase)
def post_message(
    message_info: schemas.MessageInfo = Depends(message_utils.retrieve_message),
    pdb=Depends(get_db),
):
    message = models.MessageModel(
        receiver_id=message_info.receiver.id,
        sender_id=message_info.sender.id,
        text=message_info.text,
        read=False,
        created_at=datetime.now(),
    )
    pdb.add(message)
    pdb.commit()
    print(message)
    return message


@router.get("/messages/", response_model=List[schemas.MessageBase])
def get_messages(user_id_1: str, user_id_2: str, pdb=Depends(get_db)):
    user_1 = user_utils.retrieve_user(user_id_1, pdb)
    user_2 = user_utils.retrieve_user(user_id_2, pdb)

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
def delete_message(message_id: int, pdb=Depends(get_db)):
    message = pdb.get(models.MessageModel, message_id)
    if message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    pdb.delete(message)
    pdb.commit()
    return message
