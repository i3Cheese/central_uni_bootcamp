from fastapi import APIRouter
from api.v1.endpoints import auth, boards, sharing

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
api_router.include_router(boards.router, prefix="/boards", tags=["Boards"])
api_router.include_router(sharing.router, prefix="/boards", tags=["Sharing"])
