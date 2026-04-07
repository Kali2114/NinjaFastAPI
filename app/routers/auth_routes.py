from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.schemas.user_schema import UserCreateSchema, UserReadSchema, UserLoginSchema
from app.models import User
from app.models.utils import save_avatar_in_storage
from app.db_connection import get_db_session
from app.auth.hashing import hash_password, verify_password
from app.auth.token_utils import create_token
from app.routers.utils import get_current_user


router = APIRouter()


@router.post("/register", response_model=UserReadSchema, status_code=201)
def register(user_data: UserCreateSchema, db: Session = Depends(get_db_session)):
    existing_user = (
        db.query(User)
        .filter(or_(User.username == user_data.username, User.email == user_data.email))
        .first()
    )

    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")

    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", status_code=200)
def login(user_data: UserLoginSchema, db: Session = Depends(get_db_session)):
    user = db.query(User).filter(User.username == user_data.username).first()

    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token({"sub": user.username})
    return {"access_token": token}


@router.post("/me/avatar", status_code=200)
def add_avatar(
    db: Session = Depends(get_db_session),
    user: User = Depends(get_current_user),
    avatar: UploadFile = File(...),
):
    current_user = db.query(User).filter(User.id == user.id).first()
    if not current_user:
        raise HTTPException(status_code=404, detail="User not found")
    try:
        avatar_name = save_avatar_in_storage(avatar)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    current_user.avatar_filename = avatar_name
    db.commit()
    db.refresh(current_user)
    return {"avatar_url": f"/media/avatars/{avatar_name}"}
