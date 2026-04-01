from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class DogConfig:
    name: str = "Hihi"
    breed: str = "Shiba Inu"


@dataclass
class LocationConfig:
    city: str = "Harumi, Chuo-ku, Tokyo"
    lat: float = 35.6605
    lon: float = 139.7868


@dataclass
class ScheduleConfig:
    evening_reminder: str = "20:00"
    morning_reminder: str = "07:00"
    timezone: str = "Asia/Tokyo"


@dataclass
class WalkSession:
    name: str
    time_range: tuple[str, str]
    preferred_time: str
    duration_min: int = 30


@dataclass
class NotificationsConfig:
    platform: str = "wechat"


@dataclass
class ApiConfig:
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-5-20250514"


@dataclass
class AppConfig:
    dog: DogConfig = field(default_factory=DogConfig)
    location: LocationConfig = field(default_factory=LocationConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    walks: list[WalkSession] = field(default_factory=lambda: [
        WalkSession("midday", ("11:00", "14:00"), "12:00", 30),
        WalkSession("evening", ("17:00", "21:00"), "19:00", 30),
    ])
    language: str = "zh"
    notifications: NotificationsConfig = field(default_factory=NotificationsConfig)
    api: ApiConfig = field(default_factory=ApiConfig)


def _parse_walk_session(raw: dict) -> WalkSession:
    tr = raw.get("time_range", ["06:00", "22:00"])
    return WalkSession(
        name=raw.get("name", "walk"),
        time_range=(tr[0], tr[1]),
        preferred_time=raw.get("preferred_time", tr[0]),
        duration_min=raw.get("duration_min", 30),
    )


def load_config(path: str | Path | None = None) -> AppConfig:
    if path is None:
        path = os.environ.get(
            "SHIBA_CONFIG", Path(__file__).resolve().parent.parent / "config.yaml"
        )
    path = Path(path)
    if not path.exists():
        return AppConfig()

    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}

    walks_raw = raw.get("walks", [])
    walks = [_parse_walk_session(w) for w in walks_raw] if walks_raw else AppConfig.walks

    # API key: config.yaml -> env var -> empty
    api_raw = raw.get("api", {})
    api_key = (
        api_raw.get("anthropic_api_key")
        or os.environ.get("ANTHROPIC_API_KEY")
        or ""
    )
    api = ApiConfig(
        anthropic_api_key=api_key,
        anthropic_model=api_raw.get("anthropic_model", "claude-sonnet-4-5-20250514"),
    )

    return AppConfig(
        dog=DogConfig(**raw.get("dog", {})),
        location=LocationConfig(**raw.get("location", {})),
        schedule=ScheduleConfig(**raw.get("schedule", {})),
        walks=walks,
        language=raw.get("language", "zh"),
        notifications=NotificationsConfig(**raw.get("notifications", {})),
        api=api,
    )
