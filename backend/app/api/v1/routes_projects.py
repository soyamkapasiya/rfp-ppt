from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.security import require_editor, require_viewer

router = APIRouter(prefix="/projects", tags=["projects"])


class ProjectCreate(BaseModel):
    name: str
    industry: str | None = None


@router.post("")
async def create_project(payload: ProjectCreate, _role=Depends(require_editor)) -> dict:
    return {"id": "demo-project", "name": payload.name, "industry": payload.industry}


@router.get("/{project_id}")
async def get_project(project_id: str, _role=Depends(require_viewer)) -> dict:
    return {"id": project_id, "name": "Demo", "industry": "General"}
