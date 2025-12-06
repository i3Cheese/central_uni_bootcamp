from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, ForeignKey, DateTime, func

if TYPE_CHECKING:
    from .board import Board
    from .user import User


class Sticker(Base):
    __tablename__ = "stickers"

    sticker_id: Mapped[int] = mapped_column("sticker_id", primary_key=True, index=True)
    board_id: Mapped[int] = mapped_column(
        ForeignKey("boards.board_id", ondelete="CASCADE"), nullable=False
    )
    created_by: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    layer_level: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str | None] = mapped_column(String, nullable=True)
    width: Mapped[float | None] = mapped_column(Float, nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)
    color: Mapped[str] = mapped_column(String, default="#FFEB3B", nullable=False)
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
    board: Mapped["Board"] = relationship("Board", back_populates="stickers")
    creator: Mapped["User"] = relationship("User", foreign_keys=[created_by], overlaps="created_stickers")
