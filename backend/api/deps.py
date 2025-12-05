from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import AsyncSessionLocal
from core.security import decode_access_token
from models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


SessionDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: SessionDep = Depends(),
) -> User:
    """
    Получает текущего пользователя из JWT токена.
    
    Args:
        token: JWT токен из заголовка Authorization
        db: Сессия базы данных
        
    Returns:
        User: Объект пользователя
        
    Raises:
        HTTPException: Если токен невалидный или пользователь не найден
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id: str | None = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    try:
        user_id_int = int(user_id)
    except (ValueError, TypeError):
        raise credentials_exception
    
    result = await db.execute(select(User).where(User.id == user_id_int))
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
