from __future__ import annotations

from datetime import datetime

import anthropic

from src.config import AppConfig, WalkSession
from src.weather import HourlyWeather

SYSTEM_PROMPT = """\
You are a dog walk planning assistant. Your job is to analyze hourly weather \
forecast data and recommend optimal walk times based on the user's walking habits.

## How you work
1. Analyze the hourly weather data (precipitation, temperature, wind speed)
2. Match against the user's walk schedule (sessions per day, preferred times, duration)
3. Provide specific time recommendations

## Recommendation strategy
- Prefer dry windows within the user's preferred time ranges
- If preferred slots have rain, find the lightest rain period and remind to bring an umbrella
- If heavy rain all day, suggest reducing walk count and extending each session
- Temperature: hot (>35C) avoid midday, remind to bring water and watch for hot pavement; \
cold (<0C) suggest shorter walks; strong wind (>40km/h) warn about safety
- Factor in breed-specific traits when provided (e.g., double-coat breeds are heat-sensitive)

## Output rules
- Friendly and casual tone, like a friend reminding — not formal
- Concise: 2-5 sentences with actionable advice
- Always include specific times
- Always remind about gear when needed (umbrella, raincoat, water)
- IMPORTANT: Reply in the language specified by the user
"""


def _format_weather_data(
    forecast: list[HourlyWeather], target_date: datetime
) -> str:
    day_hours = [h for h in forecast if h.time.date() == target_date.date()]
    if not day_hours:
        return "No weather data available"

    lines = ["Time | Precip(mm) | Temp(C) | Wind(km/h) | Level"]
    lines.append("-----|------------|---------|------------|------")
    for h in day_hours:
        lines.append(
            f"{h.time.strftime('%H:%M')} | {h.precipitation_mm:.1f} | "
            f"{h.temperature_c:.1f} | {h.wind_speed_kmh:.1f} | {h.rain_level}"
        )
    return "\n".join(lines)


def _format_walk_habits(walks: list[WalkSession]) -> str:
    lines = [f"{len(walks)} walks per day:"]
    for w in walks:
        lines.append(
            f"- {w.name}: preferred {w.preferred_time}, "
            f"acceptable range {w.time_range[0]}-{w.time_range[1]}, "
            f"usually {w.duration_min} min"
        )
    return "\n".join(lines)


def generate_walk_plan(
    config: AppConfig,
    forecast: list[HourlyWeather],
    target_date: datetime,
) -> str:
    weather_table = _format_weather_data(forecast, target_date)
    walk_habits = _format_walk_habits(config.walks)

    user_message = f"""\
## Info
- Dog: {config.dog.name} ({config.dog.breed})
- Location: {config.location.city}
- Date: {target_date.strftime('%Y-%m-%d')}
- Reply language: {config.language}

## Walk schedule
{walk_habits}

## Hourly weather forecast
{weather_table}

Based on the above, provide walk plan recommendations for this day."""

    client = anthropic.Anthropic(api_key=config.api.anthropic_api_key or None)
    message = client.messages.create(
        model=config.api.anthropic_model,
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text
