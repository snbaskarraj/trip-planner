# Front-End Spec — Trip Planner

Derived from `specs/goal-spec.md`. No implementation notes — screens, flow, and given/then acceptance only.

## Screens

1. **Trip List** (`/`) — index of the user’s trips and the place to start a new one.
2. **Itinerary Editor** (`/trips/:tripId`) — the working surface for a trip: days, activities, weather/conditions, share link.
3. **Share View** (`/share/:token`) — read-only itinerary for anyone with the link. No login. No edit controls.

## User flow

```
Trip List
  ├─ create trip ─────────────► Itinerary Editor
  ├─ open existing trip ──────► Itinerary Editor
  └─ (from a shared URL) ─────► Share View

Itinerary Editor
  ├─ add / edit / delete days and activities
  ├─ copy share link ─────────► Share View (new tab / pasted URL)
  └─ back ────────────────────► Trip List
```

## Acceptance criteria

### Trip List

- Given the trip list is fetching, the UI shows a loading state (“Loading trips…”) and no stale cards.
- Given the user has no trips, the UI shows an empty state inviting them to create their first trip.
- Given the user has one or more trips, the UI lists each trip’s title, destination, and date range, and each card is a link to the Itinerary Editor.
- Given the create-trip request is in flight, the submit control is disabled and labeled as saving.
- Given create succeeds, the UI navigates to the new trip’s Itinerary Editor.
- Given list or create fails (network or 4xx/5xx), the UI shows an error banner with the failure reason and a retry control; it does not crash.
- Given the user confirms delete on a trip, that trip disappears from the list; given delete fails, the trip remains and an error is shown.

### Itinerary Editor

- Given the trip is fetching, the UI shows a loading state for the itinerary.
- Given the trip id does not exist, the UI shows a not-found state with a link back to the Trip List.
- Given the trip loads and has no days, the UI shows the trip header plus an empty-days prompt to add the first day.
- Given the trip has days, the UI shows each day with its date, start/end time, notes, and nested activities.
- Given the user submits a day whose end time is before its start time, the UI does not close the form; it shows the validation error returned by the API.
- Given a day or activity write succeeds, the itinerary re-renders with the new data (no full-page reload).
- Given any CRUD call fails, the UI shows an inline error and keeps the last good itinerary on screen.
- Given day-conditions are loading, the day’s weather panel shows a loading label.
- Given day-conditions return `{"status":"ok", ...}`, the day’s weather panel shows temperature and summary.
- Given day-conditions return `{"status":"unavailable"}` (timeout, upstream error, or missing key), the day’s weather panel shows a clear “Weather unavailable” state; the rest of the itinerary remains visible and usable. The page never crashes or goes blank.
- Given the user clicks “Copy share link”, the clipboard receives `/share/:token` and a confirmation is shown.

### Share View

- Given the share token is fetching, the UI shows a loading state.
- Given the token is unknown, the UI shows a not-found / invalid-link state. There is no editor chrome.
- Given the token is valid and the trip has no days, the UI shows the trip title and an empty itinerary message.
- Given the token is valid and the trip has days, the UI renders the full itinerary read-only: no add/edit/delete controls.
- Given day-conditions are unavailable, the share view still renders the itinerary with the same “Weather unavailable” treatment as the editor.
- Given the fetch fails, the UI shows an error state with retry; it does not crash.

## Non-goals for the UI

- Authentication / login screens (out of scope; share links are public read-only).
- Map tiles rendered in the browser using a client-side maps key.
- Offline editing.
