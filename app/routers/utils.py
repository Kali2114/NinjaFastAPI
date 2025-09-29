from sqlalchemy.orm import Session
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Optional

from app.auth.token_utils import SECRET_KEY, ALGORITHM
from app.models.user import User
from app.db_connection import get_db_session

bearer_optional = HTTPBearer(auto_error=False)


def get_optional_user(
    db: Session = Depends(get_db_session),
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_optional),
) -> Optional[User]:
    if not creds:
        return None
    try:
        payload = jwt.decode(creds.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        return (
            db.query(User).filter(User.username == username).first()
            if username
            else None
        )
    except JWTError:
        return None
