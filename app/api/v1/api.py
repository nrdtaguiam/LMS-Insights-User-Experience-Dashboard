from fastapi import APIRouter

from app.api.v1.endpoints import usage, courses, webhooks

api_router = APIRouter()

api_router.include_router(usage.router, prefix="/usage", tags=["usage"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
