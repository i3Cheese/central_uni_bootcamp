from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from api.deps import BoardWithOwner, CurrentUser, SessionDep
from models.access import Access
from models.permission import Permission
from models.user import User
from schemas.sharing import (
    RevokeShareRequest,
    ShareInfo,
    ShareListResponse,
    ShareRequest,
    ShareResponse,
)

router = APIRouter()


@router.post(
    "/{board_id}/share",
    response_model=ShareResponse,
    status_code=status.HTTP_200_OK,
    summary="Предоставление или обновление доступа к доске",
    description="Выдача прав пользователю на доступ к доске. Если доступ уже существует, он будет обновлен.",
)
async def share_board(
    board_with_owner: BoardWithOwner,
    share_data: ShareRequest,
    current_user: CurrentUser,
    db: SessionDep,
) -> ShareResponse:
    """
    Предоставление или обновление доступа к доске.

    Если доступ для пользователя уже существует, он будет обновлен.

    - board_id: ID доски
    - userLogin: Логин пользователя, которому предоставляется доступ
    - permission: Уровень доступа (view или edit)
    """
    board, _ = board_with_owner

    # Проверяем, что пользователь существует по логину
    result = await db.execute(select(User).where(User.login == share_data.userLogin))
    target_user = result.scalar_one_or_none()
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "USER_NOT_FOUND", "message": "Пользователь не найден"},
        )

    # Нельзя предоставить доступ самому себе (он уже owner)
    if target_user.user_id == board.creator_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_REQUEST",
                "message": "Нельзя предоставить доступ владельцу доски",
            },
        )

    # Нельзя установить уровень доступа owner через API
    if share_data.permission == Permission.OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_PERMISSION",
                "message": "Нельзя установить уровень доступа owner",
            },
        )

    # Проверяем, не существует ли уже доступ
    existing_access_result = await db.execute(
        select(Access).where(
            Access.board_id == board.board_id,
            Access.user_id == target_user.user_id,
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
            userId=target_user.user_id,
            permission=existing_access.permission,
            grantedAt=existing_access.granted_at,
            grantedBy=existing_access.granted_by,
        )

    # Создаем новый доступ
    new_access = Access(
        board_id=board.board_id,
        user_id=target_user.user_id,
        permission=share_data.permission,
        granted_by=current_user.user_id,
    )
    db.add(new_access)
    await db.commit()
    await db.refresh(new_access)

    return ShareResponse(
        boardId=board.board_id,
        userId=target_user.user_id,
        permission=share_data.permission,
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


@router.delete(
    "/{board_id}/share",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Отзыв доступа к доске",
    description="Удаление прав пользователя на доступ к доске",
)
async def revoke_share(
    board_with_owner: BoardWithOwner,
    revoke_data: RevokeShareRequest,
    db: SessionDep,
) -> None:
    """
    Отзыв доступа пользователя к доске.

    - board_id: ID доски
    - userLogin: Логин пользователя, у которого отзывается доступ
    """
    board, _ = board_with_owner

    # Находим пользователя по логину
    user_result = await db.execute(
        select(User).where(User.login == revoke_data.userLogin)
    )
    target_user = user_result.scalar_one_or_none()
    if target_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "USER_NOT_FOUND", "message": "Пользователь не найден"},
        )

    # Нельзя отозвать доступ владельца
    if target_user.user_id == board.creator_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "INVALID_REQUEST",
                "message": "Нельзя отозвать доступ владельца доски",
            },
        )

    # Находим существующий доступ
    result = await db.execute(
        select(Access).where(
            Access.board_id == board.board_id,
            Access.user_id == target_user.user_id,
        )
    )
    access = result.scalar_one_or_none()

    if access is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "ACCESS_NOT_FOUND", "message": "Доступ не найден"},
        )

    await db.delete(access)
    await db.commit()
