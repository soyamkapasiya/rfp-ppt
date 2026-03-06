import json
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.security import require_editor, require_viewer
from app.models.api_schemas import JobCreatedResponse, JobStatusResponse
from app.models.domain import RequirementInput
from app.services.audit_service import audit_logger
from app.services.generation_service import job_store
from app.services.queue_service import enqueue_generation

router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/rfp-ppt", response_model=JobCreatedResponse)
async def generate_rfp_ppt(
    payload: RequirementInput,
    _role=Depends(require_editor),
) -> JobCreatedResponse:
    job = job_store.create_job(payload.model_dump())
    enqueue_generation(job.job_id, payload)
    return JobCreatedResponse(job_id=job.job_id, status=job.status)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str, _role=Depends(require_viewer)) -> JobStatusResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        stage=job.stage,
        artifacts=job.artifacts,
        error=job.error,
    )


@router.get("/jobs/{job_id}/artifacts/{artifact_name}")
async def get_job_artifact(job_id: str, artifact_name: str, _role=Depends(require_viewer)):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    artifacts = job.artifacts
    key = f"{artifact_name}_path"
    path = artifacts.get(key)
    if not path:
        raise HTTPException(status_code=404, detail="artifact not found")

    file_path = Path(path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="artifact file missing")

    if file_path.suffix == ".pptx":
        audit_logger.log("artifact.download", {"job_id": job_id, "artifact": artifact_name})
        return FileResponse(path=str(file_path), filename=file_path.name)

    content = json.loads(file_path.read_text(encoding="utf-8"))
    return {"job_id": job_id, "artifact": artifact_name, "data": content}

