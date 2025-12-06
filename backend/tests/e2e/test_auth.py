import pytest
import uuid
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_success(client: AsyncClient):
    """Тест успешной регистрации пользователя."""
    login = f"test_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "login": login,
            "password": password,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert "userId" in data
    assert data["login"] == login
    assert "createdAt" in data


@pytest.mark.asyncio
async def test_register_duplicate_login(client: AsyncClient):
    """Тест регистрации с уже существующим логином."""
    login = f"duplicate_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    # Создаем первого пользователя
    await client.post(
        "/api/v1/auth/register",
        json={
            "login": login,
            "password": password,
        },
    )
    
    # Пытаемся создать второго с тем же логином
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "login": login,
            "password": password,
        },
    )
    assert response.status_code == 409
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_register_validation_error(client: AsyncClient):
    """Тест валидации при регистрации."""
    # Слишком короткий логин
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "login": "ab",
            "password": f"TestPass_{uuid.uuid4().hex[:8]}!",
        },
    )
    assert response.status_code == 422
    
    # Слишком короткий пароль
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "login": f"test_{uuid.uuid4().hex[:8]}@example.com",
            "password": "short",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_success(client: AsyncClient):
    """Тест успешного входа."""
    login = f"login_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    # Сначала регистрируем пользователя
    await client.post(
        "/api/v1/auth/register",
        json={
            "login": login,
            "password": password,
        },
    )
    
    # Входим
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "login": login,
            "password": password,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "token" in data
    assert "userId" in data
    assert data["login"] == login
    assert "expiresAt" in data


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    """Тест входа с неверными данными."""
    login = f"invalid_{uuid.uuid4().hex[:8]}@example.com"
    password = f"TestPass_{uuid.uuid4().hex[:8]}!"
    
    # Регистрируем пользователя
    await client.post(
        "/api/v1/auth/register",
        json={
            "login": login,
            "password": password,
        },
    )
    
    # Пытаемся войти с неверным паролем
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "login": login,
            "password": "WrongPassword",
        },
    )
    assert response.status_code == 401
    
    # Пытаемся войти с несуществующим логином
    nonexistent_login = f"nonexistent_{uuid.uuid4().hex[:8]}@example.com"
    response = await client.post(
        "/api/v1/auth/login",
        json={
            "login": nonexistent_login,
            "password": password,
        },
    )
    assert response.status_code == 401

