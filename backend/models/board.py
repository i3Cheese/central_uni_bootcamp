from __future__ import annotations

from typing import TYPE_CHECKING

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey

if TYPE_CHECKING:
    from .user import User
    from .access import Access
    from .sticker import Sticker


class Board(Base):
    __tablename__ = "boards"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    background_color: Mapped[str | None] = mapped_column(String, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    creator: Mapped["User"] = relationship(
        "User", back_populates="created_boards", foreign_keys=[creator_id]
    )
    accesses: Mapped[list["Access"]] = relationship(
        "Access", back_populates="board"
    )
    stickers: Mapped[list["Sticker"]] = relationship(
        "Sticker", back_populates="board"
    )
