import pytest
import uuid
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_sticker(client: AsyncClient):
    """Тест создания стикера."""
    # Создаем пользователя и доску
    login = f"stickeruser_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post(
        "/api/v1/auth/register",
        json={"login": login, "password": password},
    )
    
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"login": login, "password": password},
    )
    token = login_response.json()["token"]
    
    # Создаем доску
    board_response = await client.post(
        "/api/v1/boards/",
        json={"title": f"Sticker Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {token}"},
    )
    board_id = board_response.json()["boardId"]
    
    # Создаем стикер
    response = await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={
            "x": 100.5,
            "y": 200.3,
            "width": 250,
            "height": 150,
            "color": "#FFEB3B",
            "text": f"Test Sticker {uuid.uuid4().hex[:8]}",
            "layerLevel": 1,
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert "stickerId" in data
    assert data["boardId"] == board_id
    assert data["x"] == 100.5
    assert data["y"] == 200.3


@pytest.mark.asyncio
async def test_update_sticker(client: AsyncClient):
    """Тест обновления стикера."""
    # Создаем пользователя, доску и стикер
    login = f"updatesticker_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post(
        "/api/v1/auth/register",
        json={"login": login, "password": password},
    )
    
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"login": login, "password": password},
    )
    token = login_response.json()["token"]
    
    board_response = await client.post(
        "/api/v1/boards/",
        json={"title": f"Update Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {token}"},
    )
    board_id = board_response.json()["boardId"]
    
    sticker_response = await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={"x": 100, "y": 200, "text": "Original"},
        headers={"Authorization": f"Bearer {token}"},
    )
    sticker_id = sticker_response.json()["stickerId"]
    
    # Обновляем стикер
    new_text = f"Updated {uuid.uuid4().hex[:8]}"
    response = await client.patch(
        f"/api/v1/boards/{board_id}/stickers/{sticker_id}",
        json={"x": 150.0, "y": 250.0, "text": new_text, "color": "#FF5722"},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["x"] == 150.0
    assert data["y"] == 250.0
    assert data["text"] == new_text
    assert data["color"] == "#FF5722"


@pytest.mark.asyncio
async def test_delete_sticker(client: AsyncClient):
    """Тест удаления стикера."""
    # Создаем пользователя, доску и стикер
    login = f"deletesticker_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    await client.post(
        "/api/v1/auth/register",
        json={"login": login, "password": password},
    )
    
    login_response = await client.post(
        "/api/v1/auth/login",
        json={"login": login, "password": password},
    )
    token = login_response.json()["token"]
    
    board_response = await client.post(
        "/api/v1/boards/",
        json={"title": f"Delete Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {token}"},
    )
    board_id = board_response.json()["boardId"]
    
    sticker_response = await client.post(
        f"/api/v1/boards/{board_id}/stickers",
        json={"x": 100, "y": 200},
        headers={"Authorization": f"Bearer {token}"},
    )
    sticker_id = sticker_response.json()["stickerId"]
    
    # Удаляем стикер
    response = await client.delete(
        f"/api/v1/boards/{board_id}/stickers/{sticker_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 204

