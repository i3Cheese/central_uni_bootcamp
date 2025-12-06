import pytest
import uuid
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_share_board(client: AsyncClient):
    """Тест предоставления доступа к доске."""
    # Создаем двух пользователей
    owner_login = f"owner_{uuid.uuid4().hex[:8]}@example.com"
    user_login = f"user_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"

    await client.post(
        "/api/v1/auth/register",
        json={"login": owner_login, "password": password},
    )
    await client.post(
        "/api/v1/auth/register",
        json={"login": user_login, "password": password},
    )

    owner_login_response = await client.post(
        "/api/v1/auth/login",
        json={"login": owner_login, "password": password},
    )
    owner_token = owner_login_response.json()["token"]

    # Создаем доску от имени владельца
    board_response = await client.post(
        "/api/v1/boards/",
        json={"title": f"Share Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    board_id = board_response.json()["boardId"]

    # Предоставляем доступ
    response = await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": user_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["boardId"] == board_id
    assert data["permission"] == "edit"


@pytest.mark.asyncio
async def test_get_board_shares(client: AsyncClient):
    """Тест получения списка пользователей с доступом."""
    # Создаем пользователей
    owner_login = f"ownerlist_{uuid.uuid4().hex[:8]}@example.com"
    user1_login = f"user1_{uuid.uuid4().hex[:8]}@example.com"
    user2_login = f"user2_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"

    await client.post(
        "/api/v1/auth/register",
        json={"login": owner_login, "password": password},
    )
    await client.post(
        "/api/v1/auth/register",
        json={"login": user1_login, "password": password},
    )
    await client.post(
        "/api/v1/auth/register",
        json={"login": user2_login, "password": password},
    )

    owner_login_response = await client.post(
        "/api/v1/auth/login",
        json={"login": owner_login, "password": password},
    )
    owner_token = owner_login_response.json()["token"]

    # Создаем доску
    board_response = await client.post(
        "/api/v1/boards/",
        json={"title": f"Shares Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    board_id = board_response.json()["boardId"]

    # Предоставляем доступ двум пользователям
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": user1_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": user2_login, "permission": "view"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # Получаем список пользователей с доступом
    response = await client.get(
        f"/api/v1/boards/{board_id}/share",
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["boardId"] == board_id
    assert len(data["shares"]) == 2


@pytest.mark.asyncio
async def test_revoke_share(client: AsyncClient):
    """Тест отзыва доступа к доске."""
    # Создаем пользователей
    owner_login = f"revokeowner_{uuid.uuid4().hex[:8]}@example.com"
    user_login = f"revokeuser_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"

    await client.post(
        "/api/v1/auth/register",
        json={"login": owner_login, "password": password},
    )
    await client.post(
        "/api/v1/auth/register",
        json={"login": user_login, "password": password},
    )

    owner_login_response = await client.post(
        "/api/v1/auth/login",
        json={"login": owner_login, "password": password},
    )
    owner_token = owner_login_response.json()["token"]

    # Создаем доску
    board_response = await client.post(
        "/api/v1/boards/",
        json={"title": f"Revoke Board {uuid.uuid4().hex[:8]}"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    board_id = board_response.json()["boardId"]

    # Предоставляем доступ
    await client.post(
        f"/api/v1/boards/{board_id}/share",
        json={"userLogin": user_login, "permission": "edit"},
        headers={"Authorization": f"Bearer {owner_token}"},
    )

    # Отзываем доступ
    import json

    response = await client.request(
        "DELETE",
        f"/api/v1/boards/{board_id}/share",
        content=json.dumps({"userLogin": user_login}),
        headers={
            "Authorization": f"Bearer {owner_token}",
            "Content-Type": "application/json",
        },
    )

    assert response.status_code == 204

    # Проверяем, что доступа больше нет
    shares_response = await client.get(
        f"/api/v1/boards/{board_id}/share",
        headers={"Authorization": f"Bearer {owner_token}"},
    )
    assert len(shares_response.json()["shares"]) == 0
