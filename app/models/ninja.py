from sqlalchemy import Column, Integer, String, Enum as SQLAEnum, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import validates


from app.models import enums
from app.db_connection import Base


class Ninja(Base):
    __tablename__ = "ninja"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    clan = Column(String(20), nullable=False)
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)
    team_id = Column(ForeignKey("team.id"))
    sensei = Column(String(20))
    summon_animal = Column(String(20))
    mission_completed = Column(Integer, default=0)
    village_id = Column(ForeignKey("village.id"))
    rank = Column(SQLAEnum(enums.RankEnum), default=enums.RankEnum.academy)
    kekkei_genkai = Column(
        SQLAEnum(enums.KekkeiGenkaiEnum), default=enums.KekkeiGenkaiEnum.none
    )
    chakra_nature = Column(ARRAY(String))
    alive = Column(Boolean, default=True)
    forbidden = Column(Boolean, default=False)
    jinchuriki = Column(
        SQLAEnum(enums.JinchurikiEnum), default=enums.JinchurikiEnum.none
    )

    @validates("chakra_nature")
    def validate_chakra_nautre(self, key, value):
        allowed = {"Fire", "Water", "Lightning", "Earth", "Wind"}
        if not set(value).issubset(allowed):
            raise ValueError("Invalid chakra nature(s)")
        return value
