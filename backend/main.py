from contextlib import asynccontextmanager
from fastapi import FastAPI
from core.config import settings
from api.v1.api import api_router
from core.database import engine, Base


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create tables on startup (for simplicity, usually use Alembic)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown: cleanup if needed
    await engine.dispose()


app = FastAPI(title=settings.PROJECT_NAME, lifespan=lifespan)

app.include_router(api_router, prefix="/api/v1")


@app.get("/")
def root():
    return {"message": "Hello World"}
