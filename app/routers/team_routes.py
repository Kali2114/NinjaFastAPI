from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db_connection import get_db_session
from app.models import Team, User, Ninja
from app.models import enums
from app.schemas.team_schema import TeamReadSchema, TeamCreateSchema
from app.routers.utils import get_current_user, find_team


router = APIRouter()


@router.get("", response_model=list[TeamReadSchema], status_code=200)
def get_all_teams(
    sort_by: str | None = None,
    sensei_id: int | None = None,
    db: Session = Depends(get_db_session),
):
    query = db.query(Team)

    if sensei_id is not None:
        query = query.filter(Team.sensei_id == sensei_id)

    if sort_by == "name":
        query = query.order_by(Team.name)
    teams = query.all()
    return teams


@router.get("/{team_id}", response_model=TeamReadSchema, status_code=200)
def get_detail_team(team_id: int, db: Session = Depends(get_db_session)):
    team = find_team(db, team_id)
    return team


@router.post("", response_model=TeamReadSchema, status_code=201)
def create_team(
    team_data: TeamCreateSchema,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    if hasattr(db, "query"):
        kage = (
            db.query(Ninja).filter_by(user_id=user.id, rank=enums.RankEnum.kage).first()
        )

        if not kage:
            raise HTTPException(status_code=403, detail="Only kage can create teams")

    team = Team(name=team_data.name)
    try:
        db.add(team)
        db.flush()
    except (IntegrityError, ValueError):
        raise HTTPException(status_code=409, detail="Duplicate")

    return team


@router.patch("/{team_id}", status_code=403)
def edit_team_forbidden(team_id: int):
    raise HTTPException(status_code=403, detail="Editing teams is not allowed")


@router.delete("/{team_id}", status_code=403)
def delete_team_forbidden(team_id: int):
    raise HTTPException(status_code=403, detail="Deleting teams is not allowed")


@router.post(
    "/{team_id}/sensei/{ninja_id}", response_model=TeamReadSchema, status_code=200
)
def set_sensei(
    team_id: int,
    ninja_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    team = find_team(db, team_id)
    ninja = db.query(Ninja).filter(Ninja.id == ninja_id).first()

    if not ninja:
        raise HTTPException(status_code=404, detail="Ninja not found")

    try:
        team.set_sensei(ninja, db)
        db.flush()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return team


@router.post(
    "/{team_id}/members/{ninja_id}", response_model=TeamReadSchema, status_code=200
)
def add_members(
    team_id: int,
    ninja_id: int,
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
):
    team = find_team(db, team_id)
    ninja = db.query(Ninja).filter(Ninja.id == ninja_id).first()

    if not ninja:
        raise HTTPException(status_code=404, detail="Ninja not found")

    try:
        team.add_ninja(ninja)
        db.flush()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return team
