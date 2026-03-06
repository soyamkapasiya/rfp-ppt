from fastapi import APIRouter

from app.api.v1.routes_generation import router as generation_router
from app.api.v1.routes_projects import router as projects_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(projects_router)
api_router.include_router(generation_router)
