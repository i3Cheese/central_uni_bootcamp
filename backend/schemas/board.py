from datetime import datetime

from pydantic import BaseModel, Field, field_validator


class BoardCreate(BaseModel):
    """Схема запроса на создание доски."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Название доски",
        examples=["Проектирование новой системы"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Описание доски",
        examples=["Доска для обсуждения архитектуры"],
    )
    backgroundColor: str | None = Field(
        default=None,
        pattern="^#[0-9A-Fa-f]{6}$",
        description="Цвет фона доски (hex формат)",
        examples=["#FFFFFF"],
    )

    @field_validator("backgroundColor")
    @classmethod
    def validate_background_color(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith("#"):
            raise ValueError("Background color must be in hex format (e.g., #FFFFFF)")
        return v


class BoardResponse(BaseModel):
    """Схема ответа с информацией о доске."""

    boardId: int = Field(..., description="Уникальный идентификатор доски", examples=[1])
    title: str = Field(..., description="Название доски", examples=["Проектирование системы"])
    description: str | None = Field(
        default=None, description="Описание доски", examples=["Доска для обсуждения архитектуры"]
    )
    ownerId: int = Field(..., description="ID владельца доски", examples=[1])
    ownerName: str | None = Field(
        default=None, description="Логин владельца доски", examples=["user@example.com"]
    )
    backgroundColor: str | None = Field(
        default=None, description="Цвет фона доски", examples=["#FFFFFF"]
    )
    createdAt: datetime = Field(
        ..., description="Дата и время создания", examples=["2024-01-15T10:30:00Z"]
    )
    updatedAt: datetime = Field(
        ..., description="Дата и время последнего обновления", examples=["2024-01-15T14:25:00Z"]
    )

    model_config = {"from_attributes": True}

