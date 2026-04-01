from datetime import datetime, timedelta

from src.config import load_config
from src.weather import fetch_hourly_forecast
from src.ai_planner import generate_walk_plan


def main() -> None:
    config = load_config()
    print(f"Fetching weather for {config.location.city}...\n")

    forecast = fetch_hourly_forecast(
        lat=config.location.lat,
        lon=config.location.lon,
        forecast_days=2,
    )

    tomorrow = datetime.now() + timedelta(days=1)

    print(f"Generating walk plan for {config.dog.name} "
          f"({tomorrow.strftime('%m月%d日')})...\n")

    plan = generate_walk_plan(config, forecast, tomorrow)
    print(plan)


if __name__ == "__main__":
    main()
