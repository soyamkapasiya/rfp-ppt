# Sample End-to-End Flow

This example shows one complete run from requirement input to exported PPT.

## Scenario

- Project: `Smart Retail Demand Forecasting`
- Industry: `Retail`
- Region: `India`
- Requirement text: build demand forecasting with ERP/POS integration, role-based dashboard, and compliance guardrails.

## 1. Submit generation request

```bash
curl -X POST "http://localhost:8000/api/v1/generation/rfp-ppt" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: editor-local-key" \
  -d '{
    "project_name": "Smart Retail Demand Forecasting",
    "industry": "Retail",
    "region": "India",
    "requirement_text": "We need an AI demand forecasting solution integrating POS and ERP data, with role-based dashboards, phased rollout, and clear security/compliance controls for production readiness."
  }'
```

Response:

```json
{
  "job_id": "8ef0f7c0-8f5f-4f0f-b965-6bde45d7f4af",
  "status": "queued"
}
```

## 2. Poll job status

```bash
curl "http://localhost:8000/api/v1/generation/jobs/8ef0f7c0-8f5f-4f0f-b965-6bde45d7f4af" \
  -H "X-API-Key: viewer-local-key"
```

Typical stage progression:
- `queued`
- `pipeline` (processing)
- `completed` or `failed`

Example completed response (shortened):

```json
{
  "job_id": "8ef0f7c0-8f5f-4f0f-b965-6bde45d7f4af",
  "status": "completed",
  "stage": "completed",
  "artifacts": {
    "pptx_path": "artifacts/8ef0f7c0-8f5f-4f0f-b965-6bde45d7f4af/deck.pptx",
    "questions_path": "artifacts/.../questions.json",
    "sources_path": "artifacts/.../sources.json",
    "quality_report_path": "artifacts/.../quality_report.json",
    "claim_report_path": "artifacts/.../claim_report.json"
  }
}
```

## 3. Download output deck

```bash
curl -L "http://localhost:8000/api/v1/generation/jobs/8ef0f7c0-8f5f-4f0f-b965-6bde45d7f4af/artifacts/deck?x-api-key=viewer-local-key" \
  --output deck.pptx
```

## 4. Inspect generated question bank

```bash
curl "http://localhost:8000/api/v1/generation/jobs/8ef0f7c0-8f5f-4f0f-b965-6bde45d7f4af/artifacts/questions" \
  -H "X-API-Key: viewer-local-key"
```

You should see categorized client questions (`timeline`, `data`, `compliance`, etc.).

## 5. What happens internally

- Requirement is clarified into objectives, scope, constraints.
- Tavily discovery runs and URLs are crawled.
- Source trust and freshness metadata is computed.
- Documents are ingested into Chroma and Neo4j.
- Hybrid retrieval context is available for planning/writing.
- Slides are planned and written using the fixed 15-slide blueprint.
- Claim/conflict/freshness/compliance checks run.
- If quality gate passes, PPT + JSON artifacts are stored.

## 6. Frontend path

In the React app:
1. Fill `New Project` form.
2. Watch `Generation Console` status update.
3. Open `Question Bank` and `Deck Preview`.
4. Download from `Export Center`.
