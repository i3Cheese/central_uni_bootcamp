"""
WebSocket endpoint for real-time board updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.utils import get_user_permission
from core.database import AsyncSessionLocal
from core.security import decode_access_token
from core.websocket import manager, WSEventType, create_ws_message
from models.board import Board
from models.user import User

router = APIRouter()


async def authenticate_websocket(token: str, db: AsyncSession) -> User | None:
    """
    Аутентификация WebSocket соединения по токену.
    
    Args:
        token: JWT токен
        db: Сессия базы данных
        
    Returns:
        User или None если аутентификация не удалась
    """
    if not token:
        return None
    
    payload = decode_access_token(token)
    if payload is None:
        return None
    
    user_id: str | None = payload.get("sub")
    if user_id is None:
        return None
    
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        return None
    
    result = await db.execute(select(User).where(User.user_id == user_id_int))
    user = result.scalar_one_or_none()
    return user


async def check_board_access_for_ws(
    user: User, 
    board_id: int, 
    db: AsyncSession
) -> tuple[Board | None, str | None]:
    """
    Проверка доступа пользователя к доске для WebSocket.
    
    Returns:
        tuple[Board | None, str | None]: (доска, уровень прав) или (None, None)
    """
    result = await db.execute(select(Board).where(Board.board_id == board_id))
    board = result.scalar_one_or_none()
    
    if board is None:
        return None, None
    
    permission = await get_user_permission(user, board, db)
    if permission is None:
        return None, None
    
    return board, permission.value


@router.websocket("/ws/boards/{board_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    board_id: int,
    token: str = Query(..., description="JWT токен для аутентификации"),
):
    """
    WebSocket endpoint для подключения к доске.
    
    Клиент должен передать токен как query параметр:
    ws://host/api/v1/ws/boards/{board_id}?token=JWT_TOKEN
    
    После подключения клиент будет получать события:
    - sticker_created: создан новый стикер
    - sticker_updated: обновлён стикер
    - sticker_deleted: удалён стикер
    - board_updated: обновлена доска
    - board_deleted: удалена доска
    - user_joined: пользователь присоединился к доске
    - user_left: пользователь покинул доску
    """
    async with AsyncSessionLocal() as db:
        # Аутентификация
        user = await authenticate_websocket(token, db)
        if user is None:
            await websocket.close(code=4001, reason="Authentication failed")
            return
        
        # Проверка доступа к доске
        board, permission = await check_board_access_for_ws(user, board_id, db)
        if board is None:
            await websocket.close(code=4003, reason="Board not found or access denied")
            return
        
        # Подключаем к менеджеру
        await manager.connect(websocket, board_id)
        
        # Уведомляем других о присоединении
        await manager.broadcast_to_board(
            board_id,
            create_ws_message(WSEventType.USER_JOINED, {
                "userId": user.user_id,
                "userLogin": user.login,
                "connectionCount": manager.get_connection_count(board_id),
            }),
            exclude=websocket
        )
        
        # Отправляем информацию о подключении самому клиенту
        await websocket.send_json({
            "type": "connected",
            "data": {
                "boardId": board_id,
                "userId": user.user_id,
                "permission": permission,
                "connectionCount": manager.get_connection_count(board_id),
            }
        })
        
        try:
            while True:
                # Ожидаем сообщения от клиента (ping/pong для поддержания соединения)
                data = await websocket.receive_json()
                
                # Обработка ping
                if data.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})
                    
        except WebSocketDisconnect:
            # Отключение клиента
            manager.disconnect(websocket, board_id)
            
            # Уведомляем других об отключении
            await manager.broadcast_to_board(
                board_id,
                create_ws_message(WSEventType.USER_LEFT, {
                    "userId": user.user_id,
                    "userLogin": user.login,
                    "connectionCount": manager.get_connection_count(board_id),
                })
            )
        except Exception:
            # Любая другая ошибка - отключаем
            manager.disconnect(websocket, board_id)

