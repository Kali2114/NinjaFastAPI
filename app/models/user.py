from sqlalchemy import (
    Column,
    Integer,
    String,
    UniqueConstraint,
    Boolean,
    DateTime,
    CheckConstraint,
    text,
)
from sqlalchemy.orm import relationship

from datetime import datetime, timezone

from app.db_connection import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, nullable=False)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(30), unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    ninjas = relationship("Ninja", back_populates="user")
    is_active = Column(
        Boolean, default=True, server_default=text("true"), nullable=False
    )
    created_at = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)

    __table_args__ = (
        CheckConstraint("LENGTH(username) > 0", name="username_length_check"),
        CheckConstraint("LENGTH(email) > 0", name="email_length_check"),
        CheckConstraint("LENGTH(hashed_password) > 0", name="password_length_check"),
        UniqueConstraint("username", name="uq_username"),
        UniqueConstraint("email", name="uq_email"),
    )
