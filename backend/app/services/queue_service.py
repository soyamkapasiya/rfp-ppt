from __future__ import annotations

import threading

from app.core.config import settings
from app.models.domain import RequirementInput
from app.services.audit_service import audit_logger
from app.services.generation_service import run_generation


def enqueue_generation(job_id: str, payload: RequirementInput) -> None:
    audit_logger.log("job.enqueue", {"job_id": job_id, "use_celery": settings.use_celery})

    if settings.use_celery:
        try:
            from app.workers.tasks_generation import run_generation_task

            run_generation_task.delay(job_id, payload.model_dump())
            return
        except Exception:
            # Local fallback keeps app usable if worker is unavailable.
            pass

    thread = threading.Thread(
        target=run_generation,
        kwargs={"job_id": job_id, "payload": payload, "tavily_api_key": settings.tavily_api_key},
        daemon=True,
    )
    thread.start()
