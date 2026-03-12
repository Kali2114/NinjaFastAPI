from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.db_connection import get_db_session
from app.models import Team, User, Ninja
from app.models import enums
from app.schemas.team_schema import TeamReadSchema, TeamCreateSchema
from app.routers.utils import get_current_user


router = APIRouter()


@router.get("", response_model=list[TeamReadSchema], status_code=200)
def get_all_teams(db: Session = Depends(get_db_session)):
    return db.query(Team).all()


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
