from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from api.deps import SessionDep
from models.user import User
from schemas.user import UserCreate, User as UserSchema

router = APIRouter()


@router.post("/", response_model=UserSchema)
def create_user(user: UserCreate, db: SessionDep):
    db_user = db.scalar(select(User).where(User.email == user.email))
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserSchema])
def read_users(db: SessionDep, skip: int = 0, limit: int = 100):
    users = db.scalars(select(User).offset(skip).limit(limit)).all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
def read_user(user_id: int, db: SessionDep):
    db_user = db.get(User, user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
