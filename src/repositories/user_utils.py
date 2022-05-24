from fastapi import Header, Depends, HTTPException

from src.postgres import models
from src.postgres.database import get_db


def retrieve_user(user_id: str, pdb):
    """Returns the user id of the user or 404 if not found"""

    user = pdb.get(models.UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def retrieve_sender(sender_id: str, pdb=Depends(get_db)) -> models.UserModel:
    """Returns the user id of the sender or 404 if not found"""

    return retrieve_user(sender_id, pdb)


def retrieve_receiver(receiver_id: str, pdb=Depends(get_db)) -> models.UserModel:
    """Returns the user id of the reciever or 404 if not found"""

    return retrieve_user(receiver_id, pdb)


def create_user(pdb, user_id: str):
    """Creates a user with the given id"""

    user = pdb.query(models.UserModel).filter_by(id=user_id).first()
    if user is not None:
        raise HTTPException(status_code=409, detail="User already exists")
    user = models.UserModel(id=user_id)
    pdb.add(user)
    pdb.commit()
    return user


def delete_user(pdb, user_id: str):
    """Deletes a user with the given id"""

    user = pdb.get(models.UserModel, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    pdb.delete(user)
    pdb.commit()
    return user
