# Workstation Tech Stack Checklist

What needs to be present on your machine to complete the full Multi-Agent project.

## Already on this machine

| Tool | Status |
|------|--------|
| Python 3.13 | Installed |
| uv | Installed |
| Git | Installed |
| PostgreSQL 15 | Running |

## Missing now (install these soon)

| Tool | Why |
|------|-----|
| **Node.js 24 + npm** | Frontend (React) |
| **Docker Desktop** | Easy Postgres/Redis later; matches the project plan |

## Full workstation checklist

### Must have (core app)

1. **Python 3.13** + **uv** — backend
2. **Node.js 24** + **npm** — frontend
3. **PostgreSQL 15+** (or Docker Postgres) — database
4. **Git** — version control
5. **Cursor / VS Code** — coding

### Need for middle phases (documents / AI / workers)

6. **Redis** (usually via Docker) — background jobs
7. **Tesseract OCR** — scanned PDF text
8. **LLM API key** (OpenAI-compatible) — extraction + chat agents

### Need for later / production

9. **Docker Desktop** — local full stack
10. **AWS account** (optional until Phase 14) — deploy
11. **GitHub account** — CI/CD

## Project tech stack (what the app uses)

| Layer | Stack |
|-------|--------|
| Frontend | React, TypeScript, Vite, Tailwind, React Query |
| Backend | FastAPI, Pydantic, SQLAlchemy, Alembic |
| Database | PostgreSQL + pgvector |
| AI | LangChain, LangGraph, LLM API |
| Files | Local storage → later S3 |
| Jobs | Celery + Redis |
| Deploy | Docker → AWS (ECS, RDS, S3) |

## Install next (in order)

1. **Node.js 24** — https://nodejs.org
2. **Docker Desktop** — https://www.docker.com/products/docker-desktop/
3. Confirm Postgres password works in your `.env`

## Notes

- You do **not** need AWS, Redis, Tesseract, or an LLM key to finish Phase 2 (Hostels). Those come later.
- For Phase 2, make sure `DATABASE_URL` in `.env` uses your real Postgres password.
- See `README.md` for how to run the backend and frontend.
- See `docs/ARCHITECTURE.md` for the full system design and phase plan.
