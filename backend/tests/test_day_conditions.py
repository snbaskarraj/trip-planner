import httpx

from app.services import weather


def _add_day(client, trip_id):
    response = client.post(
        f"/api/trips/{trip_id}/days",
        json={"date": "2026-04-11", "start_time": "09:00", "end_time": "18:00"},
    )
    assert response.status_code == 201
    return response.json()


def test_conditions_timeout_returns_200_unavailable(client, trip, monkeypatch):
    day = _add_day(client, trip["id"])

    class TimingOutClient:
        def __init__(self, *args, **kwargs):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def get(self, *args, **kwargs):
            raise httpx.TimeoutException("upstream timed out")

    monkeypatch.setattr(weather.httpx, "AsyncClient", TimingOutClient)

    response = client.get(f"/api/days/{day['id']}/conditions")
    assert response.status_code == 200
    assert response.json() == {"status": "unavailable"}


def test_conditions_http_error_returns_unavailable(client, trip, monkeypatch):
    day = _add_day(client, trip["id"])

    async def fail(_destination, _day_date):
        raise httpx.HTTPStatusError(
            "boom",
            request=httpx.Request("GET", "https://example.test"),
            response=httpx.Response(503),
        )

    monkeypatch.setattr(weather, "_from_open_meteo", fail)
    monkeypatch.setattr(weather.settings, "weather_api_key", "")

    response = client.get(f"/api/days/{day['id']}/conditions")
    assert response.status_code == 200
    assert response.json()["status"] == "unavailable"


def test_missing_day_is_404_not_unavailable(client):
    response = client.get("/api/days/9999/conditions")
    assert response.status_code == 404
