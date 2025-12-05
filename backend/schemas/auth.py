from datetime import datetime
from uuid import UUID

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

    userId: UUID = Field(
        ...,
        description="Уникальный идентификатор пользователя",
        examples=["550e8400-e29b-41d4-a716-446655440000"],
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

