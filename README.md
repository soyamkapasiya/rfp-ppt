# RFP AI Platform

Implementation scaffold based on `RFP_AI_PROJECT_GUIDE.md`.

## What is implemented

- FastAPI backend with project and generation routes
- Deterministic generation pipeline that outputs:
  - `deck.pptx`
  - `questions.json`
  - `sources.json`
  - `quality_report.json`
- Core domain schemas, quality gate, slide planner, question miner
- Placeholder adapters for Tavily, Neo4j, ChromaDB, and Celery workers
- React + Vite frontend for project input and job status polling
- Docker Compose infra skeleton (Postgres, Redis, Neo4j)

## Backend quickstart

```bash
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

## Frontend quickstart

```bash
cd frontend
npm install
npm run dev
```

## API

- `POST /api/v1/generation/rfp-ppt`
- `GET /api/v1/generation/jobs/{job_id}`
- `POST /api/v1/projects`
- `GET /health`
