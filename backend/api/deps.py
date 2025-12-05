from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, Path, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.utils import check_board_access
from core.database import AsyncSessionLocal
from core.security import decode_access_token
from models.board import Board
from models.permission import Permission
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: SessionDep = Depends(),
) -> User:
    """
    Получает текущего пользователя из JWT токена.
    
    Args:
        token: JWT токен из заголовка Authorization
        db: Сессия базы данных
        
    Returns:
        User: Объект пользователя
        
    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.user_id == user_id_int))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_board_by_id(
    board_id: int = Path(..., description="ID доски"),
    db: SessionDep = Depends(),
) -> Board:
    """
    Получает доску по ID.
    
    Args:
        board_id: ID доски
        db: Сессия базы данных
        
    Returns:
        Board: Объект доски
        
    Raises:
        HTTPException: Если доска не найдена
    """
    result = await db.execute(select(Board).where(Board.board_id == board_id))
    board = result.scalar_one_or_none()
    
    if board is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Board not found",
        )
    
    return board


async def get_board_with_access(
    board: Board = Depends(get_board_by_id),
    current_user: CurrentUser = Depends(),
    db: SessionDep = Depends(),
) -> tuple[Board, Permission]:
    """
    Получает доску и проверяет доступ пользователя к ней.
    
    Returns:
        tuple[Board, Permission]: Доска и уровень прав пользователя
        
    Raises:
        HTTPException: Если доска не найдена или нет доступа
    """
    permission = await check_board_access(current_user, board, db)
    return board, permission


async def require_board_owner(
    board: Board = Depends(get_board_by_id),
    current_user: CurrentUser = Depends(),
    db: SessionDep = Depends(),
) -> tuple[Board, Permission]:
    """
    Проверяет, что пользователь является владельцем доски.
    
    Returns:
        tuple[Board, Permission]: Доска и уровень прав пользователя
        
    Raises:
        HTTPException: Если нет доступа или пользователь не владелец
    """
    permission = await check_board_access(
        current_user, board, db, required_permission=Permission.OWNER
    )
    return board, permission


async def require_board_edit(
    board: Board = Depends(get_board_by_id),
    current_user: CurrentUser = Depends(),
    db: SessionDep = Depends(),
) -> tuple[Board, Permission]:
    """
    Проверяет, что пользователь имеет права на редактирование доски (edit или owner).
    
    Returns:
        tuple[Board, Permission]: Доска и уровень прав пользователя
        
    Raises:
        HTTPException: Если нет доступа или недостаточно прав
    """
    permission = await check_board_access(
        current_user, board, db, required_permission=Permission.EDIT
    )
    return board, permission

BoardWithAccess = Annotated[tuple[Board, Permission], Depends(get_board_with_access)]
BoardWithOwner = Annotated[tuple[Board, Permission], Depends(require_board_owner)]
BoardWithEdit = Annotated[tuple[Board, Permission], Depends(require_board_edit)]
