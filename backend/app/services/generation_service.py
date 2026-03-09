from __future__ import annotations

import asyncio
import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings
from app.db.chroma import ChromaStore
from app.db.neo4j import Neo4jStore
from app.models.domain import RequirementInput
from app.services.audit_service import audit_logger
from app.services.graphrag_service import GraphRAGService
from app.services.job_store import SqliteJobStore
from app.services.ppt_renderer import render_ppt
from app.workflows.rfp_graph import run_pipeline

job_url = settings.postgres_url if "sqlite" not in settings.postgres_url or ":memory:" not in settings.postgres_url else f"sqlite:///{settings.jobs_db_path}"
job_store = SqliteJobStore(job_url)

logger = logging.getLogger(__name__)

def run_generation(job_id: str, payload: RequirementInput, tavily_api_key: str) -> None:
    # Wrap in asyncio.run for synchronous Celery worker
    asyncio.run(_run_generation_async(job_id, payload, tavily_api_key))


async def _run_generation_async(job_id: str, payload: RequirementInput, tavily_api_key: str) -> None:
    job = job_store.get(job_id)
    if not job:
        return

    try:
        job_store.update(job_id, status="processing", stage="starting")
        audit_logger.log("job.start", {"job_id": job_id})

        chroma = ChromaStore(settings.chroma_persist_dir)
        try:
            neo4j = Neo4jStore(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
        except Exception as e:
            logger.warning("Neo4j unavailable, using stub: %s", e)
            neo4j = Neo4jStore.__new__(Neo4jStore)
            neo4j.driver = None

        graphrag = GraphRAGService(chroma=chroma, neo4j=neo4j)

        state = await run_pipeline(job_id=job_id, payload=payload, tavily_api_key=tavily_api_key, graphrag=graphrag)
        
        await _save_job_result(job_id, state, payload)

    except Exception as exc:
        logger.exception("Job %s failed", job_id, exc_info=exc)
        job_store.update(job_id, status="failed", stage="failed", error=str(exc))
        audit_logger.log("job.failed", {"job_id": job_id, "error": str(exc)})


async def resume_generation(job_id: str, start_node: str, tavily_api_key: str, updated_data: dict[str, Any] | None = None) -> None:
    """Resumes a paused pipeline from a specific node, potentially with updated data (like user answers)."""
    job = job_store.get(job_id)
    if not job:
        logger.error("Cannot resume: Job %s not found", job_id)
        return

    try:
        job_store.update(job_id, status="processing", stage=f"resuming_{start_node}")
        
        artifacts_dir = Path(settings.artifacts_dir) / job_id
        state_path = artifacts_dir / "state.json"
        
        if state_path.exists():
            state = json.loads(state_path.read_text(encoding="utf-8"))
        else:
            # Reconstruct basic state
            state = {
                "job_id": job_id,
                "payload": job.payload_json,
                "question_bank": updated_data.get("question_bank") if updated_data else []
            }
        
        if updated_data:
            state.update(updated_data)

        chroma = ChromaStore(settings.chroma_persist_dir)
        try:
            neo4j = Neo4jStore(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
        except Exception:
            neo4j = Neo4jStore.__new__(Neo4jStore)
            neo4j.driver = None
        
        graphrag = GraphRAGService(chroma=chroma, neo4j=neo4j)
        payload = RequirementInput(**state["payload"])
        
        final_state = await run_pipeline(
            job_id=job_id, 
            payload=payload, 
            tavily_api_key=tavily_api_key, 
            graphrag=graphrag,
            initial_state=state,
            start_node=start_node
        )
        
        await _save_job_result(job_id, final_state, payload)
        
    except Exception as exc:
        logger.exception("Resume failed for job %s", job_id)
        job_store.update(job_id, status="failed", error=str(exc))


async def _save_job_result(job_id: str, state: dict[str, Any], payload: RequirementInput) -> None:
    """Helper to save artifacts and update the job record."""
    artifacts_dir = Path(settings.artifacts_dir) / job_id
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    # Save state for next resume
    (artifacts_dir / "state.json").write_text(json.dumps(state, indent=2), encoding="utf-8")

    slides = state.get("rendered_slides", [])
    if slides and isinstance(slides[0], dict):
        slides[0]["project_name"] = payload.project_name

    pptx_path = render_ppt(slides, str(artifacts_dir / "deck_standard.pptx"))
    standard_deck_path = str(pptx_path)

    # Manus handling
    manus_url = state.get("manus_pptx_url")
    premium_deck_path = None
    if manus_url:
        from app.services.manus_service import ManusService
        try:
            manus = ManusService()
            premium_path = artifacts_dir / "deck_premium.pptx"
            await manus.download_pptx(manus_url, str(premium_path))
            premium_deck_path = str(premium_path)
        except Exception as e:
            logger.error("Manus download failed: %s", e)

    questions = state.get("question_bank", [])
    sources   = state.get("research_docs", [])
    quality   = state.get("quality_report", {})

    (artifacts_dir / "questions.json").write_text(json.dumps(questions, indent=2), encoding="utf-8")
    (artifacts_dir / "sources.json").write_text(json.dumps(sources, indent=2), encoding="utf-8")
    (artifacts_dir / "quality_report.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
    (artifacts_dir / "claim_report.json").write_text(
        json.dumps(state.get("claim_report", {}), indent=2), encoding="utf-8"
    )

    artifacts = {
        "generated_at":        datetime.now(timezone.utc).isoformat(),
        "deck_path":           premium_deck_path or standard_deck_path,
        "premium_deck_path":   premium_deck_path,
        "standard_deck_path":  standard_deck_path,
        "questions_path":      str(artifacts_dir / "questions.json"),
        "sources_path":        str(artifacts_dir / "sources.json"),
        "quality_report_path": str(artifacts_dir / "quality_report.json"),
        "claim_report_path":   str(artifacts_dir / "claim_report.json"),
        "state_path":          str(artifacts_dir / "state.json"),
        "quality_report":      quality,
    }

    # Determine next stage
    current_status = "completed"
    current_stage = "completed"
    
    # Check if we were at a HITL node
    if not state.get("is_questions_answered") and questions:
        current_status = "processing"
        current_stage = "awaiting_questions"
    elif not state.get("is_approved") and slides:
        current_status = "processing"
        current_stage = "awaiting_approval"

    job_store.update(
        job_id,
        status=current_status,
        stage=current_stage,
        artifacts_json=json.dumps(artifacts),
    )
    audit_logger.log(f"job.{current_status}", {"job_id": job_id, "stage": current_stage})
