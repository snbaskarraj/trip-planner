# Goal Spec — Trip Planner

Goal: let a user plan a multi-day trip and produce a shareable itinerary.

Constraints: React frontend, FastAPI backend, a relational database. The external maps/weather API key must never appear in client-side code; it is read only on the server from an environment variable and is never returned in any response body.

Acceptance criteria:

- Itinerary CRUD: a user can create, read, update, and delete a trip, each day’s plan, and the activities on a day.
- A day cannot be saved when its end time is before its start time; the API rejects the write and the editor shows the error.
- A user can save a trip and share it by a read-only link that requires no login.
- When the maps/weather API call fails or times out, the itinerary still renders with a clear “unavailable” state and never crashes.
- Share links expose the itinerary for reading only; they do not accept writes.
