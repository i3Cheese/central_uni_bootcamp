from datetime import datetime

from pydantic import BaseModel, Field

from models.permission import Permission


class ShareRequest(BaseModel):
    """Схема запроса на предоставление доступа."""

    userLogin: str = Field(
        ...,
        description="Логин пользователя, которому предоставляется доступ",
        examples=["user2@example.com"],
    )
    permission: Permission = Field(
        ...,
        description="Уровень доступа: view (только просмотр), edit (просмотр и редактирование)",
        examples=[Permission.EDIT],
    )


class ShareResponse(BaseModel):
    """Схема ответа при предоставлении доступа."""

    boardId: int = Field(..., description="ID доски", examples=[1])
    userId: int = Field(..., description="ID пользователя", examples=[2])
    permission: Permission = Field(
        ..., description="Уровень доступа", examples=[Permission.EDIT]
    )
    grantedAt: datetime = Field(
        ...,
        description="Дата и время предоставления доступа",
        examples=["2024-01-15T10:30:00Z"],
    )
    grantedBy: int = Field(
        ..., description="ID пользователя, предоставившего доступ", examples=[1]
    )


class ShareInfo(BaseModel):
    """Схема информации о доступе пользователя к доске."""

    userId: int = Field(..., description="ID пользователя", examples=[2])
    userLogin: str = Field(
        ..., description="Логин пользователя", examples=["user2@example.com"]
    )
    permission: Permission = Field(
        ..., description="Уровень доступа", examples=[Permission.EDIT]
    )
    grantedAt: datetime = Field(
        ...,
        description="Дата и время предоставления доступа",
        examples=["2024-01-15T10:30:00Z"],
    )

    model_config = {"from_attributes": True}


class ShareListResponse(BaseModel):
    """Схема ответа со списком пользователей с доступом."""

    boardId: int = Field(..., description="ID доски", examples=[1])
    shares: list[ShareInfo] = Field(..., description="Список пользователей с доступом")


class RevokeShareRequest(BaseModel):
    """Схема запроса на отзыв доступа."""

    userLogin: str = Field(
        ...,
        description="Логин пользователя, у которого отзывается доступ",
        examples=["user2@example.com"],
    )
