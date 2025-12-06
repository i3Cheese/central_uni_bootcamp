from fastapi import APIRouter, status

from api.deps import SessionDep, BoardWithEdit, CurrentUser
from models.sticker import Sticker
from schemas.stickers import (
    StickerCreate,
    StickerResponse
)

router = APIRouter()


@router.post(
    "/{board_id}/stickers",
    response_model=StickerResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Создание нового стикера",
    description="Создание нового стикера на доске",
)
async def create_board(
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
    - layerLevel: Уровень слоя для порядка наложения (обязательно)
    """
    board, permission = board_with_edit

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
