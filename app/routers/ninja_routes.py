from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db_connection import get_db_session
from app.models import Ninja
from app.schemas.ninja_schema import NinjaPublicReadSchema
from app.routers.utils import get_current_user
from app.models import User


router = APIRouter()


@router.get("", response_model=list[NinjaPublicReadSchema], status_code=200)
def get_all_ninjas(db: Session = Depends(get_db_session)):
    return db.query(Ninja).all()


@router.get("/my_ninjas", response_model=list[NinjaPublicReadSchema], status_code=200)
def get_my_ninjas(
    db: Session = Depends(get_db_session), user: User = Depends(get_current_user)
):
    return db.query(Ninja).filter(Ninja.user_id == user.id).all()


@router.get(
    "/my_ninjas/{ninja_id}", response_model=NinjaPublicReadSchema, status_code=200
)
def get_my_ninja(
    ninja_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    ninja = (
        db.query(Ninja).filter(Ninja.id == ninja_id, Ninja.user_id == user.id).first()
    )
    if not ninja:
        raise HTTPException(status_code=404, detail="Ninja not found")
    return ninja
