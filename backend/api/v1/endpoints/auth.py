from datetime import datetime, timedelta, timezone

import bcrypt
from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from api.deps import SessionDep
from core.config import settings
from core.security import create_access_token, verify_password
from models.user import User
from schemas.auth import (
    ErrorResponse,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    RegisterResponse,
)


def hash_password(password: str) -> str:
    """Хеширует пароль с использованием bcrypt."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")

router = APIRouter()


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Регистрация нового пользователя",
    description="Создание нового аккаунта пользователя",
    responses={
        400: {
            "model": ErrorResponse,
            "description": "Некорректные данные",
        },
        409: {
            "model": ErrorResponse,
            "description": "Пользователь с таким логином уже существует",
        },
    },
)
async def register(request: RegisterRequest, db: SessionDep) -> RegisterResponse:
    """
    Регистрация нового пользователя.

    - login: Уникальный логин пользователя (3-50 символов)
    - password: Пароль (8-100 символов)
    """
    # Проверяем, существует ли пользователь с таким логином
    result = await db.execute(select(User).where(User.login == request.login))
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "USER_EXISTS",
                "message": "Пользователь с таким логином уже существует",
                "details": {"field": "login", "reason": "Логин уже занят"},
            },
        )

    hashed_password = hash_password(request.password)

    new_user = User(
        login=request.login,
        hash_password=hashed_password,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return RegisterResponse(
        userId=new_user.user_id,
        login=new_user.login,
        createdAt=new_user.created_at,
    )


@router.post(
    "/login",
    response_model=LoginResponse,
    status_code=status.HTTP_200_OK,
    summary="Вход в систему",
    description="Аутентификация пользователя и получение токена",
    responses={
        401: {
            "model": ErrorResponse,
            "description": "Неверный логин или пароль",
        },
    },
)
async def login(request: LoginRequest, db: SessionDep) -> LoginResponse:
    """
    Вход в систему.

    - login: Логин пользователя
    - password: Пароль пользователя
    """
    result = await db.execute(select(User).where(User.login == request.login))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "INVALID_CREDENTIALS",
                "message": "Неверный логин или пароль",
            },
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.user_id), "login": user.login},
        expires_delta=access_token_expires,
    )

    expires_at = datetime.now(timezone.utc) + access_token_expires

    return LoginResponse(
        userId=user.user_id,
        login=user.login,
        token=access_token,
        expiresAt=expires_at,
    )

