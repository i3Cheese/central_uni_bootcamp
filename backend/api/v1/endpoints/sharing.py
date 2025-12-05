from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.deps import BoardWithOwner, CurrentUser, SessionDep
from models.access import Access
from models.permission import Permission
from models.user import User
from schemas.sharing import (
    ShareInfo,
    ShareListResponse,
    ShareRequest,
    ShareResponse,
    UpdateShareRequest,
    UpdateShareResponse,
)

router = APIRouter()


def validate_permission(value: str) -> None:
    """
    Валидирует уровень доступа.
    
    Args:
        value: Значение уровня доступа
        
    Raises:
        HTTPException: Если уровень доступа некорректен
    """
    if value not in Permission._value2member_map_:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_PERMISSION", "message": "Некорректный уровень доступа"},
        )
    if value == Permission.OWNER.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_PERMISSION", "message": "Нельзя установить уровень доступа owner"},
        )


@router.post(
    "/{board_id}/share",
    response_model=ShareResponse,
    status_code=status.HTTP_200_OK,
    summary="Предоставление доступа к доске",
    description="Выдача прав пользователю на доступ к доске",
)
async def share_board(
    board_with_owner: BoardWithOwner,
    share_data: ShareRequest,
    current_user: CurrentUser,
    db: SessionDep,
) -> ShareResponse:
    """
    Предоставление доступа к доске.
    
    - board_id: ID доски
    - userId: ID пользователя, которому предоставляется доступ
    - permission: Уровень доступа (view или edit)
    """
    board, _ = board_with_owner
    
    # Проверяем, что пользователь существует
    result = await db.execute(select(User).where(User.user_id == share_data.userId))
    target_user = result.scalar_one_or_none()
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "USER_NOT_FOUND", "message": "Пользователь не найден"},
        )
    
    # Нельзя предоставить доступ самому себе (он уже owner)
    if share_data.userId == board.creator_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_REQUEST", "message": "Нельзя предоставить доступ владельцу доски"},
        )
    
    validate_permission(share_data.permission)
    
    # Проверяем, не существует ли уже доступ
    existing_access_result = await db.execute(
        select(Access).where(
            Access.board_id == board.board_id,
            Access.user_id == share_data.userId,
        )
    )
    existing_access = existing_access_result.scalar_one_or_none()
    
    if existing_access:
        # Обновляем существующий доступ
        existing_access.permission = share_data.permission
        existing_access.granted_by = current_user.user_id
        existing_access.granted_at = datetime.now(timezone.utc)
        await db.commit()
        await db.refresh(existing_access)
        
        return ShareResponse(
            boardId=board.board_id,
            userId=share_data.userId,
            permission=existing_access.permission,
            grantedAt=existing_access.granted_at,
            grantedBy=existing_access.granted_by,
        )
    
    # Создаем новый доступ
    new_access = Access(
        board_id=board.board_id,
        user_id=share_data.userId,
        permission=share_data.permission,
        granted_by=current_user.user_id,
    )
    db.add(new_access)
    await db.commit()
    await db.refresh(new_access)
    
    return ShareResponse(
        boardId=board.board_id,
        userId=share_data.userId,
        permission=new_access.permission,
        grantedAt=new_access.granted_at,
        grantedBy=new_access.granted_by,
    )


@router.get(
    "/{board_id}/share",
    response_model=ShareListResponse,
    summary="Получение списка пользователей с доступом",
    description="Получение списка всех пользователей, имеющих доступ к доске",
)
async def get_board_shares(
    board_with_owner: BoardWithOwner,
    db: SessionDep,
) -> ShareListResponse:
    """
    Получение списка пользователей с доступом к доске.
    
    - board_id: ID доски
    - Возвращает список всех пользователей с доступом (кроме владельца)
    """
    board, _ = board_with_owner
    
    # Получаем все Access для этой доски с загрузкой пользователей
    result = await db.execute(
        select(Access)
        .where(Access.board_id == board.board_id)
        .options(selectinload(Access.user))
    )
    accesses = result.scalars().all()
    
    shares = []
    for access in accesses:
        if access.user is None:
            continue
        
        # Пропускаем владельца (он не в Access, у него автоматически OWNER)
        if access.user_id == board.creator_id:
            continue
        
        shares.append(
            ShareInfo(
                userId=access.user_id,
                userLogin=access.user.login,
                permission=access.permission,
                grantedAt=access.granted_at,
            )
        )
    
    return ShareListResponse(boardId=board.board_id, shares=shares)


@router.put(
    "/{board_id}/share/{user_id}",
    response_model=UpdateShareResponse,
    summary="Изменение уровня доступа",
    description="Обновление прав пользователя на доску",
)
async def update_share(
    board_with_owner: BoardWithOwner,
    update_data: UpdateShareRequest,
    db: SessionDep,
    user_id: int = Path(..., description="ID пользователя"),
) -> UpdateShareResponse:
    """
    Изменение уровня доступа пользователя к доске.
    
    - board_id: ID доски
    - user_id: ID пользователя
    - permission: Новый уровень доступа (view или edit)
    """
    board, _ = board_with_owner
    
    validate_permission(update_data.permission)
    
    # Нельзя изменить доступ владельца
    if user_id == board.creator_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_REQUEST", "message": "Нельзя изменить доступ владельца доски"},
        )
    
    # Находим существующий доступ
    result = await db.execute(
        select(Access).where(
            Access.board_id == board.board_id,
            Access.user_id == user_id,
        )
    )
    access = result.scalar_one_or_none()
    
    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "ACCESS_NOT_FOUND", "message": "Доступ не найден"},
        )
    
    # Обновляем уровень доступа
    access.permission = update_data.permission
    access.granted_by = board.creator_id
    access.granted_at = datetime.now(timezone.utc)  # Обновляем дату предоставления доступа
    await db.commit()
    await db.refresh(access)
    
    return UpdateShareResponse(
        boardId=board.board_id,
        userId=user_id,
        permission=access.permission,
        updatedAt=access.granted_at,
    )


@router.delete(
    "/{board_id}/share/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отзыв доступа к доске",
    description="Удаление прав пользователя на доступ к доске",
)
async def revoke_share(
    board_with_owner: BoardWithOwner,
    db: SessionDep,
    user_id: int = Path(..., description="ID пользователя"),
) -> None:
    """
    Отзыв доступа пользователя к доске.
    
    - board_id: ID доски
    - user_id: ID пользователя
    """
    board, _ = board_with_owner
    
    # Нельзя отозвать доступ владельца
    if user_id == board.creator_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "INVALID_REQUEST", "message": "Нельзя отозвать доступ владельца доски"},
        )
    
    # Находим существующий доступ
    result = await db.execute(
        select(Access).where(
            Access.board_id == board.board_id,
            Access.user_id == user_id,
        )
    )
    access = result.scalar_one_or_none()
    
    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "ACCESS_NOT_FOUND", "message": "Доступ не найден"},
        )
    
    # Удаляем доступ
    await db.delete(access)
    await db.commit()

