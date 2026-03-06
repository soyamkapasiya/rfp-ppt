from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from app.models.domain import ClarifiedRequirement, RequirementInput
from app.services.ppt_renderer import render_ppt
from app.services.quality_service import score_deck
from app.services.question_miner import mine_questions
from app.services.slide_planner import build_slide_plan
from app.services.slide_writer import write_slides
from app.services.tavily_service import TavilyService


@dataclass
class JobRecord:
    job_id: str
    status: str = "queued"
    stage: str = "queued"
    artifacts: dict = field(default_factory=dict)
    error: str | None = None


class JobStore:
    def __init__(self) -> None:
        self._jobs: dict[str, JobRecord] = {}

    def create_job(self) -> JobRecord:
        job = JobRecord(job_id=str(uuid4()))
        self._jobs[job.job_id] = job
        return job

    def get(self, job_id: str) -> JobRecord | None:
        return self._jobs.get(job_id)


job_store = JobStore()


def _clarify_requirement(payload: RequirementInput) -> ClarifiedRequirement:
    return ClarifiedRequirement(
        objectives=[f"Deliver measurable value for {payload.project_name}"],
        in_scope=[payload.requirement_text[:140]],
        out_of_scope=["Undocumented third-party integrations"],
        constraints=["Budget and timeline to be validated"],
        assumptions=["Stakeholder access available during delivery"],
    )


def run_generation(job_id: str, payload: RequirementInput, tavily_api_key: str) -> None:
    job = job_store.get(job_id)
    if not job:
        return

    try:
        job.status = "processing"

        job.stage = "clarify"
        clarified = _clarify_requirement(payload)

        job.stage = "research"
        research = TavilyService(tavily_api_key).search(
            f"{payload.industry or ''} {payload.project_name} implementation best practices"
        )

        job.stage = "mine_questions"
        questions = mine_questions(clarified)

        job.stage = "plan_slides"
        planned = build_slide_plan(payload.project_name, clarified, questions)

        job.stage = "write_slides"
        slides = write_slides(planned)

        job.stage = "qa"
        quality = score_deck(slides=slides, has_sources=bool(research))
        if not quality.pass_gate:
            job.status = "failed"
            job.error = "; ".join(quality.issues)
            job.artifacts["quality_report"] = quality.model_dump()
            return

        job.stage = "render_ppt"
        artifacts_dir = Path("backend/artifacts") / job_id
        pptx_path = render_ppt(slides, str(artifacts_dir / "deck.pptx"))

        sources = [
            {"id": idx + 1, "url": row.get("url", ""), "title": row.get("title", "")}
            for idx, row in enumerate(research)
        ]

        artifacts_dir.mkdir(parents=True, exist_ok=True)
        (artifacts_dir / "questions.json").write_text(
            json.dumps([q.model_dump() for q in questions], indent=2), encoding="utf-8"
        )
        (artifacts_dir / "sources.json").write_text(json.dumps(sources, indent=2), encoding="utf-8")
        (artifacts_dir / "quality_report.json").write_text(
            json.dumps(quality.model_dump(), indent=2), encoding="utf-8"
        )

        job.stage = "completed"
        job.status = "completed"
        job.artifacts = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "pptx_path": str(pptx_path),
            "questions_path": str(artifacts_dir / "questions.json"),
            "sources_path": str(artifacts_dir / "sources.json"),
            "quality_report_path": str(artifacts_dir / "quality_report.json"),
            "quality_report": quality.model_dump(),
        }
    except Exception as exc:
        job.status = "failed"
        job.stage = "failed"
        job.error = str(exc)
