from fastapi import APIRouter, HTTPException

from app.core.config import settings
from app.models.api_schemas import JobCreatedResponse, JobStatusResponse
from app.models.domain import RequirementInput
from app.services.generation_service import job_store, run_generation

router = APIRouter(prefix="/generation", tags=["generation"])


@router.post("/rfp-ppt", response_model=JobCreatedResponse)
async def generate_rfp_ppt(payload: RequirementInput) -> JobCreatedResponse:
    job = job_store.create_job()
    run_generation(job.job_id, payload, settings.tavily_api_key)
    return JobCreatedResponse(job_id=job.job_id, status=job.status)


@router.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str) -> JobStatusResponse:
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
