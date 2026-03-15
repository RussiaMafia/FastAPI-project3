from fastapi import APIRouter
from app.api import auth, links, redirect

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(links.router)
api_router.include_router(redirect.router)

__all__ = ["api_router"]