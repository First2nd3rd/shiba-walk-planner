---
name: walk-planner
description: >
  AI-driven dog walk planner skill. Analyzes hourly weather forecast data
  and generates personalized walk time recommendations based on user's
  dog walking habits, preferred schedule, and weather conditions.
triggers:
  - "walk plan"
  - "遛狗"
  - "weather forecast"
  - "天气"
---

# Walk Planner Skill

## When to activate
- User asks about walk planning, dog walking schedule, or weather-based recommendations
- User wants to generate or test walk plan output
- User wants to modify the AI planner prompt or weather analysis logic

## Architecture

The planner is AI-first, not rule-based:
1. `src/weather.py` fetches hourly forecast from Open-Meteo API (no key needed)
2. `src/ai_planner.py` sends structured weather data + user config to Claude API
3. Claude analyzes weather patterns and generates natural language walk recommendations

### Why AI over rules
- Weather interpretation is nuanced (0.1mm drizzle vs 0.1mm ending-rain are different)
- Tone and language adaptation (zh/en/ja) comes free
- Edge cases (typhoon warning, sudden temperature drop, pollen season) don't need explicit rules
- Can factor in breed-specific knowledge (Shiba double coat, heat sensitivity)

## Key files
- `src/weather.py` — Open-Meteo hourly forecast fetcher, `HourlyWeather` dataclass
- `src/ai_planner.py` — Claude API integration, system prompt, weather data formatting
- `src/config.py` — User config loader (dog, location, walk sessions, language)
- `config.yaml` — User-facing config (walks list is fully customizable)

## Config: Walk sessions
Users define their walk habits in `config.yaml` under `walks`:
```yaml
walks:
  - name: "午遛"
    time_range: ["11:00", "14:00"]
    preferred_time: "12:00"
    duration_min: 30
  - name: "晚遛"
    time_range: ["17:00", "21:00"]
    preferred_time: "19:00"
    duration_min: 30
```
Number of sessions, time ranges, and durations are all user-customizable.

## AI planner prompt strategy
The system prompt in `src/ai_planner.py` instructs Claude to:
- Prioritize dry windows within user's preferred time ranges
- Fall back to light rain periods with gear reminders
- Suggest reducing walk count in severe weather (e.g., 3→2 sessions, longer each)
- Give breed-specific advice (Shiba: heat-sensitive, cold-tolerant)
- Keep output friendly and concise (2-5 sentences)
- Always include specific times and gear reminders

## Testing
```bash
conda activate shiba-walk
cd ~/Documents/project/shiba-walk-planner
python -m src.main
```
Requires `ANTHROPIC_API_KEY` environment variable.
