import pytest
import pytest_asyncio
import os
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool

from main import app
from api.deps import get_db
from core.config import settings

# Для тестов используем localhost вместо postgres (для Docker)
# Можно переопределить через переменную окружения TEST_DATABASE_URL
test_db_url = os.getenv(
    "TEST_DATABASE_URL",
    settings.DATABASE_URL.replace("postgres:", "localhost:").replace("postgresql+asyncpg://", "postgresql+asyncpg://")
)

# Используем БД из .env или тестовую БД
# Для тестов используем транзакции с откатом для изоляции
engine = create_async_engine(
    test_db_url,
    echo=False,
    poolclass=NullPool,  # Не используем пул для тестов
)
TestingSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def db():
    """
    Create a new database session for a test.
    Используем транзакцию с откатом для изоляции тестов.
    """
    async with TestingSessionLocal() as session:
        # Начинаем транзакцию
        transaction = await session.begin()
        try:
            yield session
        finally:
            # Откатываем транзакцию после теста
            if transaction.is_active:
                await transaction.rollback()
            await session.close()


@pytest_asyncio.fixture(scope="function")
async def client(db: AsyncSession):
    """
    Create an AsyncClient that uses the override_get_db dependency.
    """
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def random_login():
    """Генерирует уникальный логин для тестов."""
    return f"test_{uuid.uuid4().hex[:8]}@example.com"


@pytest.fixture
def random_password():
    """Генерирует пароль для тестов."""
    return f"TestPass_{uuid.uuid4().hex[:8]}!"
