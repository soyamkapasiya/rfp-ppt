# Runbook

## 1. Configure env

Copy `backend/.env.example` to `backend/.env` and set:
- `TAVILY_API_KEY`
- `OPENROUTER_API_KEY` (optional)
- API keys for RBAC users

## 2. Start backend

```bash
cd backend
pip install -e .[dev]
uvicorn app.main:app --reload --port 8000
```

## 3. Start worker (optional but recommended)

```bash
cd backend
celery -A app.workers.tasks_generation.celery worker --loglevel=info
```

## 4. Start frontend

```bash
cd frontend
npm install
npm run dev
```

## 5. Generate deck

`POST /api/v1/generation/rfp-ppt` with `X-API-Key: editor-local-key`.

## 6. Observability

- `GET /metrics` for basic API metrics
- Prometheus + Grafana available in Docker Compose (`9090`, `3000`)

## 7. Audit logs

Generation and artifact events are appended to:
- `artifacts/audit.log`

