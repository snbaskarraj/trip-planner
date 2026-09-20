from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Activity, Day, Trip
from app.validation import DomainError


def domain_http(exc: DomainError) -> HTTPException:
    return HTTPException(status_code=400, detail={"detail": exc.message, "code": exc.code})


def get_trip_or_404(db: Session, trip_id: int) -> Trip:
    trip = db.get(Trip, trip_id)
    if trip is None:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip


def get_day_or_404(db: Session, day_id: int) -> Day:
    day = db.get(Day, day_id)
    if day is None:
        raise HTTPException(status_code=404, detail="Day not found")
    return day


def get_activity_or_404(db: Session, activity_id: int) -> Activity:
    activity = db.get(Activity, activity_id)
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity
