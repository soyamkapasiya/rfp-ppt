from typing import Any, Literal

from pydantic import BaseModel, Field


class JobCreatedResponse(BaseModel):
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]


class JobStatusResponse(BaseModel):
    job_id: str
    status: Literal["queued", "processing", "completed", "failed"]
    stage: str
    artifacts: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
