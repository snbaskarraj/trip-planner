from datetime import datetime, time


def fmt_time(value: time | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%H:%M")


def fmt_dt(value: datetime | None) -> str | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.isoformat() + "Z"
    return value.isoformat().replace("+00:00", "Z")


def activity_to_dict(activity) -> dict:
    return {
        "id": activity.id,
        "day_id": activity.day_id,
        "title": activity.title,
        "location": activity.location,
        "start_time": fmt_time(activity.start_time),
        "end_time": fmt_time(activity.end_time),
        "notes": activity.notes,
        "position": activity.position,
    }


def day_to_dict(day) -> dict:
    return {
        "id": day.id,
        "trip_id": day.trip_id,
        "date": day.date.isoformat(),
        "start_time": fmt_time(day.start_time),
        "end_time": fmt_time(day.end_time),
        "notes": day.notes,
        "position": day.position,
        "activities": [activity_to_dict(a) for a in day.activities],
    }


def trip_to_dict(trip) -> dict:
    return {
        "id": trip.id,
        "title": trip.title,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat(),
        "end_date": trip.end_date.isoformat(),
        "share_token": trip.share_token,
        "created_at": fmt_dt(trip.created_at),
        "updated_at": fmt_dt(trip.updated_at),
        "days": [day_to_dict(d) for d in trip.days],
    }


def trip_summary(trip) -> dict:
    return {
        "id": trip.id,
        "title": trip.title,
        "destination": trip.destination,
        "start_date": trip.start_date.isoformat(),
        "end_date": trip.end_date.isoformat(),
        "created_at": fmt_dt(trip.created_at),
    }
