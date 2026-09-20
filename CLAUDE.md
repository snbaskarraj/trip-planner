# Trip Planner — project memory

Stack: **React (Vite) + FastAPI + a relational database (SQLite locally, any SQLAlchemy-supported engine in production).**

## Directory layout

```
trip-planner/
  backend/          FastAPI app, SQLAlchemy models, Alembic migrations, pytest
  frontend/         React + Vite SPA
  specs/            source of truth — read these before changing behavior
  .github/workflows CI (and CD gate) 
```

## Specs (always current)

- Goal: [specs/goal-spec.md](specs/goal-spec.md)
- Front end: [specs/frontend-spec.md](specs/frontend-spec.md)
- Back end: [specs/backend-spec.md](specs/backend-spec.md)
- API contract (the seam): [specs/api-contract.md](specs/api-contract.md)
- Build plan: [specs/build-plan.md](specs/build-plan.md)
- Acceptance → tests: [specs/acceptance-tests.md](specs/acceptance-tests.md)

If spec and code disagree, update the spec first, then the code.

## Hard rules

- One task, one diff. Do not "clean up" unrelated files.
- Maps/weather is called only from `backend/app/services/weather.py`. The API key lives in `WEATHER_API_KEY` and is never sent to the client.
- Upstream weather failure → HTTP 200 + `{"status":"unavailable"}`, never 5xx.
- A Day (and Activity) with `end_time` before `start_time` is rejected with `400` / `END_BEFORE_START`.

## Local run

- Backend: `backend/.venv/bin/uvicorn app.main:app --reload --app-dir backend --port 8000`
- Frontend: `npm run dev` in `frontend/` (proxies `/api` and `/health` to :8000)
