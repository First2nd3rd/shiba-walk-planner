import argparse
from datetime import datetime, timedelta

from src.config import load_config
from src.weather import fetch_hourly_forecast
from src.ai_planner import generate_walk_plan
from src.notifier import send_notification


def main() -> None:
    parser = argparse.ArgumentParser(description="Shiba Walk Planner")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the plan, do not send notification",
    )
    args = parser.parse_args()

    config = load_config()

    # Decide target date: evening run (>=18:00) plans for tomorrow, otherwise today
    now = datetime.now()
    if now.hour >= 18:
        target_date = (now + timedelta(days=1)).date()
        label = "明天"
    else:
        target_date = now.date()
        label = "今天"

    target_dt = datetime.combine(target_date, datetime.min.time())

    print(f"Fetching weather for {config.location.city}...\n")

    forecast = fetch_hourly_forecast(
        lat=config.location.lat,
        lon=config.location.lon,
        forecast_days=2,
    )

    print(f"Generating walk plan for {config.dog.name} "
          f"({label} {target_date.strftime('%m月%d日')})...\n")

    plan = generate_walk_plan(config, forecast, target_dt, label)
    print(plan)

    if args.dry_run:
        print("\n[dry-run] Skipping notification.")
        return

    if config.notifications.line_channel_access_token:
        print("\nSending notification via LINE...")
        send_notification(config.notifications, plan)
        print("Sent!")
    else:
        print("\n[skip] LINE credentials not configured, skipping notification.")


if __name__ == "__main__":
    main()
