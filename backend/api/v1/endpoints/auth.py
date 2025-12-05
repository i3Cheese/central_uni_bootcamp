from datetime import datetime, timezone
from uuid import uuid4

import bcrypt
from fastapi import APIRouter, HTTPException, status

from schemas.auth import RegisterRequest, RegisterResponse, ErrorResponse


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
async def register(request: RegisterRequest) -> RegisterResponse:
    """
    Регистрация нового пользователя.

    - **login**: Уникальный логин пользователя (3-50 символов)
    - **password**: Пароль (8-100 символов)
    """
    # TODO: Проверить, существует ли пользователь с таким логином в БД
    # Пример:
    # existing_user = await db.get_user_by_login(request.login)
    # if existing_user:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail=ErrorResponse(
    #             error="USER_EXISTS",
    #             message="Пользователь с таким логином уже существует",
    #             details={"field": "login", "reason": "Логин уже занят"},
    #         ).model_dump(),
    #     )
    user_exists = False  # TODO: Заменить на реальную проверку в БД
    if user_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "USER_EXISTS",
                "message": "Пользователь с таким логином уже существует",
                "details": {"field": "login", "reason": "Логин уже занят"},
            },
        )

    # Хешируем пароль
    hashed_password = hash_password(request.password)

    # TODO: Сохранить пользователя в БД
    # Пример:
    # new_user = await db.create_user(
    #     login=request.login,
    #     hashed_password=hashed_password,
    # )
    # return RegisterResponse(
    #     userId=new_user.id,
    #     login=new_user.login,
    #     createdAt=new_user.created_at,
    # )

    # Заглушка: возвращаем фейковые данные
    return RegisterResponse(
        userId=uuid4(),  # TODO: Заменить на реальный ID из БД
        login=request.login,
        createdAt=datetime.now(timezone.utc),  # TODO: Заменить на реальную дату из БД
    )

