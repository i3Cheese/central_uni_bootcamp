from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, DateTime, func

if TYPE_CHECKING:
    from .board import Board
    from .access import Access


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column("user_id", primary_key=True, index=True)
    login: Mapped[str] = mapped_column(String, unique=True, index=True)
    hash_password: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    # Relationships
    created_boards: Mapped[list["Board"]] = relationship(
        "Board", back_populates="creator", foreign_keys="Board.creator_id"
    )
    accesses: Mapped[list["Access"]] = relationship(
        "Access", back_populates="user", foreign_keys="Access.user_id"
    )
    granted_accesses: Mapped[list["Access"]] = relationship(
        "Access", foreign_keys="Access.granted_by"
    )
