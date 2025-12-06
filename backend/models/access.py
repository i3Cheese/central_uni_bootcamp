from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from core.database import Base
from sqlalchemy import ForeignKey, DateTime, UniqueConstraint, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .permission import Permission

if TYPE_CHECKING:
    from .user import User
    from .board import Board


class Access(Base):
    __tablename__ = "accesses"

    access_id: Mapped[int] = mapped_column("access_id", primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.user_id"), nullable=False)
    board_id: Mapped[int] = mapped_column(
        ForeignKey("boards.board_id", ondelete="CASCADE"), nullable=False
    )
    permission: Mapped[Permission] = mapped_column(
        SQLEnum(Permission),
        nullable=False,
        default=Permission.VIEW,
        comment="Уровень доступа: view (только просмотр), edit (просмотр и редактирование)",
    )
    granted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    granted_by: Mapped[int] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
        comment="ID пользователя, предоставившего доступ",
    )

    # Relationships
    user: Mapped["User"] = relationship(
        "User", back_populates="accesses", foreign_keys=[user_id]
    )
    board: Mapped["Board"] = relationship("Board", back_populates="accesses")
    granter: Mapped["User"] = relationship(
        "User", foreign_keys=[granted_by], overlaps="granted_accesses"
    )

    __table_args__ = (UniqueConstraint("user_id", "board_id", name="uq_user_board"),)
