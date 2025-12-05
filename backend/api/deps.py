from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


SessionDep = Annotated[Session, Depends(get_db)]
