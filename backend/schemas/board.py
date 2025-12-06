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


class BoardSummary(BaseModel):
    """Схема краткой информации о доске для списка."""

    boardId: int = Field(..., description="Уникальный идентификатор доски", examples=[1])
    title: str = Field(..., description="Название доски", examples=["Проектирование системы"])
    description: str | None = Field(
        default=None, description="Описание доски", examples=["Доска для обсуждения архитектуры"]
    )
    ownerId: int = Field(..., description="ID владельца доски", examples=[1])
    ownerName: str | None = Field(
        default=None, description="Логин владельца доски", examples=["user@example.com"]
    )
    permission: str = Field(
        ...,
        description="Права текущего пользователя на доску",
        examples=["owner"],
    )
    stickerCount: int = Field(
        default=0, description="Количество стикеров на доске", examples=[15]
    )
    updatedAt: datetime = Field(
        ..., description="Дата и время последнего обновления", examples=["2024-01-15T14:25:00Z"]
    )

    model_config = {"from_attributes": True}


class BoardListResponse(BaseModel):
    """Схема ответа со списком досок."""

    boards: list[BoardSummary] = Field(..., description="Список досок")


class StickerResponse(BaseModel):
    """Схема ответа со стикером."""

    stickerId: int = Field(..., description="Уникальный идентификатор стикера", examples=[1])
    boardId: int = Field(..., description="ID доски", examples=[1])
    x: float = Field(..., description="Координата X", examples=[100.5])
    y: float = Field(..., description="Координата Y", examples=[200.3])
    width: float | None = Field(default=None, description="Ширина стикера", examples=[200.0])
    height: float | None = Field(default=None, description="Высота стикера", examples=[200.0])
    text: str | None = Field(default=None, description="Текст стикера", examples=["Текст стикера"])
    layerLevel: int = Field(..., description="Уровень слоя для порядка наложения", examples=[1])
    color: str = Field(..., description="Цвет стикера (hex)", examples=["#FFEB3B"])
    createdBy: int = Field(..., description="ID создателя", examples=[1])
    createdAt: datetime = Field(..., description="Дата создания", examples=["2024-01-15T10:30:00Z"])
    updatedAt: datetime = Field(..., description="Дата обновления", examples=["2024-01-15T14:25:00Z"])

    model_config = {"from_attributes": True}


class BoardDetail(BaseModel):
    """Схема детальной информации о доске со стикерами."""

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
    stickers: list[StickerResponse] = Field(
        default_factory=list, description="Список всех стикеров на доске"
    )
    permission: str = Field(
        ...,
        description="Права текущего пользователя на доску",
        examples=["owner"],
    )

    model_config = {"from_attributes": True}


class BoardUpdate(BaseModel):
    """Схема запроса на обновление доски."""

    title: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Обновленное название доски",
        examples=["Обновленное название"],
    )
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="Обновленное описание доски",
        examples=["Обновленное описание"],
    )
    backgroundColor: str | None = Field(
        default=None,
        pattern="^#[0-9A-Fa-f]{6}$",
        description="Обновленный цвет фона доски (hex формат)",
        examples=["#F0F0F0"],
    )

    @field_validator("backgroundColor")
    @classmethod
    def validate_background_color(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith("#"):
            raise ValueError("Background color must be in hex format (e.g., #FFFFFF)")
        return v