from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

JobStatus = Literal["queued", "processing", "completed", "failed"]


class JobCreatedResponse(BaseModel):
    job_id: str
    status: JobStatus


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobStatus
    stage: str
    artifacts: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


class ErrorDetail(BaseModel):
    field: str | None = None
    msg: str
    type: str | None = None


class ErrorResponse(BaseModel):
    """Standard error envelope returned by all error handlers."""
    error: str
    detail: str | list[ErrorDetail]
