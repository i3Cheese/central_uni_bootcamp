from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class StickerCreate(BaseModel):
    """Схема запроса на создание стикера."""

    x: float = Field(..., description="Координата X стикера на доске", example=100.5)
    y: float = Field(..., description="Координата Y стикера на доске", example=200.3)
    width: float | None = Field(
        default=200,
        ge=50,
        le=1000,
        description="Ширина стикера",
        example=200,
    )
    height: float | None = Field(
        default=200,
        ge=50,
        le=1000,
        description="Высота стикера",
        example=200,
    )
    color: str | None = Field(
        default="#FFEB3B",
        pattern="^#[0-9A-Fa-f]{6}$",
        description="Цвет стикера (hex формат)",
        example="#FFEB3B",
    )
    text: str | None = Field(
        default="",
        max_length=5000,
        description="Текстовое содержимое стикера",
        example="Текст стикера",
    )
    layerLevel: int = Field(
        default=0,
        description="Уровень слоя для определения порядка наложения",
        example=1,
    )

    @field_validator("color")
    @classmethod
    def validate_color(cls, v: str | None) -> str | None:
        if v is not None and not v.startswith("#"):
            raise ValueError("Color must be in hex format (e.g., #FFFFFF)")
        return v


class StickerResponse(BaseModel):
    """Схема ответа с информацией о стикере."""

    stickerId: int = Field(..., description="Уникальный идентификатор стикера", examples=[1])
    boardId: int = Field(..., description="ID доски, к которой относится стикер", examples=[1])
    x: float = Field(..., description="Координата X стикера на доске", examples=[100.5])
    y: float = Field(..., description="Координата Y стикера на доске", examples=[200.3])
    width: float = Field(..., description="Ширина стикера", examples=[200.0])
    height: float = Field(..., description="Высота стикера", examples=[200.0])
    text: str | None = Field(default=None, description="Текст стикера", examples=["Текст стикера"])
    layerLevel: int = Field(..., description="Уровень слоя для порядка наложения", examples=[1])
    color: str = Field(..., description="Цвет стикера (hex)", examples=["#FFEB3B"])
    createdBy: int = Field(..., description="ID создателя", examples=[1])
    createdAt: datetime = Field(..., description="Дата создания", examples=["2024-01-15T10:30:00Z"])
    updatedAt: datetime = Field(..., description="Дата обновления", examples=["2024-01-15T14:25:00Z"])

    model_config = {"from_attributes": True}
