"""
WebSocket manager for real-time board updates.
"""

from typing import Dict, Set
from fastapi import WebSocket
import json


class ConnectionManager:
    """Менеджер WebSocket подключений для досок."""
    
    def __init__(self):
        # board_id -> set of websocket connections
        self.active_connections: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, board_id: int):
        """Подключение клиента к доске."""
        await websocket.accept()
        if board_id not in self.active_connections:
            self.active_connections[board_id] = set()
        self.active_connections[board_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, board_id: int):
        """Отключение клиента от доски."""
        if board_id in self.active_connections:
            self.active_connections[board_id].discard(websocket)
            if not self.active_connections[board_id]:
                del self.active_connections[board_id]
    
    async def broadcast_to_board(
        self, 
        board_id: int, 
        message: dict,
        exclude: WebSocket | None = None
    ):
        """
        Отправка сообщения всем подключённым к доске клиентам.
        
        Args:
            board_id: ID доски
            message: Сообщение для отправки
            exclude: WebSocket соединение, которое нужно исключить (отправитель)
        """
        if board_id not in self.active_connections:
            return
        
        disconnected = set()
        for connection in self.active_connections[board_id]:
            if connection == exclude:
                continue
            try:
                await connection.send_json(message)
            except Exception:
                disconnected.add(connection)
        
        # Удаляем отключённые соединения
        for conn in disconnected:
            self.active_connections[board_id].discard(conn)
    
    def get_connection_count(self, board_id: int) -> int:
        """Получить количество подключений к доске."""
        return len(self.active_connections.get(board_id, set()))


# Глобальный экземпляр менеджера
manager = ConnectionManager()


# Типы событий для WebSocket сообщений
class WSEventType:
    # Стикеры
    STICKER_CREATED = "sticker_created"
    STICKER_UPDATED = "sticker_updated"
    STICKER_DELETED = "sticker_deleted"
    
    # Доска
    BOARD_UPDATED = "board_updated"
    BOARD_DELETED = "board_deleted"
    
    # Пользователи
    USER_JOINED = "user_joined"
    USER_LEFT = "user_left"


def create_ws_message(event_type: str, data: dict) -> dict:
    """Создание структурированного WebSocket сообщения."""
    return {
        "type": event_type,
        "data": data
    }

