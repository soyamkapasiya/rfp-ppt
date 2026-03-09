from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse

from app.core.config import settings
from app.core.security import require_editor, require_viewer
from app.models.api_schemas import JobCreatedResponse, JobStatusResponse
from app.models.domain import RequirementInput
from app.services.audit_service import audit_logger
from app.services.generation_service import job_store
from app.services.queue_service import enqueue_generation

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/generation", tags=["generation"])


# ── Create job ────────────────────────────────────────────────────────────────
@router.post(
    "/rfp-ppt",
    response_model=JobCreatedResponse,
    status_code=202,
    summary="Start an RFP PPT generation job",
)
async def generate_rfp_ppt(
    payload: RequirementInput,
    _role=Depends(require_editor),
) -> JobCreatedResponse:
    job = job_store.create_job(payload.model_dump())
    enqueue_generation(job.job_id, payload)
    logger.info("Job created", extra={"job_id": job.job_id})
    return JobCreatedResponse(job_id=job.job_id, status=job.status)


# ── List jobs ─────────────────────────────────────────────────────────────────
@router.get(
    "/jobs",
    response_model=list[JobStatusResponse],
    summary="List recent generation jobs",
)
async def list_jobs(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    _role=Depends(require_viewer),
) -> list[JobStatusResponse]:
    jobs = job_store.list_jobs(limit=limit, offset=offset)
    return [
        JobStatusResponse(
            job_id=j.job_id,
            status=j.status,
            stage=j.stage,
            artifacts=j.artifacts,
            error=j.error,
            created_at=datetime.fromisoformat(j.created_at) if j.created_at else None,
            updated_at=datetime.fromisoformat(j.updated_at) if j.updated_at else None,
        )
        for j in jobs
    ]


# ── Get job ───────────────────────────────────────────────────────────────────
@router.get(
    "/jobs/{job_id}",
    response_model=JobStatusResponse,
    summary="Get status of a specific generation job",
)
async def get_job_status(
    job_id: str,
    _role=Depends(require_viewer),
) -> JobStatusResponse:
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return JobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        stage=job.stage,
        artifacts=job.artifacts,
        error=job.error,
        created_at=datetime.fromisoformat(job.created_at) if job.created_at else None,
        updated_at=datetime.fromisoformat(job.updated_at) if job.updated_at else None,
    )


# ── Get artifact ──────────────────────────────────────────────────────────────
@router.get(
    "/jobs/{job_id}/artifacts/{artifact_name}",
    summary="Download or read a job artifact",
)
async def get_job_artifact(
    job_id: str,
    artifact_name: str,
    _role=Depends(require_viewer),
):
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    artifacts = job.artifacts
    key = f"{artifact_name}_path"
    path = artifacts.get(key)

    if not path:
        raise HTTPException(
            status_code=404,
            detail=f"Artifact '{artifact_name}' not available for this job. "
                   "The job may still be processing.",
        )

    file_path = Path(path)
    if not file_path.exists():
        logger.error("Artifact file missing from disk", extra={"job_id": job_id, "path": path})
        raise HTTPException(
            status_code=500,
            detail="Artifact file was recorded but is missing from storage.",
        )

    # Binary (PPTX) – return as file download
    if file_path.suffix in {".pptx", ".ppt"}:
        audit_logger.log("artifact.download", {"job_id": job_id, "artifact": artifact_name})
        return FileResponse(
            path=str(file_path),
            filename=file_path.name,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )

    # JSON – parse and return as API response
    try:
        content = json.loads(file_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        logger.exception("Failed to read artifact", exc_info=exc)
        raise HTTPException(status_code=500, detail="Failed to read artifact file.") from exc

    return {"job_id": job_id, "artifact": artifact_name, "data": content}


# ── HITL Interactions: Answers ──────────────────────────────────────────────
@router.post(
    "/jobs/{job_id}/answers",
    summary="Submit user answers to mined questions",
)
async def submit_job_answers(
    job_id: str,
    answers: list[dict],
    _role=Depends(require_editor),
):
    """
    Saves user-provided answers and resumes the pipeline from 'research'.
    Each dict in 'answers' should match QuestionItem (index or question text matching).
    """
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    from app.services.generation_service import resume_generation
    
    # We pass the question_bank with user_answer fields filled
    updated_data = {"question_bank": answers, "is_questions_answered": True}
    
    # Run in background
    asyncio.create_task(
        resume_generation(
            job_id=job_id, 
            start_node="research", 
            tavily_api_key=settings.tavily_api_key, 
            updated_data=updated_data
        )
    )
    
    return {"status": "resumed", "next_stage": "research"}


# ── HITL Interactions: Final Approval ────────────────────────────────────────
@router.post(
    "/jobs/{job_id}/generate-premium",
    summary="Final approval to trigger Manus Premium PPT generation",
)
async def approve_job_ppt(
    job_id: str,
    _role=Depends(require_editor),
):
    """Triggers the final phase: Manus PPT generation."""
    job = job_store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    from app.services.generation_service import resume_generation
    
    updated_data = {"is_approved": True}
    
    asyncio.create_task(
        resume_generation(
            job_id=job_id, 
            start_node="manus_ppt", 
            tavily_api_key=settings.tavily_api_key, 
            updated_data=updated_data
        )
    )
    
    return {"status": "resumed", "next_stage": "manus_ppt"}
