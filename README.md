# WindSight UK

WindSight UK is a full-stack decision-time analytics product for January 2026 Great Britain wind generation. It compares Elexon's day-ahead `WINDFOR` forecasts with `FUELHH` wind actuals while enforcing the forecast information boundary that existed at **D-1 09:50 GMT**.

The central question is not “which forecast revision was eventually most accurate?” It is “how accurate was the latest forecast that could genuinely have informed the decision?”

## What the evaluator can inspect

- A 744-hour January forecast-versus-actual evidence trail.
- MAE, RMSE, mean bias, WAPE, P90 absolute error, and coverage.
- Daily accuracy with focused-day investigation.
- Forecast revision history with the purchasing cutoff clearly marked.
- Reproducible Elexon ingestion, snapshot provenance, validation, and tests.
- A responsive React interface backed by a typed FastAPI API.

## Architecture

```text
Elexon WINDFOR + FUELHH
          │
          ▼
Python ingestion and validation
          │
          ▼
Versioned January JSON snapshot ──► FastAPI analytics API ──► React dashboard
```

This snapshot-backed architecture keeps the challenge reproducible and reviewable without introducing a database that the fixed January scope does not require.

```text
frontend/        React, TypeScript, Vite, TanStack Query, Recharts
backend/         FastAPI, Pydantic, Pandas, pytest
scripts/         Repository-level Elexon ingestion entry point
data/processed/  Versioned snapshot and SHA-256 provenance metadata
```

## Quick start with Docker

Requirements: Docker Desktop with Docker Compose.

```bash
docker compose up --build
```

Open:

- Dashboard: <http://localhost:3000>
- API health: <http://localhost:8000/health>
- OpenAPI docs: <http://localhost:8000/docs>

Stop the stack with:

```bash
docker compose down
```

## Local development

Requirements:

- Node.js 22+
- pnpm 10.29.2 through Corepack
- Python 3.10+
- uv 0.9.26+

Install and start the backend:

```bash
cd backend
uv sync --dev
uv run uvicorn app.main:app --reload --port 8000
```

In a second terminal, install and start the frontend from the repository root:

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm dev
```

The Vite development server runs at <http://localhost:5173> and proxies `/api` and `/health` to port `8000`.

Environment templates are provided in `backend/.env.example` and `frontend/.env.example`. Do not commit local `.env` files.

## Data methodology

1. Fetch `WINDFOR` forecast revisions and `FUELHH` generation records from the official Elexon Insights API in date chunks.
2. Retain January 2026 target timestamps and `fuelType=WIND` actuals.
3. For every delivery hour, calculate the decision cutoff at the previous day, 09:50 GMT.
4. Select the latest forecast whose publication time is at or before that cutoff. Later revisions are never used in accuracy metrics.
5. Convert each pair of half-hour wind actuals to an hourly arithmetic mean.
6. Keep missing observations as `null`; never fabricate them or silently reduce the expected period count.
7. Write the snapshot and a provenance file containing its SHA-256 digest and source URLs.

Regenerate the snapshot from the repository root:

```bash
cd backend
uv sync --dev
cd ..
uv run --project backend python scripts/ingest_elexon.py --chunk-days 1
```

The ingestion command calls the public Elexon API and replaces `data/processed/january-2026.v1.json` plus its provenance file. Review the resulting diff and rerun all tests before committing regenerated data.

### Error convention

```text
errorMw = forecastMw - actualMw
```

- Positive error: generation was over-forecast.
- Negative error: generation was under-forecast.

## API reference

| Endpoint | Purpose |
| --- | --- |
| `GET /health` | Service readiness |
| `GET /api/v1/overview` | Summary metrics and snapshot status |
| `GET /api/v1/timeseries` | Hourly forecast, actual, error, publication, and cutoff values |
| `GET /api/v1/daily-accuracy` | Metrics grouped by delivery date |
| `GET /api/v1/forecast-evolution` | All revisions for a selected delivery hour |
| `GET /api/v1/error-distribution` | Forecast-error histogram bins |

The overview, timeseries, daily-accuracy, and error-distribution endpoints accept inclusive `from` and `to` dates within `2026-01-01` and `2026-01-31`. Forecast evolution requires a timezone-aware `startTime`.

Interactive request and response schemas are available at `/docs` while the backend is running.

## Verification

Backend:

```bash
cd backend
uv run pytest
uv run ruff check .
```

Frontend, from the repository root:

```bash
pnpm test
pnpm lint
pnpm typecheck
pnpm build
```

Full production-style smoke test:

```bash
docker compose up --build -d
docker compose ps
docker compose down
```

The committed reference test verifies all 744 January hours, the no-hindsight cutoff, snapshot integrity, complete coverage, and known metric baselines.

## Demo video

Watch the complete project walkthrough: [WindSight UK — Full-Stack Software Engineer Challenge](https://youtu.be/Zh_A8KevDu0)

## Deployment

Deployment configuration is committed for a Vercel frontend and Render backend.

- Backend API: <https://vdfcds.onrender.com>
- API documentation: <https://vdfcds.onrender.com/docs>
- Frontend: <https://windsight-uk.vercel.app>

### 1. Create the Vercel project

1. Import the GitHub repository into Vercel and keep the repository root as the project root.
2. Vercel reads `vercel.json`, installs the pnpm workspace, builds `@windsight/frontend`, and publishes `frontend/dist`.
3. The first deployment can complete without `VITE_API_BASE_URL`; it will establish the permanent Vercel production origin.

### 2. Create the Render backend

1. In Render, create a Blueprint from the same repository. Render reads `render.yaml` and builds `backend/Dockerfile` with the repository root as its Docker context.
2. When prompted for `WINDSIGHT_ALLOWED_ORIGINS`, enter a JSON list containing only the production Vercel origin, with no trailing slash:

   ```json
   ["https://your-project.vercel.app"]
   ```

3. Wait for `/health` to pass and copy the resulting `https://...onrender.com` service origin.

### 3. Connect the frontend

1. Add `VITE_API_BASE_URL` to the Vercel Production environment using the Render origin, with no trailing slash.
2. Redeploy the Vercel project because Vite embeds public environment variables at build time.
3. Verify the dashboard, browser console, API health, and a filtered date range in an incognito window.

The backend CORS configuration intentionally allows only the deployed production frontend origin. Add preview origins explicitly only if preview deployments need API access.

## Assumptions and limitations

- Scope is fixed to January 2026 and its 744 hourly periods.
- GMT and UTC are equivalent throughout January; daylight-saving transitions are outside this dataset.
- Hourly actual generation is the arithmetic mean of two half-hour observations.
- Metrics exclude incomplete forecast/actual pairs but continue to report expected and complete coverage.
- The product analyses forecast quality; it does not issue trades or claim commercial outcomes.
- Authentication, database persistence, CSV export, heatmaps, ML forecasting, and trading execution are intentionally outside v1.

## AI-tool disclosure

This challenge was developed with AI-assisted engineering using OpenAI Codex. AI assistance was used for planning, implementation, test authoring, UI critique, verification workflows, and documentation. The resulting code and analytical decisions were reviewed against the acceptance criteria and validated with automated tests, linting, type checking, production builds, Docker smoke tests, and browser inspection.
