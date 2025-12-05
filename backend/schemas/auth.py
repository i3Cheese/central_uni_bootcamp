from datetime import datetime

from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    """Схема запроса на регистрацию пользователя."""

    login: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Уникальный логин пользователя",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Пароль (минимум 8 символов)",
        examples=["SecurePass123!"],
    )


class RegisterResponse(BaseModel):
    """Схема ответа при успешной регистрации."""

    userId: int = Field(
        ...,
        description="Уникальный идентификатор пользователя",
        examples=[1],
    )
    login: str = Field(
        ...,
        description="Логин пользователя",
        examples=["user@example.com"],
    )
    createdAt: datetime = Field(
        ...,
        description="Дата и время создания аккаунта",
        examples=["2024-01-15T10:30:00Z"],
    )


class LoginRequest(BaseModel):
    """Схема запроса на вход в систему."""

    login: str = Field(
        ...,
        description="Логин пользователя",
        examples=["user@example.com"],
    )
    password: str = Field(
        ...,
        description="Пароль пользователя",
        examples=["SecurePass123!"],
    )


class LoginResponse(BaseModel):
    """Схема ответа при успешном входе."""

    userId: int = Field(
        ...,
        description="Уникальный идентификатор пользователя",
        examples=[1],
    )
    login: str = Field(
        ...,
        description="Логин пользователя",
        examples=["user@example.com"],
    )
    token: str = Field(
        ...,
        description="JWT токен для авторизации",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."],
    )
    expiresAt: datetime = Field(
        ...,
        description="Дата и время истечения токена",
        examples=["2024-01-16T10:30:00Z"],
    )


class ErrorResponse(BaseModel):
    """Схема ответа при ошибке."""

    error: str = Field(
        ...,
        description="Код ошибки",
        examples=["VALIDATION_ERROR"],
    )
    message: str = Field(
        ...,
        description="Человекочитаемое описание ошибки",
        examples=["Некорректные данные запроса"],
    )
    details: dict | None = Field(
        default=None,
        description="Дополнительная информация об ошибке",
        examples=[{"field": "login", "reason": "Логин уже занят"}],
    )

