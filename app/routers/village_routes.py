from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db_connection import get_db_session
from app.models import Village, User
from app.schemas.village_schema import VillageReadSchema
from app.routers.utils import find_village, get_current_user, find_ninja
from app.models.utils import ensure_alive


router = APIRouter()


@router.get("/", response_model=list[VillageReadSchema], status_code=200)
def get_all_villages(sort_by: str | None = None, db: Session = Depends(get_db_session)):
    query = db.query(Village)

    villages = query.all()

    if sort_by == "country":
        villages = sorted(villages, key=lambda village: village.country.value)

    if sort_by == "name":
        villages = sorted(villages, key=lambda village: village.name.value)

    return villages


@router.get("/{village_id}", response_model=VillageReadSchema, status_code=200)
def get_detail_village(village_id: int, db: Session = Depends(get_db_session)):
    village = find_village(db, village_id)
    return village


@router.post(
    "/{village_id}/add_ninja_to_village/{ninja_id}",
    response_model=VillageReadSchema,
    status_code=200,
)
def add_ninja_to_village(
    village_id: int,
    ninja_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    village = find_village(db, village_id)
    ninja = find_ninja(db, ninja_id, user.id)
    try:
        village.add_ninja_to_village(ninja)
        ensure_alive(ninja)
        return village
    except (ValueError, RuntimeError) as e:
        raise HTTPException(409, detail=str(e))


@router.post(
    "/{village_id}/set_kage/{ninja_id}",
    response_model=VillageReadSchema,
    status_code=200,
)
def set_kage(
    village_id: int,
    ninja_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    village = find_village(db, village_id)
    ninja = find_ninja(db, ninja_id, user.id)
    try:
        village.set_kage(ninja)
        db.flush()
        return village
    except (ValueError, RuntimeError) as e:
        raise HTTPException(409, detail=str(e))
