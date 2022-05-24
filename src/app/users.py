from fastapi import Depends, APIRouter

from src.postgres import schemas
from src.postgres.database import get_db
from src.repositories import user_utils

router = APIRouter(tags=["users"])


@router.delete("/users/{user_id}/", response_model=schemas.UserBase)
def delete_user(user_id: str, pdb=Depends(get_db)):
    """Delete a user"""
    return user_utils.delete_user(pdb, user_id)
