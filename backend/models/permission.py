from enum import Enum


class Permission(str, Enum):
    """Уровни прав доступа к доске."""

    OWNER = "owner"
    VIEW = "view"
    EDIT = "edit"

