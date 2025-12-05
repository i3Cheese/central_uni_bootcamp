from __future__ import annotations

from typing import TYPE_CHECKING

from core.database import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint

if TYPE_CHECKING:
    from .user import User
    from .board import Board


class Access(Base):
    __tablename__ = "accesses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    board_id: Mapped[int] = mapped_column(ForeignKey("boards.id"), nullable=False)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="accesses")
    board: Mapped["Board"] = relationship("Board", back_populates="accesses")

    __table_args__ = (
        UniqueConstraint("user_id", "board_id", name="uq_user_board"),
    )
