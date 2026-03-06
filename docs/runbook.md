# Runbook

## Start backend

```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

## Start frontend

```bash
cd frontend
npm install
npm run dev
```

## Run tests

```bash
cd backend
pytest
```
