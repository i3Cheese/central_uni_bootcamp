from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.access import Access
from models.board import Board
from models.permission import Permission
from models.user import User


async def get_user_permission(
    user: User,
    board: Board,
    db: AsyncSession,
    accesses_cache: dict[int, Access] | None = None,
) -> Permission | None:
    """
    Определяет права пользователя на доску.

    Args:
        user: Пользователь
        board: Доска
        db: Сессия базы данных
        accesses_cache: Опциональный кэш Access по board_id для оптимизации

    Returns:
        Permission | None: Уровень прав или None если нет доступа
    """
    if board.creator_id == user.user_id:
        return Permission.OWNER

    # Используем кэш если передан, иначе делаем запрос
    if accesses_cache is not None:
        access = accesses_cache.get(board.board_id)
    else:
        result = await db.execute(
            select(Access).where(
                Access.board_id == board.board_id,
                Access.user_id == user.user_id,
            )
        )
        access = result.scalar_one_or_none()

    if access:
        return access.permission

    if board.is_public:
        return Permission.VIEW

    return None


async def check_board_access(
    user: User,
    board: Board,
    db: AsyncSession,
    required_permission: Permission | None = None,
) -> Permission:
    """
    Проверяет доступ пользователя к доске и возвращает его права.

    Args:
        user: Пользователь
        board: Доска
        db: Сессия базы данных
        required_permission: Минимальный требуемый уровень прав (None = любой доступ)

    Returns:
        Permission: Уровень прав пользователя

    Raises:
        HTTPException: Если нет доступа или недостаточно прав
    """
    from fastapi import HTTPException, status

    permission = await get_user_permission(user, board, db)

    if permission is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No access to this board",
        )

    # Проверяем достаточность прав
    if required_permission:
        permission_hierarchy: dict[Permission, int] = {
            Permission.VIEW: 1,
            Permission.EDIT: 2,
            Permission.OWNER: 3,
        }

        user_level = permission_hierarchy.get(permission, 0)
        required_level = permission_hierarchy.get(required_permission, 0)

        if user_level < required_level:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Requires {required_permission.value} permission, but user has {permission.value}",
            )

    return permission
