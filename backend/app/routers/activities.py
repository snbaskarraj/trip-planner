from datetime import time

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_activity_or_404
from app.serializers import activity_to_dict
from app.validation import assert_time_order

router = APIRouter(prefix="/api/activities", tags=["activities"])


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


@router.patch("/{activity_id}")
def update_activity(activity_id: int, payload: dict, db: Session = Depends(get_db)):
    activity = get_activity_or_404(db, activity_id)
    if "title" in payload:
        title = (payload.get("title") or "").strip()
        if not title:
            raise HTTPException(status_code=422, detail="title is required")
        activity.title = title
    if "location" in payload:
        activity.location = payload["location"]
    if "start_time" in payload:
        activity.start_time = _parse_optional_time(payload["start_time"])
    if "end_time" in payload:
        activity.end_time = _parse_optional_time(payload["end_time"])
    if "notes" in payload:
        activity.notes = payload["notes"]
    if "position" in payload and payload["position"] is not None:
        activity.position = int(payload["position"])
    assert_time_order(activity.start_time, activity.end_time)
    db.commit()
    db.refresh(activity)
    return activity_to_dict(activity)


@router.delete("/{activity_id}", status_code=204)
def delete_activity(activity_id: int, db: Session = Depends(get_db)):
    activity = get_activity_or_404(db, activity_id)
    db.delete(activity)
    db.commit()
    return Response(status_code=204)
