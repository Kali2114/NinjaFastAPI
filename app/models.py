from sqlalchemy import Column, Integer

from .db_connection import Base


class Ninja(Base):
    __tablename__ = "ninja"

    id = Column(Integer, primary_key=True)
