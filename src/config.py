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
    city: str = "東京都中央区晴海"
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
class AppConfig:
    dog: DogConfig = field(default_factory=DogConfig)
    location: LocationConfig = field(default_factory=LocationConfig)
    schedule: ScheduleConfig = field(default_factory=ScheduleConfig)
    walks: list[WalkSession] = field(default_factory=lambda: [
        WalkSession("午遛", ("11:00", "14:00"), "12:00", 30),
        WalkSession("晚遛", ("17:00", "21:00"), "19:00", 30),
    ])
    language: str = "zh"
    notifications: NotificationsConfig = field(default_factory=NotificationsConfig)


def _parse_walk_session(raw: dict) -> WalkSession:
    tr = raw.get("time_range", ["06:00", "22:00"])
    return WalkSession(
        name=raw.get("name", "遛狗"),
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

    return AppConfig(
        dog=DogConfig(**raw.get("dog", {})),
        location=LocationConfig(**raw.get("location", {})),
        schedule=ScheduleConfig(**raw.get("schedule", {})),
        walks=walks,
        language=raw.get("language", "zh"),
        notifications=NotificationsConfig(**raw.get("notifications", {})),
    )
