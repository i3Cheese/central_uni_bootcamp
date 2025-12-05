from fastapi import FastAPI
from core.config import settings
from api.v1.api import api_router
from core.database import engine, Base

# Create tables on startup (for simplicity, usually use Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Hello World"}
