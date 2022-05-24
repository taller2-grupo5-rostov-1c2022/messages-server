from fastapi import Depends, APIRouter

from src.postgres import schemas
from src.postgres.database import get_db
from src.repositories import user_utils

router = APIRouter(tags=["users"])


@router.post("/users/", response_model=schemas.UserBase)
def post_user(user: schemas.UserBase, pdb=Depends(get_db)):
    """Create a new user"""
    return user_utils.create_user(pdb, user.id)


@router.delete("/users/{user_id}/", response_model=schemas.UserBase)
def delete_user(user_id: str, pdb=Depends(get_db)):
    """Delete a user"""
    return user_utils.delete_user(pdb, user_id)
