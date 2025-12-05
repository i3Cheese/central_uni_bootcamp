from __future__ import annotations

from typing import TYPE_CHECKING

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Float, Integer, ForeignKey

if TYPE_CHECKING:
    from .board import Board


class Sticker(Base):
    __tablename__ = "stickers"

    sticker_id: Mapped[int] = mapped_column("sticker_id", primary_key=True, index=True)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.board_id"), nullable=False)
    x: Mapped[float] = mapped_column(Float, nullable=False)
    y: Mapped[float] = mapped_column(Float, nullable=False)
    layer_level: Mapped[int] = mapped_column(Integer, nullable=False)
    text: Mapped[str | None] = mapped_column(String, nullable=True)
    width: Mapped[float | None] = mapped_column(Float, nullable=True)
    height: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    board: Mapped["Board"] = relationship("Board", back_populates="stickers")
