from sqlalchemy import (
    Column,
    Integer,
    Enum as SQLAEnum,
    UniqueConstraint,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.models import enums
from app.db_connection import Base
from .utils import ensure_alive, validate_set_kage


class Village(Base):
    __tablename__ = "village"

    id = Column(Integer, primary_key=True)
    name = Column(SQLAEnum(enums.VillageEnum), unique=True, nullable=False)
    country = Column(SQLAEnum(enums.CountryEnum), nullable=False)
    kage_id = Column(ForeignKey("ninja.id", use_alter=True), nullable=True, unique=True)
    kage = relationship("Ninja", foreign_keys=[kage_id])
    ninjas = relationship(
        "Ninja", back_populates="village", foreign_keys="Ninja.village_id"
    )

    __table_args__ = (
        UniqueConstraint("name", name="uq_village_name"),
        UniqueConstraint("kage_id", name="uq_kage_id"),
    )

    def add_ninja_to_village(self, ninja):
        ensure_alive(ninja)
        if ninja.village is not None:
            raise ValueError("Ninja already belongs to village.")
        ninja.village = self

    def set_kage(self, ninja):
        ensure_alive(ninja)
        validate_set_kage(ninja, self)
        self.kage = ninja
