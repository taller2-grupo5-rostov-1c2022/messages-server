from fastapi import Depends

from src.postgres import schemas
from src.postgres.database import get_db
from src.repositories import user_utils


def retrieve_message(message_info: schemas.MessagePost, pdb=Depends(get_db)):
    sender = user_utils.retrieve_user(message_info.sender_id, pdb)
    receiver = user_utils.retrieve_user(message_info.receiver_id, pdb)

    return schemas.MessageInfo(text=message_info.text, sender=sender, receiver=receiver)
