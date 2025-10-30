from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.db_connection import get_db_session
from app.models import Ninja
from app.schemas.ninja_schema import NinjaPublicReadSchema, NinjaCreateSchema
from app.routers.utils import get_current_user, find_ninja
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
    ninja = find_ninja(db, ninja_id, user.id)
    return ninja


@router.post("", response_model=NinjaPublicReadSchema, status_code=201)
def create_ninja(
    ninja_data: NinjaCreateSchema,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    data = ninja_data.model_dump()
    ninja = Ninja(**data)
    ninja.user_id = user.id
    db.add(ninja)
    db.flush()

    return ninja


@router.delete("/my_ninjas/{ninja_id}", status_code=204)
def delete_ninja(
    ninja_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):

    ninja = find_ninja(db, ninja_id, user.id)
    db.delete(ninja)
    db.flush()

    return Response(status_code=204)


@router.post("/my_ninjas/{ninja_id}/train", response_model=NinjaPublicReadSchema)
def train_ninja(
    ninja_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    ninja = find_ninja(db, ninja_id, user.id, for_update=True)
    try:
        ninja.train()
    except RuntimeError as e:
        msg = str(e).lower()
        if "dead" in msg:
            raise HTTPException(status_code=409, detail="Ninja is dead")
        if "not enough chakra" in msg:
            raise HTTPException(status_code=400, detail="Not enough chakra")
        raise

    return ninja


@router.post("/my_ninjas/{ninja_id}/rest", response_model=NinjaPublicReadSchema)
def rest_ninja(
    ninja_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    ninja = find_ninja(db, ninja_id, user.id, for_update=True)
    try:
        ninja.rest()
    except RuntimeError as e:
        msg = str(e).lower()
        if "dead" in msg:
            raise HTTPException(status_code=409, detail="Ninja is dead")
        raise

    return ninja
