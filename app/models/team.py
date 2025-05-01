from sqlalchemy import (
    Column,
    Integer,
    String,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.db_connection import Base

from .utils import validate_ninja_can_join_team
from app.models import enums


class Team(Base):
    __tablename__ = "team"

    id = Column(Integer, primary_key=True, nullable=False)
    name = Column(String(20), nullable=False, unique=True)
    sensei_id = Column(ForeignKey("ninja.id", use_alter=True), unique=True)
    sensei = relationship("Ninja", foreign_keys=[sensei_id], uselist=False)
    members = relationship(
        "Ninja",
        back_populates="team",
        foreign_keys="Ninja.team_id",
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_team_name"),
        UniqueConstraint("sensei_id", name="uq_sensei_id"),
    )

    def set_sensei(self, ninja, session):
        validate_ninja_can_join_team(ninja)
        if ninja.rank != enums.RankEnum.jonin:
            raise ValueError("Only jonin can be a sensei.")
        if ninja in self.members:
            raise ValueError("Team member cannot be assigned as sensei.")
        existing = session.query(Team).filter(Team.sensei_id == ninja.id).first()
        if existing:
            raise ValueError("Ninja is already a sensei of another team.")

        self.sensei = ninja

    def add_ninja(self, ninja):
        validate_ninja_can_join_team(ninja)
        if len(self.members) >= 3:
            raise ValueError("Team already has 3 members.")
        if ninja == self.sensei:
            raise ValueError("Sensei cannot be a regular member.")
        self.members.append(ninja)
