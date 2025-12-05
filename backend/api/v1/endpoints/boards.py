from fastapi import APIRouter, status

from api.deps import CurrentUser, SessionDep
from models.board import Board
from schemas.board import BoardCreate, BoardResponse

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
    await db.refresh(new_board)

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

