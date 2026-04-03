import argparse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.config import load_config
from src.weather import fetch_hourly_forecast, summarize_weather, weather_changed
from src.ai_planner import generate_walk_plan
from src.notifier import send_notification
from src.cache import save_summary, load_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Shiba Walk Planner")
    parser.add_argument(
        "--mode",
        choices=["evening", "morning"],
        default="evening",
        help="evening: plan for tomorrow; morning: check for weather changes",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only print the plan, do not send notification",
    )
    args = parser.parse_args()

    config = load_config()
    tz = ZoneInfo(config.timezone)
    now = datetime.now(tz)

    forecast = fetch_hourly_forecast(
        lat=config.location.lat,
        lon=config.location.lon,
        forecast_days=2,
    )

    if args.mode == "evening":
        target_date = (now + timedelta(days=1)).date()
        label = "明天"
        target_dt = datetime.combine(target_date, datetime.min.time())

        print(f"[evening] Generating walk plan for {config.dog.name} "
              f"({label} {target_date.strftime('%m月%d日')})...\n")

        plan = generate_walk_plan(config, forecast, target_dt, label)
        print(plan)

        # Save weather summary for morning comparison
        summary = summarize_weather(forecast, target_dt)
        save_summary(summary)
        print("\n[evening] Weather summary saved for morning comparison.")

    else:  # morning
        target_date = now.date()
        label = "今天"
        target_dt = datetime.combine(target_date, datetime.min.time())

        new_summary = summarize_weather(forecast, target_dt)
        old_summary = load_summary()

        if old_summary and not weather_changed(old_summary, new_summary):
            plan = (
                f"🐕 {config.dog.name} — {label}天气和昨晚预报一致，"
                f"按昨晚的计划走就好！"
            )
            print(f"[morning] No significant weather change.\n\n{plan}")
        else:
            reason = "weather changed" if old_summary else "no evening data"
            print(f"[morning] Regenerating plan ({reason})...\n")
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
