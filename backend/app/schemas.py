from datetime import date as Date
from datetime import datetime, time

from pydantic import BaseModel, ConfigDict, Field


def _fmt_time(value: time | None) -> str | None:
    if value is None:
        return None
    return value.strftime("%H:%M")


class ActivityCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    start_time: time | None = None
    end_time: time | None = None
    notes: str | None = None
    position: int = 0


class ActivityUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    location: str | None = Field(default=None, max_length=200)
    start_time: time | None = None
    end_time: time | None = None
    notes: str | None = None
    position: int | None = None


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    day_id: int
    title: str
    location: str | None
    start_time: time | None
    end_time: time | None
    notes: str | None
    position: int

    def model_dump_api(self) -> dict:
        data = self.model_dump()
        data["start_time"] = _fmt_time(self.start_time)
        data["end_time"] = _fmt_time(self.end_time)
        return data


class DayCreate(BaseModel):
    date: Date
    start_time: time | None = None
    end_time: time | None = None
    notes: str | None = None
    position: int = 0


class DayUpdate(BaseModel):
    date: Date | None = None
    start_time: time | None = None
    end_time: time | None = None
    notes: str | None = None
    position: int | None = None


class DayOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    trip_id: int
    date: Date
    start_time: time | None
    end_time: time | None
    notes: str | None
    position: int
    activities: list[ActivityOut] = []


class TripCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    destination: str = Field(min_length=1, max_length=200)
    start_date: Date
    end_date: Date


class TripUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    destination: str | None = Field(default=None, max_length=200)
    start_date: Date | None = None
    end_date: Date | None = None


class TripSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    destination: str
    start_date: Date
    end_date: Date
    created_at: datetime


class TripOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    destination: str
    start_date: Date
    end_date: Date
    share_token: str
    created_at: datetime
    updated_at: datetime
    days: list[DayOut] = []


class TripListOut(BaseModel):
    trips: list[TripSummary]


class ConditionsOk(BaseModel):
    status: str = "ok"
    destination: str
    date: Date
    temperature_c: float
    summary: str
    wind_kph: float | None = None


class ConditionsUnavailable(BaseModel):
    status: str = "unavailable"


class HealthOut(BaseModel):
    status: str = "ok"
