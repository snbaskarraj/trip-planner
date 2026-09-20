import secrets

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_trip_or_404
from app.models import Trip
from app.schemas import TripCreate, TripUpdate
from app.serializers import trip_summary, trip_to_dict
from app.validation import assert_date_order

router = APIRouter(prefix="/api/trips", tags=["trips"])


@router.get("")
def list_trips(db: Session = Depends(get_db)):
    trips = db.query(Trip).order_by(Trip.created_at.desc()).all()
    return {"trips": [trip_summary(t) for t in trips]}


@router.post("", status_code=201)
def create_trip(payload: TripCreate, db: Session = Depends(get_db)):
    assert_date_order(payload.start_date, payload.end_date)
    trip = Trip(
        title=payload.title,
        destination=payload.destination,
        start_date=payload.start_date,
        end_date=payload.end_date,
        share_token=secrets.token_hex(16),
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip_to_dict(trip)


@router.get("/{trip_id}")
def get_trip(trip_id: int, db: Session = Depends(get_db)):
    return trip_to_dict(get_trip_or_404(db, trip_id))


@router.patch("/{trip_id}")
def update_trip(trip_id: int, payload: TripUpdate, db: Session = Depends(get_db)):
    trip = get_trip_or_404(db, trip_id)
    data = payload.model_dump(exclude_unset=True)
    start = data.get("start_date", trip.start_date)
    end = data.get("end_date", trip.end_date)
    assert_date_order(start, end)
    for key, value in data.items():
        setattr(trip, key, value)
    db.commit()
    db.refresh(trip)
    return trip_to_dict(trip)


@router.delete("/{trip_id}", status_code=204)
def delete_trip(trip_id: int, db: Session = Depends(get_db)):
    trip = get_trip_or_404(db, trip_id)
    db.delete(trip)
    db.commit()
    return Response(status_code=204)


@router.post("/{trip_id}/days", status_code=201)
def create_day(trip_id: int, payload: dict, db: Session = Depends(get_db)):
    """Create a Day. Time-order validation lives here so the mutation check can target it."""
    from datetime import date

    from app.models import Day
    from app.serializers import day_to_dict
    from app.validation import assert_time_order

    get_trip_or_404(db, trip_id)
    try:
        day_date = date.fromisoformat(payload["date"])
    except (KeyError, TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail="date is required (YYYY-MM-DD)") from exc

    start_time = _parse_optional_time(payload.get("start_time"))
    end_time = _parse_optional_time(payload.get("end_time"))

    # --- mutation-check target: comment out the next line to verify the test ---
    assert_time_order(start_time, end_time)
    # --- end mutation-check target ---

    day = Day(
        trip_id=trip_id,
        date=day_date,
        start_time=start_time,
        end_time=end_time,
        notes=payload.get("notes"),
        position=int(payload.get("position") or 0),
    )
    db.add(day)
    db.commit()
    db.refresh(day)
    return day_to_dict(day)


def _parse_optional_time(value):
    from datetime import time

    if value in (None, ""):
        return None
    if isinstance(value, time):
        return value
    try:
        hours, minutes = str(value).split(":")[:2]
        return time(int(hours), int(minutes))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail="time must be HH:MM") from exc
