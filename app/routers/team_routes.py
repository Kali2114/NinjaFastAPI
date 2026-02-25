from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db_connection import get_db_session
from app.models import Team
from app.schemas.team_schema import TeamReadSchema


router = APIRouter()


@router.get("", response_model=list[TeamReadSchema], status_code=200)
def get_all_teams(db: Session = Depends(get_db_session)):
    return db.query(Team).all()
