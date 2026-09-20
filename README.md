# Trip Planner

A multi-day itinerary app built to the Chapters 4–7 lab guide: React (Vite) frontend, FastAPI backend, SQLite, shareable read-only links, and a maps/weather wrapper that never crashes the itinerary.

```
trip-planner/
  backend/     FastAPI + SQLAlchemy + Alembic + pytest
  frontend/    React + Vite + Vitest
  specs/       goal, frontend, backend, API contract
```

---

## What you get

- **Trip List** — create, open, and delete trips.
- **Itinerary Editor** — days and activities, including the “end time before start time” rejection.
- **Share View** — `/share/:token`, read-only, no login.
- **Day conditions** — weather for the trip destination. Timeout or vendor failure returns `200 {"status":"unavailable"}`; the page still renders.

The weather API key (`WEATHER_API_KEY`) is read only on the server. It is never sent to the browser.

---

## Run it locally (verify before anything else)

You need Python 3.11+ (3.13 is what this repo’s venv uses) and Node 20+.

### 1. Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Confirm:

```bash
curl http://127.0.0.1:8000/health
# {"status":"ok"}
```

Interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

Optional: copy `backend/.env.example` to `backend/.env` and set `WEATHER_API_KEY` if you want OpenWeatherMap. With the key unset, the wrapper uses Open-Meteo (no key) and still returns `unavailable` on any failure.

### 2. Frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open [http://localhost:5173](http://localhost:5173). Vite proxies `/api` and `/health` to the backend, so you do not need `VITE_API_URL` locally.

Click through: create a trip → add a day → add an activity → copy the share link → open it in a private window. Set a day’s end time earlier than its start time and confirm the editor shows the error and does not save.

### 3. Tests

```bash
cd backend && .venv/bin/pytest
cd frontend && npm test
```

### 4. Mutation-style check (§6.2)

In `backend/app/routers/trips.py`, comment out `assert_time_order(start_time, end_time)` inside `create_day`. Run `pytest`. `test_create_day_rejects_end_before_start` must fail. Restore the line. The suite must pass again. If it stayed green with the check removed, the test was not testing the endpoint.

---

## Specs (read these before changing behavior)

| File | Role |
|---|---|
| [specs/goal-spec.md](specs/goal-spec.md) | Goal, constraints, acceptance |
| [specs/frontend-spec.md](specs/frontend-spec.md) | Screens, flow, given/then states |
| [specs/backend-spec.md](specs/backend-spec.md) | Data model, rules, NFRs |
| [specs/api-contract.md](specs/api-contract.md) | Every endpoint, status, body |
| [specs/build-plan.md](specs/build-plan.md) | Task order |
| [specs/acceptance-tests.md](specs/acceptance-tests.md) | Criterion → test type |

`CLAUDE.md` at the repo root is the session memory file from §5.5.

---

## CI / CD

`.github/workflows/ci.yml` runs pytest and Vitest on every push and pull request. A deploy job runs only on `main`, and only after both test jobs pass (`needs:`).

1. Create a GitHub repo and push this project.
2. Open the Actions tab and confirm the workflow is green.
3. Connect `frontend/` to Vercel. Set build-time env `VITE_API_URL` to the deployed backend origin.
4. Deploy the backend container (Render, Fly, Railway, or Cloud Run). Set `WEATHER_API_KEY` and `CORS_ORIGINS` in the provider dashboard — never in git.
5. Optional: set repo secret `DEPLOY_WEBHOOK_URL` so the gated deploy job actually triggers your host.

```bash
# backend image
cd backend
docker build -t trip-planner-backend .
docker run --rm -p 8000:8000 -e WEATHER_API_KEY=your-key trip-planner-backend
```

---

## Understanding check (§7.2)

1. **Why a weather wrapper?** The itinerary endpoints must stay up when the vendor is down. The wrapper is the only module that talks to the vendor, and it swallows timeouts/errors into `{"status":"unavailable"}`. Remove it and a 504/exception from OpenWeather or Open-Meteo becomes a 5xx (or a crashed request) on the itinerary page — exactly the failure the goal spec forbids.
2. **End time before start time.** The editor POSTs `/api/trips/:id/days`. The Day create endpoint calls `assert_time_order`. That raises `DomainError`, which the app turns into `400` + `END_BEFORE_START`. The UI keeps the form open and shows the message. It is caught on the server so a second client (or a crafted request) cannot persist an invalid day even if the browser checks were skipped.

---

## Shipping checklist (§6.6)

- [x] Every acceptance criterion has a test (`specs/acceptance-tests.md`)
- [x] Mutation-style check is documented and should be run once locally (Step 4 above)
- [x] CI runs the full suite on every push
- [ ] CD deploys on merge to `main` once you attach a host and `DEPLOY_WEBHOOK_URL`
- [ ] A public URL exists, secrets live only in env vars, and it works on someone else’s laptop
