"""Maps/weather wrapper.

The rest of the codebase must import this module — never the vendor HTTP
APIs — so a timeout or outage can be turned into the contract's
{"status": "unavailable"} shape instead of an exception.
"""

from __future__ import annotations

import logging
from datetime import date

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

UNAVAILABLE = {"status": "unavailable"}

OPEN_METEO_GEOCODE = "https://geocoding-api.open-meteo.com/v1/search"
OPEN_METEO_FORECAST = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_ARCHIVE = "https://archive-api.open-meteo.com/v1/archive"
OPENWEATHER_GEOCODE = "https://api.openweathermap.org/geo/1.0/direct"
OPENWEATHER_FORECAST = "https://api.openweathermap.org/data/2.5/weather"


def _timeout() -> httpx.Timeout:
    seconds = settings.weather_timeout_seconds
    return httpx.Timeout(seconds)


async def get_day_conditions(destination: str, day_date: date) -> dict:
    """Return the api-contract success or unavailable shape. Never raises."""
    try:
        if settings.weather_api_key:
            return await _from_openweather(destination, day_date)
        return await _from_open_meteo(destination, day_date)
    except Exception as exc:  # vendor down, timeout, parse, missing coords
        logger.info("weather unavailable: %s", type(exc).__name__)
        return dict(UNAVAILABLE)


async def _from_open_meteo(destination: str, day_date: date) -> dict:
    async with httpx.AsyncClient(timeout=_timeout()) as client:
        geo = await client.get(
            OPEN_METEO_GEOCODE,
            params={"name": destination, "count": 1},
        )
        geo.raise_for_status()
        results = geo.json().get("results") or []
        if not results:
            raise ValueError("no geocode match")
        lat = results[0]["latitude"]
        lon = results[0]["longitude"]
        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "weathercode,temperature_2m_max,windspeed_10m_max",
            "timezone": "auto",
            "start_date": day_date.isoformat(),
            "end_date": day_date.isoformat(),
        }
        # Forecast rejects historical dates with 400; archive covers the past.
        url = OPEN_METEO_ARCHIVE if day_date < date.today() else OPEN_METEO_FORECAST
        forecast = await client.get(url, params=params)
        if forecast.status_code >= 400:
            fallback = OPEN_METEO_FORECAST if url == OPEN_METEO_ARCHIVE else OPEN_METEO_ARCHIVE
            forecast = await client.get(fallback, params=params)
        forecast.raise_for_status()
        daily = forecast.json().get("daily") or {}
        temps = [t for t in (daily.get("temperature_2m_max") or []) if t is not None]
        winds = daily.get("windspeed_10m_max") or []
        codes = daily.get("weathercode") or []
        if not temps:
            raise ValueError("no forecast row")
        return {
            "status": "ok",
            "destination": destination,
            "date": day_date.isoformat(),
            "temperature_c": float(temps[0]),
            "summary": _wmo_summary(codes[0] if codes else None),
            "wind_kph": float(winds[0]) if winds else None,
        }


async def _from_openweather(destination: str, day_date: date) -> dict:
    """Used only when WEATHER_API_KEY is set. Key never appears in the result."""
    key = settings.weather_api_key
    async with httpx.AsyncClient(timeout=_timeout()) as client:
        geo = await client.get(
            OPENWEATHER_GEOCODE,
            params={"q": destination, "limit": 1, "appid": key},
        )
        geo.raise_for_status()
        places = geo.json()
        if not places:
            raise ValueError("no geocode match")
        lat = places[0]["lat"]
        lon = places[0]["lon"]
        weather = await client.get(
            OPENWEATHER_FORECAST,
            params={"lat": lat, "lon": lon, "appid": key, "units": "metric"},
        )
        weather.raise_for_status()
        payload = weather.json()
        return {
            "status": "ok",
            "destination": destination,
            "date": day_date.isoformat(),
            "temperature_c": float(payload["main"]["temp"]),
            "summary": (payload.get("weather") or [{}])[0].get("description", "Weather"),
            "wind_kph": float(payload.get("wind", {}).get("speed", 0)) * 3.6,
        }


def _wmo_summary(code: int | None) -> str:
    if code is None:
        return "Forecast"
    if code == 0:
        return "Clear"
    if code in {1, 2, 3}:
        return "Partly cloudy"
    if code in {45, 48}:
        return "Fog"
    if code in {51, 53, 55, 56, 57}:
        return "Drizzle"
    if code in {61, 63, 65, 66, 67, 80, 81, 82}:
        return "Rain"
    if code in {71, 73, 75, 77, 85, 86}:
        return "Snow"
    if code in {95, 96, 99}:
        return "Thunderstorm"
    return "Forecast"
