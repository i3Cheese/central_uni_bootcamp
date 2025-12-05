from datetime import datetime

from pydantic import BaseModel, Field


class ShareRequest(BaseModel):
    """Схема запроса на предоставление доступа."""

    userId: int = Field(..., description="ID пользователя, которому предоставляется доступ", examples=[2])
    permission: str = Field(
        ...,
        description="Уровень доступа: view (только просмотр), edit (просмотр и редактирование)",
        examples=["edit"],
    )


class ShareResponse(BaseModel):
    """Схема ответа при предоставлении доступа."""

    boardId: int = Field(..., description="ID доски", examples=[1])
    userId: int = Field(..., description="ID пользователя", examples=[2])
    permission: str = Field(..., description="Уровень доступа", examples=["edit"])
    grantedAt: datetime = Field(..., description="Дата и время предоставления доступа", examples=["2024-01-15T10:30:00Z"])
    grantedBy: int = Field(..., description="ID пользователя, предоставившего доступ", examples=[1])


class UpdateShareRequest(BaseModel):
    """Схема запроса на изменение уровня доступа."""

    permission: str = Field(
        ...,
        description="Новый уровень доступа: view (только просмотр), edit (просмотр и редактирование)",
        examples=["edit"],
    )


class UpdateShareResponse(BaseModel):
    """Схема ответа при изменении уровня доступа."""

    boardId: int = Field(..., description="ID доски", examples=[1])
    userId: int = Field(..., description="ID пользователя", examples=[2])
    permission: str = Field(..., description="Новый уровень доступа", examples=["edit"])
    updatedAt: datetime = Field(..., description="Дата и время обновления", examples=["2024-01-15T12:00:00Z"])


class ShareInfo(BaseModel):
    """Схема информации о доступе пользователя к доске."""

    userId: int = Field(..., description="ID пользователя", examples=[2])
    userLogin: str = Field(..., description="Логин пользователя", examples=["user2@example.com"])
    permission: str = Field(..., description="Уровень доступа", examples=["edit"])
    grantedAt: datetime = Field(..., description="Дата и время предоставления доступа", examples=["2024-01-15T10:30:00Z"])

    model_config = {"from_attributes": True}


class ShareListResponse(BaseModel):
    """Схема ответа со списком пользователей с доступом."""

    boardId: int = Field(..., description="ID доски", examples=[1])
    shares: list[ShareInfo] = Field(..., description="Список пользователей с доступом")

