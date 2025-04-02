import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base


DEV_DATABASE_URL = os.getenv("DEV_DATABASE")

engine = create_engine(DEV_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=True)

Base = declarative_base


def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
