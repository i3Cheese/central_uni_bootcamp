from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, DateTime, ForeignKey, func

if TYPE_CHECKING:
    from .user import User
    from .access import Access
    from .sticker import Sticker


class Board(Base):
    __tablename__ = "boards"

    board_id: Mapped[int] = mapped_column("board_id", primary_key=True, index=True)
    creator_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    background_color: Mapped[str | None] = mapped_column(String, nullable=True)
    is_public: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

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
