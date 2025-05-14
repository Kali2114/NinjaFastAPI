from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum as SQLAEnum,
    Boolean,
    CheckConstraint,
    text,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import validates, relationship

import random

from app.models import enums
from app.db_connection import Base
from .utils import ensure_alive


class Ninja(Base):
    __tablename__ = "ninja"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    chakra = Column(Integer, default=100, server_default=text("100"), nullable=False)
    clan = Column(String(20), nullable=False)
    level = Column(Integer, default=1, server_default=text("1"), nullable=False)
    experience = Column(Integer, default=0, server_default=text("0"), nullable=False)
    team_id = Column(ForeignKey("team.id"), nullable=True)
    team = relationship("Team", back_populates="members", foreign_keys=[team_id])
    user_id = Column(ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="ninjas")
    sensei = Column(String(20))
    summon_animal = Column(String(20))
    mission_completed = Column(
        Integer, default=0, server_default=text("0"), nullable=False
    )
    village_id = Column(ForeignKey("village.id"), nullable=True)
    village = relationship(
        "Village", back_populates="ninjas", foreign_keys=[village_id]
    )
    rank = Column(
        SQLAEnum(enums.RankEnum),
        default=enums.RankEnum.academy,
        server_default=text("'academy'"),
        nullable=False,
    )
    kekkei_genkai = Column(
        SQLAEnum(enums.KekkeiGenkaiEnum),
        default=enums.KekkeiGenkaiEnum.none,
        server_default=text("'none'"),
    )
    chakra_nature = Column(ARRAY(String))
    alive = Column(Boolean, default=True, server_default=text("true"), nullable=False)
    forbidden = Column(
        Boolean, default=False, server_default=text("false"), nullable=False
    )
    jinchuriki = Column(
        SQLAEnum(enums.JinchurikiEnum),
        default=enums.JinchurikiEnum.none,
        server_default=text("'none'"),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("LENGTH(name) > 0", name="name_length_check"),
        CheckConstraint("chakra >= 0", name="chakra_check"),
        CheckConstraint("LENGTH(clan) > 0", name="clan_length_check"),
        CheckConstraint("level >= 1", name="min_1_lvl_check"),
        CheckConstraint("experience >= 0", name="experience_positive_check"),
        CheckConstraint("mission_completed >= 0", name="mission_positive_check"),
        UniqueConstraint("name", name="uq_ninja_name"),
    )

    @validates("chakra_nature")
    def validate_chakra_nature(self, key, value):
        allowed = {"Fire", "Water", "Lightning", "Earth", "Wind"}
        if not set(value).issubset(allowed):
            raise ValueError("Invalid chakra nature(s)")
        return value

    def add_experience(self):
        ensure_alive(self)
        self.experience += random.randint(1, 4)
        self._check_level_up()

    def train(self):
        ensure_alive(self)
        chakra_spent = random.randint(30, 50)
        if self.chakra < chakra_spent:
            raise RuntimeError("Not enough chakra for training")
        self.chakra -= chakra_spent
        self.add_experience()

    def _check_level_up(self):
        current_lvl = self.level
        new_lvl = max(
            [
                lvl
                for lvl, xp in enums.LEVEL_THRESHOLDS.items()
                if self.experience >= xp
            ],
            default=current_lvl,
        )
        if new_lvl != current_lvl:
            self.level = new_lvl
            self._check_chakra_level()

    def rest(self):
        ensure_alive(self)
        self.chakra = enums.CHAKRA_THRESHOLDS[self.level]

    def _check_chakra_level(self):
        self.chakra = enums.CHAKRA_THRESHOLDS[self.level]

    def learn_chakra_nature(self, chakra):
        ensure_alive(self)
        self.validate_chakra_nature("chakra_nature", [chakra])
        self.chakra_nature = (self.chakra_nature or []) + [chakra]

    def mark_as_dead(self):
        self.alive = False

    def mark_as_forbidden(self):
        ensure_alive(self)
        self.forbidden = True

    def change_rank(self, new_rank):
        ensure_alive(self)
        try:
            self.rank = enums.RankEnum(new_rank)
        except ValueError:
            raise ValueError("Invalid rank")
