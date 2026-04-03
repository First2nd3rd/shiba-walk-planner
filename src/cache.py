from __future__ import annotations

import json
from pathlib import Path

CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
SUMMARY_FILE = CACHE_DIR / "weather_summary.json"


def save_summary(summary: dict) -> None:
    CACHE_DIR.mkdir(exist_ok=True)
    SUMMARY_FILE.write_text(json.dumps(summary, ensure_ascii=False), encoding="utf-8")


def load_summary() -> dict | None:
    if not SUMMARY_FILE.exists():
        return None
    try:
        return json.loads(SUMMARY_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
