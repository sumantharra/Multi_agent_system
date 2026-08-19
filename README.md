# Multi-Agent AI Platform

Phase 2 adds PostgreSQL and Hostels CRUD on top of the Phase 1 health check.

## Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- Node.js 24 and npm
- PostgreSQL 15+ (local install or Docker)

## 1. Configure environment

From the repo root:

```bash
copy .env.example .env
```

Edit `.env` if your Postgres username/password differ from `postgres` / `postgres`.

## 2. Start PostgreSQL

**Option A — local Postgres (already installed on Windows):** create the database once:

```bash
"C:\Program Files\PostgreSQL\15\bin\psql.exe" -U postgres -c "CREATE DATABASE multi_agent;"
```

**Option B — Docker (when Docker Desktop is installed):**

```bash
docker compose up -d postgres
```

## 3. Start the backend

```bash
cd backend
uv sync --dev
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000
```

Useful URLs:

- Liveness: `GET http://localhost:8000/health`
- Readiness (DB): `GET http://localhost:8000/health/ready`
- Hostels API: `http://localhost:8000/api/v1/hostels`
- Interactive docs: `http://localhost:8000/docs`

With `APP_ENV=development` and `ALLOW_UNAUTHENTICATED=true`, hostel routes are open for local work. Do not use that setting in staging or production.

### Quick hostel API smoke test

```bash
curl -X POST http://localhost:8000/api/v1/hostels -H "Content-Type: application/json" -d "{\"name\":\"Sai Boys Hostel\",\"code\":\"sai-01\",\"default_rate_per_liter\":\"45.50\"}"
curl http://localhost:8000/api/v1/hostels
```

## 4. Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The status page still checks backend health (hostel UI comes in a later phase).

## Run checks

Backend:

```bash
cd backend
uv run ruff check .
uv run pytest
```

Frontend:

```bash
cd frontend
npm run lint
npm run typecheck
npm test -- --run
npm run build
```

## What is implemented now

- PostgreSQL connection + Alembic migrations
- Hostels CRUD under `/api/v1/hostels` (create, list, get, update, soft-delete)
- `/health/ready` database probe
- Development-only unauthenticated access gate

## Not yet implemented

Deliveries, invoices, payments, auth/JWT, documents, RAG, or LangGraph agents.
