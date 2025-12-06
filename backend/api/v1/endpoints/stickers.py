from fastapi import APIRouter, HTTPException, Path, status
from sqlalchemy import select

from api.deps import BoardWithEdit, CurrentUser, SessionDep
from models.sticker import Sticker
from schemas.stickers import (
    StickerCreate,
    StickerResponse,
    StickerUpdate,
)

router = APIRouter()


@router.post(
    "/{board_id}/stickers",
    response_model=StickerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового стикера",
    description="Создание нового стикера на доске",
)
async def create_sticker(
        sticker_data: StickerCreate,
        board_with_edit: BoardWithEdit,
        current_user: CurrentUser,
        db: SessionDep,
) -> StickerResponse:
    """
    Создание нового стикера на доске.

    - board_id: id доски
    - x: Координата X стикера на доске (обязательно)
    - y: Координата Y стикера на доске (обязательно)
    - width: Ширина стикера (необязательно, по умолчанию 200, диапазон 50–1000)
    - height: Высота стикера (необязательно, по умолчанию 200, диапазон 50–1000)
    - color: Цвет стикера в hex формате (необязательно, по умолчанию "#FFEB3B")
    - text: Текстовое содержимое стикера (необязательно, максимум 5000 символов)
    - layerLevel: Уровень слоя для порядка наложения (необязательно, по умолчанию 0)
    """
    board, _ = board_with_edit

    new_sticker = Sticker(
        board_id=board.board_id,
        x=sticker_data.x,
        y=sticker_data.y,
        width=sticker_data.width,
        height=sticker_data.height,
        color=sticker_data.color,
        text=sticker_data.text,
        layer_level=sticker_data.layerLevel,
        created_by=current_user.user_id
    )

    db.add(new_sticker)
    await db.commit()
    await db.refresh(new_sticker)

    return StickerResponse(
        stickerId=new_sticker.sticker_id,
        boardId=new_sticker.board_id,
        x=new_sticker.x,
        y=new_sticker.y,
        width=new_sticker.width,
        height=new_sticker.height,
        color=new_sticker.color,
        text=new_sticker.text,
        layerLevel=new_sticker.layer_level,
        createdBy=new_sticker.created_by,
        createdAt=new_sticker.created_at,
        updatedAt=new_sticker.updated_at,
    )


@router.patch(
    "/{board_id}/stickers/{sticker_id}",
    response_model=StickerResponse,
    summary="Обновление стикера",
    description="Обновление параметров стикера (координаты, размер, цвет, текст, уровень слоя)",
)
async def update_sticker(
    board_with_edit: BoardWithEdit,
    sticker_data: StickerUpdate,
    db: SessionDep,
    sticker_id: int = Path(..., description="ID стикера"),
) -> StickerResponse:
    """
    Обновление существующего стикера на доске.

    - board_id: ID доски
    - sticker_id: ID стикера
    - Все поля опциональны - обновляются только переданные
    """
    board, _ = board_with_edit

    result = await db.execute(
        select(Sticker).where(
            Sticker.sticker_id == sticker_id,
            Sticker.board_id == board.board_id,
        )
    )
    sticker = result.scalar_one_or_none()

    if sticker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sticker not found",
        )

    if sticker_data.x is not None:
        sticker.x = sticker_data.x
    if sticker_data.y is not None:
        sticker.y = sticker_data.y
    if sticker_data.width is not None:
        sticker.width = sticker_data.width
    if sticker_data.height is not None:
        sticker.height = sticker_data.height
    if sticker_data.color is not None:
        sticker.color = sticker_data.color
    if sticker_data.text is not None:
        sticker.text = sticker_data.text
    if sticker_data.layerLevel is not None:
        sticker.layer_level = sticker_data.layerLevel

    await db.commit()
    await db.refresh(sticker)

    return StickerResponse(
        stickerId=sticker.sticker_id,
        boardId=sticker.board_id,
        x=sticker.x,
        y=sticker.y,
        width=sticker.width,
        height=sticker.height,
        color=sticker.color,
        text=sticker.text,
        layerLevel=sticker.layer_level,
        createdBy=sticker.created_by,
        createdAt=sticker.created_at,
        updatedAt=sticker.updated_at,
    )


@router.delete(
    "/{board_id}/stickers/{sticker_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Удаление стикера",
    description="Удаление стикера с доски",
)
async def delete_sticker(
    board_with_edit: BoardWithEdit,
    db: SessionDep,
    sticker_id: int = Path(..., description="ID стикера"),
) -> None:
    """
    Удаление стикера с доски.

    - board_id: ID доски
    - sticker_id: ID стикера
    """
    board, _ = board_with_edit

    result = await db.execute(
        select(Sticker).where(
            Sticker.sticker_id == sticker_id,
            Sticker.board_id == board.board_id,
        )
    )
    sticker = result.scalar_one_or_none()

    if sticker is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Sticker not found",
        )

    await db.delete(sticker)
    await db.commit()
