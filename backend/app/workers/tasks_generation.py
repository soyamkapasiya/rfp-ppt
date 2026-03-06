from app.core.config import settings
from app.models.domain import RequirementInput
from app.services.generation_service import run_generation
from app.workers.celery_app import create_celery

celery = create_celery(settings.redis_url)


@celery.task(name="generation.run")
def run_generation_task(job_id: str, payload: dict) -> None:
    run_generation(job_id=job_id, payload=RequirementInput(**payload), tavily_api_key=settings.tavily_api_key)
