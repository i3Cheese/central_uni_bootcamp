import pytest
import uuid
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_create_board(client: AsyncClient):
    """Тест создания доски."""
    # Создаем пользователя и получаем токен
    login = f"boarduser_{uuid.uuid4().hex[:8]}@example.com"
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
    board_title = f"Test Board {uuid.uuid4().hex[:8]}"
    response = await client.post(
        "/api/v1/boards/",
        json={
            "title": board_title,
            "description": "Test description",
            "backgroundColor": "#FF5733",
        },
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == board_title
    assert "boardId" in data
    assert data["ownerId"] > 0


@pytest.mark.asyncio
async def test_get_boards_list(client: AsyncClient):
    """Тест получения списка досок."""
    # Создаем пользователя
    login = f"listuser_{uuid.uuid4().hex[:8]}@example.com"
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
    
    # Создаем несколько досок
    for i in range(3):
        await client.post(
            "/api/v1/boards/",
            json={
                "title": f"Board {i} {uuid.uuid4().hex[:8]}",
                "description": f"Description {i}",
            },
            headers={"Authorization": f"Bearer {token}"},
        )
    
    # Получаем список досок
    response = await client.get(
        "/api/v1/boards/?filter=all&page=1&limit=10",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "boards" in data
    assert len(data["boards"]) >= 3


@pytest.mark.asyncio
async def test_get_board_by_id(client: AsyncClient):
    """Тест получения доски по ID."""
    # Создаем пользователя
    login = f"getuser_{uuid.uuid4().hex[:8]}@example.com"
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
    board_title = f"Get Board {uuid.uuid4().hex[:8]}"
    create_response = await client.post(
        "/api/v1/boards/",
        json={"title": board_title, "description": "Test"},
        headers={"Authorization": f"Bearer {token}"},
    )
    board_id = create_response.json()["boardId"]
    
    # Получаем доску
    response = await client.get(
        f"/api/v1/boards/{board_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["boardId"] == board_id
    assert data["title"] == board_title
    assert "stickers" in data


@pytest.mark.asyncio
async def test_update_board(client: AsyncClient):
    """Тест обновления доски."""
    # Создаем пользователя
    login = f"updateuser_{uuid.uuid4().hex[:8]}@example.com"
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
    create_response = await client.post(
        "/api/v1/boards/",
        json={"title": f"Original {uuid.uuid4().hex[:8]}", "description": "Original"},
        headers={"Authorization": f"Bearer {token}"},
    )
    board_id = create_response.json()["boardId"]
    
    # Обновляем доску
    new_title = f"Updated {uuid.uuid4().hex[:8]}"
    response = await client.put(
        f"/api/v1/boards/{board_id}",
        json={"title": new_title, "description": "Updated description"},
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == new_title
    assert data["description"] == "Updated description"


@pytest.mark.asyncio
async def test_delete_board(client: AsyncClient):
    """Тест удаления доски."""
    # Создаем пользователя
    login = f"deleteuser_{uuid.uuid4().hex[:8]}@example.com"
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
    create_response = await client.post(
        "/api/v1/boards/",
        json={"title": f"Delete Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {token}"},
    )
    board_id = create_response.json()["boardId"]
    
    # Удаляем доску
    response = await client.delete(
        f"/api/v1/boards/{board_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    
    assert response.status_code == 204
    
    # Проверяем, что доска удалена
    get_response = await client.get(
        f"/api/v1/boards/{board_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 404



