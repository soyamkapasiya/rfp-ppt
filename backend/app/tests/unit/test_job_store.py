from app.services.job_store import SqliteJobStore


def test_sqlite_job_store_create_and_update(tmp_path) -> None:
    store = SqliteJobStore(str(tmp_path / "jobs.db"))
    job = store.create_job({"project_name": "A"})

    assert job.status == "queued"

    updated = store.update(job.job_id, status="processing", stage="pipeline")
    assert updated is not None
    assert updated.status == "processing"
    assert updated.stage == "pipeline"
