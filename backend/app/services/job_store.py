from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class JobRecord:
    job_id: str
    status: str
    stage: str
    payload_json: str
    artifacts_json: str
    error: str | None
    created_at: str | None = None
    updated_at: str | None = None

    @property
    def artifacts(self) -> dict:
        return json.loads(self.artifacts_json or "{}")


class SqliteJobStore:
    def __init__(self, db_path: str) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        # Enable WAL for better concurrent read performance
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id        TEXT PRIMARY KEY,
                    status        TEXT NOT NULL,
                    stage         TEXT NOT NULL,
                    payload_json  TEXT NOT NULL,
                    artifacts_json TEXT NOT NULL,
                    error         TEXT,
                    created_at    TEXT NOT NULL,
                    updated_at    TEXT NOT NULL
                )
                """
            )
            # Migrate: add columns if they don't exist (idempotent)
            for col, default in [("created_at", _now_iso()), ("updated_at", _now_iso())]:
                try:
                    conn.execute(f"ALTER TABLE jobs ADD COLUMN {col} TEXT NOT NULL DEFAULT '{default}'")
                except sqlite3.OperationalError:
                    pass  # column already exists
            conn.commit()

    def create_job(self, payload: dict) -> JobRecord:
        job_id = str(uuid4())
        now = _now_iso()
        payload_json = json.dumps(payload)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO jobs(job_id,status,stage,payload_json,artifacts_json,error,created_at,updated_at) "
                "VALUES(?,?,?,?,?,?,?,?)",
                (job_id, "queued", "queued", payload_json, "{}", None, now, now),
            )
            conn.commit()
        result = self.get(job_id)
        if result is None:
            raise RuntimeError(f"Failed to create job {job_id}")
        return result

    def get(self, job_id: str) -> JobRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if not row:
            return None
        return JobRecord(**dict(row))

    def list_jobs(self, limit: int = 50, offset: int = 0) -> list[JobRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM jobs ORDER BY created_at DESC LIMIT ? OFFSET ?",
                (limit, offset),
            ).fetchall()
        return [JobRecord(**dict(r)) for r in rows]

    def update(self, job_id: str, **kwargs) -> JobRecord | None:
        allowed = {"status", "stage", "payload_json", "artifacts_json", "error"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        updates["updated_at"] = _now_iso()

        set_clause = ", ".join([f"{k}=?" for k in updates])
        values = list(updates.values()) + [job_id]
        with self._connect() as conn:
            conn.execute(f"UPDATE jobs SET {set_clause} WHERE job_id=?", values)
            conn.commit()
        return self.get(job_id)
