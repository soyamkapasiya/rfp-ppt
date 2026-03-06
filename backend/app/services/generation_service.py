from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings
from app.db.chroma import ChromaStore
from app.db.neo4j import Neo4jStore
from app.models.domain import RequirementInput
from app.services.audit_service import audit_logger
from app.services.graphrag_service import GraphRAGService
from app.services.job_store import SqliteJobStore
from app.services.ppt_renderer import render_ppt
from app.workflows.rfp_graph import run_pipeline

job_store = SqliteJobStore(settings.jobs_db_path)


def run_generation(job_id: str, payload: RequirementInput, tavily_api_key: str) -> None:
    job = job_store.get(job_id)
    if not job:
        return

    try:
        job_store.update(job_id, status="processing", stage="pipeline")
        audit_logger.log("job.start", {"job_id": job_id})

        chroma = ChromaStore(settings.chroma_persist_dir)
        neo4j = Neo4jStore(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
        graphrag = GraphRAGService(chroma=chroma, neo4j=neo4j)

        state = run_pipeline(payload=payload, tavily_api_key=tavily_api_key, graphrag=graphrag)

        quality = state.get("quality_report", {})
        if not quality.get("pass_gate", False):
            job_store.update(
                job_id,
                status="failed",
                stage="qa",
                artifacts_json=json.dumps({"quality_report": quality, "claim_report": state.get("claim_report", {})}),
                error="; ".join(quality.get("issues", ["quality gate failed"])),
            )
            audit_logger.log("job.failed", {"job_id": job_id, "reason": "quality_gate"})
            return

        artifacts_dir = Path(settings.artifacts_dir) / job_id
        artifacts_dir.mkdir(parents=True, exist_ok=True)

        slides = state.get("rendered_slides", [])
        pptx_path = render_ppt(slides, str(artifacts_dir / "deck.pptx"))

        questions = state.get("question_bank", [])
        sources = state.get("research_docs", [])

        (artifacts_dir / "questions.json").write_text(json.dumps(questions, indent=2), encoding="utf-8")
        (artifacts_dir / "sources.json").write_text(json.dumps(sources, indent=2), encoding="utf-8")
        (artifacts_dir / "quality_report.json").write_text(json.dumps(quality, indent=2), encoding="utf-8")
        (artifacts_dir / "claim_report.json").write_text(
            json.dumps(state.get("claim_report", {}), indent=2), encoding="utf-8"
        )

        artifacts = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pptx_path": str(pptx_path),
            "deck_path": str(pptx_path),
            "questions_path": str(artifacts_dir / "questions.json"),
            "sources_path": str(artifacts_dir / "sources.json"),
            "quality_report_path": str(artifacts_dir / "quality_report.json"),
            "claim_report_path": str(artifacts_dir / "claim_report.json"),
            "quality_report": quality,
        }

        job_store.update(
            job_id,
            status="completed",
            stage="completed",
            artifacts_json=json.dumps(artifacts),
            error=None,
        )
        audit_logger.log("job.completed", {"job_id": job_id, "pptx_path": str(pptx_path)})
    except Exception as exc:
        job_store.update(job_id, status="failed", stage="failed", error=str(exc))
        audit_logger.log("job.failed", {"job_id": job_id, "error": str(exc)})
