from fastapi import APIRouter

from app.api.routes import (
    chat,
    demo,
    login,
    logs,
    plans,
    private,
    profile,
    programs,
    summary,
    users,
    utils,
)
from app.core.config import settings

api_router = APIRouter()
api_router.include_router(login.router)
api_router.include_router(users.router)
api_router.include_router(utils.router)
api_router.include_router(profile.router)
api_router.include_router(programs.router)
api_router.include_router(plans.router)
api_router.include_router(logs.router)
api_router.include_router(summary.router)
api_router.include_router(chat.router)

if settings.ENVIRONMENT == "local":
    api_router.include_router(private.router)
    api_router.include_router(demo.router)
