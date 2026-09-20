# Back-End Spec — Trip Planner

Derived from `specs/goal-spec.md` and `specs/frontend-spec.md`.

## Data model

Relational, 1-to-many throughout: **Trip has many Days; each Day has many Activities.**

### Trip

| Column | Type | Rules |
|---|---|---|
| id | integer PK | autoincrement |
| title | string | required, 1–200 chars |
| destination | string | required, 1–200 chars; used as the weather/geocode query |
| start_date | date | required |
| end_date | date | required; must be on or after start_date |
| share_token | string | unique, generated server-side, never chosen by the client |
| created_at | datetime | set on insert |
| updated_at | datetime | set on insert and update |

### Day

| Column | Type | Rules |
|---|---|---|
| id | integer PK | autoincrement |
| trip_id | FK → trips.id | required, cascade delete |
| date | date | required |
| start_time | time | optional |
| end_time | time | optional; **must not be before start_time when both are set** |
| notes | text | optional |
| position | integer | display order within the trip, default 0 |

### Activity

| Column | Type | Rules |
|---|---|---|
| id | integer PK | autoincrement |
| day_id | FK → days.id | required, cascade delete |
| title | string | required, 1–200 chars |
| location | string | optional |
| start_time | time | optional |
| end_time | time | optional; must not be before start_time when both are set |
| notes | text | optional |
| position | integer | display order within the day, default 0 |

## Business rules

1. A Day cannot be saved (create or update) with an end time before its start time. Reject with `400` and a stable error code `END_BEFORE_START`.
2. The same time-order rule applies to Activity create/update.
3. A trip’s `end_date` cannot be before its `start_date`.
4. Deleting a Trip cascades to its Days and Activities.
5. Deleting a Day cascades to its Activities.
6. `share_token` is generated once at Trip creation and is immutable.
7. The share endpoint is read-only: `GET` only. There is no write route keyed by `share_token`.
8. Day-conditions (maps/weather) are fetched only through the dedicated endpoint. Upstream failure or timeout is an **expected** condition: return HTTP 200 with `{"status":"unavailable"}`. Never raise a 5xx because the weather vendor is down.

## Non-functional requirements

- **Share links are read-only and require no login.** `GET /api/share/{token}` is unauthenticated. Possession of the token is the only authorization. No session, cookie, or user id is required.
- **The maps/weather API key is read server-side only.** It is loaded from the `WEATHER_API_KEY` environment variable. It is never written to the database, never logged in full, and never returned in any response body (including error bodies). The frontend must not import, bundle, or display this key.
- The maps/weather vendor is reached only from `app/services/weather.py`. Routers call that wrapper; they do not call the vendor HTTP API themselves. The wrapper never raises to the router: every failure path returns the unavailable shape.

## External integration

The day-conditions endpoint asks the wrapper for a forecast for the trip’s `destination` on the day’s `date`. The wrapper may call a geocoding step then a weather step. Timeouts are short (a few seconds). Any of: missing key (when the configured vendor requires one), DNS failure, HTTP error, JSON parse error, or timeout → unavailable shape.
