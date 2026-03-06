from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    industry: str | None = None


@router.post("")
async def create_project(payload: ProjectCreate) -> dict:
    return {"id": "demo-project", "name": payload.name, "industry": payload.industry}
