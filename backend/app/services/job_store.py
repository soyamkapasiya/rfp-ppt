from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, List, Optional

from sqlalchemy import Column, DateTime, String, Text, create_engine, desc
from sqlalchemy.orm import declarative_base, sessionmaker

logger = logging.getLogger(__name__)

Base = declarative_base()

def _now_utc() -> datetime:
    return datetime.now(timezone.utc)

class JobModel(Base):
    __tablename__ = "jobs"

    job_id = Column(String(50), primary_key=True)
    status = Column(String(50), nullable=False)
    stage = Column(String(50), nullable=False)
    payload_json = Column(Text, nullable=False)
    artifacts_json = Column(Text, nullable=False, default="{}")
    error = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=_now_utc)
    updated_at = Column(DateTime, nullable=False, default=_now_utc, onupdate=_now_utc)

@dataclass
class JobRecord:
    job_id: str
    status: str
    stage: str
    payload_json: str
    artifacts_json: str
    error: str | None
    created_at: Any | None = None
    updated_at: Any | None = None

    @property
    def artifacts(self) -> dict:
        return json.loads(self.artifacts_json or "{}")

class JobStore:
    """SQLAlchemy-based job store supporting both SQLite and PostgreSQL."""
    def __init__(self, db_url: str) -> None:
        self.engine = create_engine(db_url, pool_pre_ping=True)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def create_job(self, payload: dict) -> JobRecord:
        import uuid
        job_id = str(uuid.uuid4())
        payload_json = json.dumps(payload)
        
        with self.Session() as session:
            job = JobModel(
                job_id=job_id,
                status="queued",
                stage="queued",
                payload_json=payload_json,
                artifacts_json="{}",
                error=None
            )
            session.add(job)
            session.commit()
            return self._to_record(job)

    def get(self, job_id: str) -> JobRecord | None:
        with self.Session() as session:
            job = session.query(JobModel).filter(JobModel.job_id == job_id).first()
            return self._to_record(job) if job else None

    def list_jobs(self, limit: int = 50, offset: int = 0) -> List[JobRecord]:
        with self.Session() as session:
            jobs = session.query(JobModel).order_by(desc(JobModel.created_at)).limit(limit).offset(offset).all()
            return [self._to_record(j) for j in jobs]

    def update(self, job_id: str, **kwargs) -> JobRecord | None:
        allowed = {"status", "stage", "payload_json", "artifacts_json", "error"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        
        with self.Session() as session:
            job = session.query(JobModel).filter(JobModel.job_id == job_id).first()
            if not job:
                return None
            
            for k, v in updates.items():
                setattr(job, k, v)
            
            session.commit()
            return self._to_record(job)

    def _to_record(self, job: JobModel) -> JobRecord:
        return JobRecord(
            job_id=job.job_id,
            status=job.status,
            stage=job.stage,
            payload_json=job.payload_json,
            artifacts_json=job.artifacts_json,
            error=job.error,
            created_at=job.created_at.isoformat() if job.created_at else None,
            updated_at=job.updated_at.isoformat() if job.updated_at else None,
        )

# Maintain alias for compatibility
SqliteJobStore = JobStore
