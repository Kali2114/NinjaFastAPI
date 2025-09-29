from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Literal, Optional

from app.db_connection import get_db_session
from app.models import Ninja
from app.schemas.ninja_schema import NinjaPublicReadSchema
from app.routers.utils import get_optional_user
from app.models import User


router = APIRouter()


@router.get("", response_model=list[NinjaPublicReadSchema], status_code=200)
def get_ninja(
    scope: Literal["all", "mine"] = "all",
    db: Session = Depends(get_db_session),
    current_user: Optional[User] = Depends(get_optional_user),
):
    if scope == "mine":
        if not current_user:
            raise HTTPException(status_code=401, detail="Authentication required")
        return db.query(Ninja).filter(Ninja.user_id == current_user.id).all()
    return db.query(Ninja).all()
