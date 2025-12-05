from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from api.deps import SessionDep
from models.user import User
from schemas.user import UserCreate, User as UserSchema

router = APIRouter()


@router.post("/", response_model=UserSchema)
async def create_user(user: UserCreate, db: SessionDep):
    result = await db.execute(select(User).where(User.login == user.login))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="Login already registered")
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = User(login=user.login, hash_password=fake_hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserSchema])
async def read_users(db: SessionDep, skip: int = 0, limit: int = 100):
    result = await db.execute(select(User).offset(skip).limit(limit))
    users = result.scalars().all()
    return users


@router.get("/{user_id}", response_model=UserSchema)
async def read_user(user_id: int, db: SessionDep):
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalar_one_or_none()
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
