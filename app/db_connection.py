import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from pathlib import Path
import sys
from dotenv import load_dotenv

load_dotenv(dotenv_path=Path(__file__).resolve().parent.parent / ".env")


if "pytest" in sys.modules:
    DATABASE_URL = os.getenv("TEST_DATABASE_URL")
else:
    DATABASE_URL = os.getenv("DEV_DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=True, bind=engine)

Base = declarative_base()


def get_db_session():
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except:
        db.rollback()
        raise
    finally:
        db.close()
