# Acceptance criteria → test table

Written before the tests (Phase 4 / §6.1). Every row has at least one automated test.

| Acceptance criterion | Test type | Where |
|---|---|---|
| A Day cannot be saved with an end time before its start time | Unit | `backend/tests/test_validation.py` |
| Creating a Day via the API with end before start returns 400 `END_BEFORE_START` | Integration | `backend/tests/test_validation.py` |
| The itinerary still renders with “unavailable” when the maps/weather call times out | Integration | `backend/tests/test_day_conditions.py` (API) + `frontend/src/conditionsBanner.test.jsx` (UI) |
| Day-conditions never returns 5xx on upstream failure | Integration | `backend/tests/test_day_conditions.py` |
| Share links are read-only and require no login | Integration | `backend/tests/test_share.py` |
| Trip date range cannot be inverted | Unit | `backend/tests/test_validation.py` |
| Health endpoint returns ok | Integration | `backend/tests/test_health.py` |
