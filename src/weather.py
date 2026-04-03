from __future__ import annotations

import json
import urllib.request
import urllib.parse
from dataclasses import dataclass
from datetime import datetime


@dataclass
class HourlyWeather:
    time: datetime
    precipitation_mm: float
    rain_mm: float
    showers_mm: float
    snowfall_cm: float
    temperature_c: float
    wind_speed_kmh: float
    wind_gusts_kmh: float

    @property
    def is_dry(self) -> bool:
        return self.precipitation_mm == 0.0

    @property
    def rain_level(self) -> str:
        p = self.precipitation_mm
        if p == 0:
            return "none"
        if p < 1:
            return "light"
        if p < 4:
            return "moderate"
        if p < 10:
            return "heavy"
        return "torrential"


API_URL = "https://api.open-meteo.com/v1/forecast"

HOURLY_VARS = [
    "precipitation",
    "rain",
    "showers",
    "snowfall",
    "temperature_2m",
    "wind_speed_10m",
    "wind_gusts_10m",
]


def fetch_hourly_forecast(
    lat: float, lon: float, forecast_days: int = 2
) -> list[HourlyWeather]:
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "hourly": ",".join(HOURLY_VARS),
        "timezone": "auto",
        "forecast_days": forecast_days,
    })
    url = f"{API_URL}?{params}"

    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        data = json.loads(resp.read().decode())

    if data.get("error"):
        raise RuntimeError(f"Open-Meteo API error: {data.get('reason', 'unknown')}")

    hourly = data["hourly"]
    results: list[HourlyWeather] = []

    for i, time_str in enumerate(hourly["time"]):
        results.append(HourlyWeather(
            time=datetime.fromisoformat(time_str),
            precipitation_mm=hourly["precipitation"][i] or 0.0,
            rain_mm=hourly["rain"][i] or 0.0,
            showers_mm=hourly["showers"][i] or 0.0,
            snowfall_cm=hourly["snowfall"][i] or 0.0,
            temperature_c=hourly["temperature_2m"][i] or 0.0,
            wind_speed_kmh=hourly["wind_speed_10m"][i] or 0.0,
            wind_gusts_kmh=hourly["wind_gusts_10m"][i] or 0.0,
        ))

    return results


def summarize_weather(
    forecast: list[HourlyWeather], target_date: datetime,
) -> dict:
    """Extract a compact summary of the day's weather for comparison."""
    day_hours = [h for h in forecast if h.time.date() == target_date.date()]
    return {
        "date": target_date.strftime("%Y-%m-%d"),
        "hours": [
            {
                "time": h.time.strftime("%H:%M"),
                "precip": round(h.precipitation_mm, 1),
                "rain_level": h.rain_level,
                "temp": round(h.temperature_c, 1),
            }
            for h in day_hours
        ],
    }


def weather_changed(old_summary: dict, new_summary: dict) -> bool:
    """Check if weather changed significantly between two summaries."""
    old_hours = {h["time"]: h for h in old_summary.get("hours", [])}
    new_hours = {h["time"]: h for h in new_summary.get("hours", [])}

    for time_key, new_h in new_hours.items():
        old_h = old_hours.get(time_key)
        if old_h is None:
            continue
        # Rain level changed (e.g. none → light, moderate → heavy)
        if old_h["rain_level"] != new_h["rain_level"]:
            return True
        # Temperature shifted by more than 3°C
        if abs(old_h["temp"] - new_h["temp"]) > 3.0:
            return True

    return False
