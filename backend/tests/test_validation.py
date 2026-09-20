from datetime import time

import pytest

from app.validation import DomainError, assert_date_order, assert_time_order


def test_end_time_before_start_time_is_rejected():
    with pytest.raises(DomainError) as exc:
        assert_time_order(time(18, 0), time(9, 0))
    assert exc.value.code == "END_BEFORE_START"
    assert "end_time" in exc.value.message


def test_equal_times_are_allowed():
    assert_time_order(time(9, 0), time(9, 0))


def test_missing_times_are_allowed():
    assert_time_order(time(9, 0), None)
    assert_time_order(None, time(18, 0))
    assert_time_order(None, None)


def test_inverted_trip_dates_are_rejected():
    from datetime import date

    with pytest.raises(DomainError) as exc:
        assert_date_order(date(2026, 4, 14), date(2026, 4, 10))
    assert exc.value.code == "END_BEFORE_START"


def test_create_day_rejects_end_before_start(client, trip):
    """Mutation-check target: this must fail if the Day create endpoint skips validation."""
    response = client.post(
        f"/api/trips/{trip['id']}/days",
        json={
            "date": "2026-04-11",
            "start_time": "18:00",
            "end_time": "09:00",
            "notes": "should not persist",
        },
    )
    assert response.status_code == 400
    body = response.json()
    assert body["code"] == "END_BEFORE_START"
    assert "end_time" in body["detail"]

    itinerary = client.get(f"/api/trips/{trip['id']}")
    assert itinerary.status_code == 200
    assert itinerary.json()["days"] == []
