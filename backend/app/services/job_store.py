from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


@dataclass
class JobRecord:
    job_id: str
    status: str
    stage: str
    payload_json: str
    artifacts_json: str
    error: str | None

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
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS jobs (
                    job_id TEXT PRIMARY KEY,
                    status TEXT NOT NULL,
                    stage TEXT NOT NULL,
                    payload_json TEXT NOT NULL,
                    artifacts_json TEXT NOT NULL,
                    error TEXT
                )
                """
            )
            conn.commit()

    def create_job(self, payload: dict) -> JobRecord:
        job_id = str(uuid4())
        payload_json = json.dumps(payload)
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO jobs(job_id,status,stage,payload_json,artifacts_json,error) VALUES(?,?,?,?,?,?)",
                (job_id, "queued", "queued", payload_json, "{}", None),
            )
            conn.commit()
        return self.get(job_id)

    def get(self, job_id: str) -> JobRecord | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM jobs WHERE job_id=?", (job_id,)).fetchone()
        if not row:
            return None
        return JobRecord(**dict(row))

    def update(self, job_id: str, **kwargs) -> JobRecord | None:
        allowed = {"status", "stage", "payload_json", "artifacts_json", "error"}
        updates = {k: v for k, v in kwargs.items() if k in allowed}
        if not updates:
            return self.get(job_id)

        set_clause = ", ".join([f"{k}=?" for k in updates])
        values = list(updates.values()) + [job_id]
        with self._connect() as conn:
            conn.execute(f"UPDATE jobs SET {set_clause} WHERE job_id=?", values)
            conn.commit()
        return self.get(job_id)
