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

### Deploy the backend to Render

The repository includes `render.yaml`, which creates a Python web service. The
current blueprint uses SQLite, matching local development; note that Render's
free web-service filesystem is ephemeral, so use a hosted database before
production data matters.

1. Open [Render](https://dashboard.render.com), choose **New -> Blueprint**, and
  select `snbaskarraj/trip-planner`.
2. Review the `trip-planner-api` web service and `trip-planner-db` database, then
  apply the blueprint.
3. In the web service's **Environment** page, set `CORS_ORIGINS` to the exact
  deployed Vercel origin, for example `https://trip-planner.vercel.app`.
4. Set `WEATHER_API_KEY` to your provider key, or leave it empty to use the
  Open-Meteo fallback. Never commit either value.
5. Wait for `/health` to become healthy and copy the service URL, such as
  `https://trip-planner-api.onrender.com`.
6. In Vercel, set `VITE_API_BASE_URL` to that backend URL with no trailing slash and
  redeploy the frontend.

To enable the existing gated GitHub deploy job, open the Render service's
**Settings -> Deploy Hook**, copy the generated URL, and add it as a repository
secret named `DEPLOY_WEBHOOK_URL`:

```bash
gh secret set DEPLOY_WEBHOOK_URL --repo snbaskarraj/trip-planner
```

Paste the Render URL only when the GitHub CLI prompts. Do not put it in a file or
command argument. The workflow will call the hook only after backend and
frontend tests pass on a push to `main`.

1. Create a GitHub repo and push this project.
2. Open the Actions tab and confirm the workflow is green.
3. Connect `frontend/` to Vercel with **Root Directory** set to `frontend`. Set
  build-time env `VITE_API_BASE_URL` to the deployed backend origin.
4. Deploy the backend with the root `render.yaml` Blueprint ([Render dashboard → Blueprints](https://dashboard.render.com/blueprints)). New → connect `snbaskarraj/trip-planner`. When prompted, set dashboard-only env vars (never git):
   - `WEATHER_API_KEY` — OpenWeatherMap key, or leave empty to use Open-Meteo
   - `CORS_ORIGINS` — the Vercel origin, e.g. `https://your-app.vercel.app`
5. Optional automatic deploys after CI: in the Render service, open Settings → Deploy Hook, copy the URL, then add GitHub Actions secret `DEPLOY_WEBHOOK_URL`. The `deploy-backend` job on `main` will POST it only after tests pass.

```bash
# backend local fallback
cd backend
.venv/bin/uvicorn app.main:app --reload --port 8000
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
