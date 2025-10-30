from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from sqlalchemy.orm import Session

from app.db_connection import get_db_session
from app.models import User, Ninja
from app.auth.token_utils import SECRET_KEY, ALGORITHM

security = HTTPBearer()


def get_current_user(
    db: Session = Depends(get_db_session),
    creds: HTTPAuthorizationCredentials = Depends(security),
):
    token = creds.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
            )

        return user

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


def find_ninja(db: Session, ninja_id: int, user_id: int, *, for_update: bool = False):
    q = db.query(Ninja).filter(Ninja.id == ninja_id, Ninja.user_id == user_id)
    if for_update:
        q = q.with_for_update()
    ninja = q.first()
    if not ninja:
        raise HTTPException(404, "Ninja not found")

    return ninja
