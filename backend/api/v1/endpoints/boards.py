from typing import Literal

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select, or_
from sqlalchemy.orm import selectinload

from api.deps import BoardWithAccess, CurrentUser, SessionDep, BoardWithEdit, BoardWithOwner
from api.utils import get_user_permission, check_board_access
from models.access import Access
from models.board import Board
from models.permission import Permission
from models.sticker import Sticker
from schemas.board import (
    BoardCreate,
    BoardDetail,
    BoardListResponse,
    BoardResponse,
    BoardSummary,
    StickerResponse,
    BoardUpdate,
)

router = APIRouter()


@router.post(
    "/",
    response_model=BoardResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание новой доски",
    description="Создание новой доски для текущего пользователя",
)
async def create_board(
        board_data: BoardCreate,
        current_user: CurrentUser,
        db: SessionDep,
) -> BoardResponse:
    """
    Создание новой доски.

    - title: Название доски (обязательно, 1-200 символов)
    - description: Описание доски (опционально, до 1000 символов)
    - backgroundColor: Цвет фона доски в hex формате (опционально)
    """
    new_board = Board(
        creator_id=current_user.user_id,
        title=board_data.title,
        description=board_data.description,
        background_color=board_data.backgroundColor,
        is_public=False,
    )
    db.add(new_board)
    await db.commit()
    await db.refresh(new_board, ["creator"])

    return BoardResponse(
        boardId=new_board.board_id,
        title=new_board.title or "",
        description=new_board.description,
        ownerId=new_board.creator_id,
        ownerName=current_user.login,
        backgroundColor=new_board.background_color,
        createdAt=new_board.created_at,
        updatedAt=new_board.updated_at,
    )


@router.get(
    "/",
    response_model=BoardListResponse,
    summary="Получение списка досок",
    description="Получение списка досок текущего пользователя (собственных и расшаренных)",
)
async def get_boards(
        current_user: CurrentUser,
        db: SessionDep,
        board_filter: Literal["own", "shared", "all"] = Query(
            default="all",
            alias="filter",
            description="Фильтр досок: own (только свои), shared (только расшаренные), all (все)",
        ),
        page: int = Query(default=1, ge=1, description="Номер страницы"),
        limit: int = Query(default=20, ge=1, le=100,
                           description="Количество элементов на странице"),
        sortBy: Literal["createdAt", "updatedAt", "title"] = Query(
            default="updatedAt", description="Поле для сортировки"
        ),
        sortOrder: Literal["asc", "desc"] = Query(
            default="desc", description="Порядок сортировки"),
) -> BoardListResponse:
    """
    Получение списка досок с фильтрацией, пагинацией и сортировкой.

    - filter: Фильтр досок (own/shared/all)
    - page: Номер страницы (начиная с 1)
    - limit: Количество элементов на странице (1-100)
    - sortBy: Поле для сортировки (createdAt/updatedAt/title)
    - sortOrder: Порядок сортировки (asc/desc)
    """
    # Строим базовый запрос в зависимости от фильтра
    if board_filter == "own":
        base_query = select(Board).where(
            Board.creator_id == current_user.user_id)
    elif board_filter == "shared":
        base_query = (
            select(Board)
            .join(Access, Board.board_id == Access.board_id)
            .where(Access.user_id == current_user.user_id)
            .where(Board.creator_id != current_user.user_id)
            .distinct()
        )
    else:  # all
        # Получаем все доски: свои + расшаренные
        conditions = [Board.creator_id == current_user.user_id]

        # Получаем ID расшаренных досок одним запросом
        shared_board_ids_query = select(Access.board_id).where(
            Access.user_id == current_user.user_id
        )
        shared_board_ids_result = await db.execute(shared_board_ids_query)
        shared_board_ids = [row[0] for row in shared_board_ids_result.all()]

        if shared_board_ids:
            conditions.append(Board.board_id.in_(shared_board_ids))

        base_query = select(Board).where(or_(*conditions))

    # Применяем сортировку
    if sortBy == "title":
        # Используем lower() для сортировки без учета регистра и coalesce для обработки NULL
        sort_column = func.lower(func.coalesce(Board.title, ""))
    else:
        sort_column = {
            "createdAt": Board.created_at,
            "updatedAt": Board.updated_at,
        }[sortBy]

    if sortOrder == "asc":
        base_query = base_query.order_by(sort_column.asc())
    else:
        base_query = base_query.order_by(sort_column.desc())

    # Применяем пагинацию
    offset = (page - 1) * limit
    base_query = base_query.offset(offset).limit(limit)

    # Загружаем создателя для каждой доски
    base_query = base_query.options(selectinload(Board.creator))

    # Выполняем запрос
    result = await db.execute(base_query)
    boards = result.scalars().unique().all()

    if not boards:
        return BoardListResponse(boards=[])

    # Получаем все Access для этих досок одним запросом (избегаем N+1)
    board_ids = [board.board_id for board in boards]
    accesses_query = select(Access).where(
        Access.board_id.in_(board_ids),
        Access.user_id == current_user.user_id,
    )
    accesses_result = await db.execute(accesses_query)
    accesses_cache = {
        access.board_id: access for access in accesses_result.scalars().all()}

    # Подсчитываем стикеры одним запросом (GROUP BY)
    sticker_counts_query = (
        select(Sticker.board_id, func.count(Sticker.sticker_id).label("count"))
        .where(Sticker.board_id.in_(board_ids))
        .group_by(Sticker.board_id)
    )
    sticker_counts_result = await db.execute(sticker_counts_query)
    sticker_counts = {row[0]: row[1] for row in sticker_counts_result.all()}

    # Подготавливаем данные для ответа
    board_summaries = []
    for board in boards:
        permission = await get_user_permission(current_user, board, db, accesses_cache=accesses_cache)

        if permission is None:
            continue

        sticker_count = sticker_counts.get(board.board_id, 0)
        creator_login = board.creator.login

        board_summaries.append(
            BoardSummary(
                boardId=board.board_id,
                title=board.title or "",
                description=board.description,
                ownerId=board.creator_id,
                ownerName=creator_login,
                permission=permission.value,
                stickerCount=sticker_count,
                updatedAt=board.updated_at,
            )
        )

    return BoardListResponse(boards=board_summaries)


@router.get(
    "/{board_id}",
    response_model=BoardDetail,
    summary="Получение доски по ID",
    description="Получение полной информации о доске, включая все стикеры",
)
async def get_board(
        board_with_access: BoardWithAccess,
        db: SessionDep,
) -> BoardDetail:
    """
    Получение доски по ID со всеми стикерами.

    - board_id: ID доски
    - Возвращает полную информацию о доске и все стикеры
    """
    board, permission = board_with_access

    await db.refresh(board, ["creator", "stickers"])

    if board.creator is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Board creator not found",
        )

    stickers = []
    for sticker in board.stickers:
        stickers.append(
            StickerResponse(
                stickerId=sticker.sticker_id,
                boardId=sticker.board_id,
                x=sticker.x,
                y=sticker.y,
                width=sticker.width,
                height=sticker.height,
                text=sticker.text,
                layerLevel=sticker.layer_level,
                color=sticker.color,
                createdBy=sticker.created_by,
                createdAt=sticker.created_at,
                updatedAt=sticker.updated_at,
            )
        )

    creator_login = board.creator.login

    return BoardDetail(
        boardId=board.board_id,
        title=board.title or "",
        description=board.description,
        ownerId=board.creator_id,
        ownerName=creator_login,
        backgroundColor=board.background_color,
        createdAt=board.created_at,
        updatedAt=board.updated_at,
        stickers=stickers,
        permission=permission.value,
    )


@router.put(
    "/{board_id}",
    response_model=BoardResponse,
    summary="Обновление доски",
    description="Обновление настроек доски текущим пользователем",
)
async def update_board(
        board_with_edit: BoardWithEdit,
        new_data: BoardUpdate,
        db: SessionDep,
) -> BoardResponse:
    """
    Обновление существующей доски.

    - board_id: ID доски
    - title: Новое название доски (обязательно, 1-200 символов)
    - description: Новое описание доски (опционально, до 1000 символов)
    - backgroundColor: Новый цвет фона доски в hex формате (опционально)
    """

    board, _ = board_with_edit

    if new_data.title is not None:
        board.title = new_data.title
    if new_data.description is not None:
        board.description = new_data.description
    if new_data.backgroundColor is not None:
        board.background_color = new_data.backgroundColor

    await db.commit()
    await db.refresh(board, ["creator"])

    if board.creator is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Board creator not found",
        )

    return BoardResponse(
        boardId=board.board_id,
        title=board.title or "",
        description=board.description,
        ownerId=board.creator_id,
        ownerName=board.creator.login,
        backgroundColor=board.background_color,
        createdAt=board.created_at,
        updatedAt=board.updated_at,
    )


@router.delete(
    "/{board_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление доски",
    description="Удаление доски владельцем",
)
async def delete_board(
        board_with_owner: BoardWithOwner,
        db: SessionDep,
):
    """
    Удаление доски по ID.

    - board_id: ID доски
    """
    board, _ = board_with_owner

    await db.delete(board)
    await db.commit()
