# RFP AI Platform

Production-oriented implementation based on `RFP_AI_PROJECT_GUIDE.md`.

## Implemented

- Backend: FastAPI + role-based auth (API key), persisted job store (SQLite), async queue dispatch (Celery or thread fallback), LangGraph orchestration with deterministic fallback.
- Retrieval: Tavily discovery + HTTP crawler + source trust/freshness enrichment + Chroma/Neo4j hybrid retrieval service.
- Quality: claim verification, conflict checks, freshness flags, compliance coverage checks, quality score gating.
- Artifacts: `deck.pptx`, `questions.json`, `sources.json`, `quality_report.json`, `claim_report.json`.
- Frontend: React + TypeScript + Vite + TanStack Query + Zustand with screens:
  - New Project
  - Generation Console
  - Question Bank
  - Deck Preview
  - Export Center
- Infra: Docker Compose for api, worker, frontend, postgres, redis, neo4j, chroma, prometheus, grafana.
- CI: GitHub Actions workflow (`ruff`, `mypy`, unit tests, frontend build).

## API auth

Use `X-API-Key` header (or `x-api-key` query param for download links).

Default local keys (from `.env.example`):
- admin: `admin-local-key`
- editor: `editor-local-key`
- viewer: `viewer-local-key`

## Sample Flow`n`nSee [docs/sample_flow.md](docs/sample_flow.md) for a full request-to-export walkthrough.`n`n## Run locally

```bash
# backend
cd backend
python -m venv .venv
. .venv/Scripts/activate
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000

# frontend
cd ../frontend
npm install
npm run dev
```

## Start full stack with Docker

```bash
cd infra
docker compose up -d --build
```

