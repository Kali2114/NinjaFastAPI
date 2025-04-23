from sqlalchemy import (
    Column,
    Integer,
    String,
    Enum as SQLAEnum,
    Boolean,
    CheckConstraint,
    text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import validates


from app.models import enums
from app.db_connection import Base


class Ninja(Base):
    __tablename__ = "ninja"

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False)
    clan = Column(String(20), nullable=False)
    level = Column(Integer, default=1, server_default=text("1"), nullable=False)
    experience = Column(Integer, default=0, server_default=text("0"), nullable=False)
    # team_id = Column(ForeignKey("team.id"))
    sensei = Column(String(20))
    summon_animal = Column(String(20))
    mission_completed = Column(
        Integer, default=0, server_default=text("0"), nullable=False
    )
    # village_id = Column(ForeignKey("village.id"))
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
        CheckConstraint("LENGTH(clan) > 0", name="clan_length_check"),
        CheckConstraint("level >= 1", name="min_1_lvl_check"),
        CheckConstraint("experience >= 0", name="experience_positive_check"),
        CheckConstraint("mission_completed >= 0", name="mission_positive_check"),
        UniqueConstraint("name", name="uq_ninja_name"),
    )

    @validates("chakra_nature")
    def validate_chakra_nautre(self, key, value):
        allowed = {"Fire", "Water", "Lightning", "Earth", "Wind"}
        if not set(value).issubset(allowed):
            raise ValueError("Invalid chakra nature(s)")
        return value
