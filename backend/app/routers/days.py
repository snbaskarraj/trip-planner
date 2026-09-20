from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_day_or_404
from app.models import Activity
from app.serializers import activity_to_dict, day_to_dict
from app.validation import assert_time_order

router = APIRouter(tags=["days"])


def _parse_optional_time(value):
    if value in (None, ""):
        return None
    if isinstance(value, time):
        return value
    try:
        hours, minutes = str(value).split(":")[:2]
        return time(int(hours), int(minutes))
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail="time must be HH:MM") from exc


@router.patch("/api/days/{day_id}")
def update_day(day_id: int, payload: dict, db: Session = Depends(get_db)):
    day = get_day_or_404(db, day_id)
    if "date" in payload and payload["date"]:
        try:
            day.date = date.fromisoformat(payload["date"])
        except ValueError as exc:
            raise HTTPException(status_code=422, detail="date must be YYYY-MM-DD") from exc
    if "start_time" in payload:
        day.start_time = _parse_optional_time(payload["start_time"])
    if "end_time" in payload:
        day.end_time = _parse_optional_time(payload["end_time"])
    if "notes" in payload:
        day.notes = payload["notes"]
    if "position" in payload and payload["position"] is not None:
        day.position = int(payload["position"])
    assert_time_order(day.start_time, day.end_time)
    db.commit()
    db.refresh(day)
    return day_to_dict(day)


@router.delete("/api/days/{day_id}", status_code=204)
def delete_day(day_id: int, db: Session = Depends(get_db)):
    day = get_day_or_404(db, day_id)
    db.delete(day)
    db.commit()
    return Response(status_code=204)


@router.post("/api/days/{day_id}/activities", status_code=201)
def create_activity(day_id: int, payload: dict, db: Session = Depends(get_db)):
    get_day_or_404(db, day_id)
    title = (payload.get("title") or "").strip()
    if not title:
        raise HTTPException(status_code=422, detail="title is required")
    start_time = _parse_optional_time(payload.get("start_time"))
    end_time = _parse_optional_time(payload.get("end_time"))
    assert_time_order(start_time, end_time)
    activity = Activity(
        day_id=day_id,
        title=title,
        location=payload.get("location"),
        start_time=start_time,
        end_time=end_time,
        notes=payload.get("notes"),
        position=int(payload.get("position") or 0),
    )
    db.add(activity)
    db.commit()
    db.refresh(activity)
    return activity_to_dict(activity)
