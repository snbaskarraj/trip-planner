# Build Plan — Trip Planner

Plan-only. Implementation follows this order; each task is one reviewable diff.

## Order

1. **Schema + migration** — SQLAlchemy models for Trip, Day, Activity; Alembic revision `001_initial_schema`; SQLite file database. No HTTP yet beyond the existing `/health`.
2. **CRUD endpoints** — trips, days, activities per `specs/api-contract.md`, including `END_BEFORE_START` on Day (and Activity) writes. Share `GET` included here because it is a read of the same aggregate.
3. **React views** — Trip List, Itinerary Editor, Share View. Loading / empty / error / not-found states from `specs/frontend-spec.md`. Talk to the CRUD + share endpoints only.
4. **Maps/weather wrapper** — `app/services/weather.py` as the only vendor client. Day-conditions router calls it and always maps failures to `200 {"status":"unavailable"}`. Editor + Share View consume the endpoint.
5. **Tests** — unit: inverted day times; integration: conditions timeout → 200 unavailable; integration: share GET is unauthenticated read-only.
6. **CI** — GitHub Actions: pytest + frontend vitest on every push/PR.
7. **Container + deploy docs** — backend Dockerfile (key from env, never baked in); Vercel notes for `frontend/` with `VITE_API_URL`.

## Out of scope for v1

Login, multi-user ownership, paid maps tiles, mobile native apps.
