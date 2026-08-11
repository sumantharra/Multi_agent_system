# Multi-Agent AI Platform

Phase 1 provides the project foundation: a FastAPI health endpoint and a React status page that verifies frontend-to-backend connectivity.

## Prerequisites

- Python 3.13
- [uv](https://docs.astral.sh/uv/)
- Node.js 24 and npm

## Start the backend

```bash
cd backend
uv sync --dev
uv run uvicorn app.main:app --reload --port 8000
```

The API is available at `http://localhost:8000`; its health endpoint is `GET /health`.

## Start the frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:5173`. The page reports whether it can reach the backend.

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

## Environment configuration

Copy `.env.example` to `.env` only when overriding defaults. Never commit `.env` files or secrets. Phase 1 deliberately has no database, authentication, document-processing, or AI configuration.

