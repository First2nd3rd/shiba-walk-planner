from __future__ import annotations

import json
from datetime import datetime

import anthropic

from src.config import AppConfig, WalkSession
from src.weather import HourlyWeather

SYSTEM_PROMPT = """\
你是一个遛狗计划助手。你的任务是根据逐小时天气预报数据，为用户规划最佳的遛狗时间。

## 你的工作方式
1. 分析用户提供的逐小时天气数据（降水量、温度、风速）
2. 结合用户的遛狗习惯（每天几次、偏好时段、每次时长）
3. 给出具体的遛狗时间推荐

## 推荐策略
- 优先在用户偏好时段内找无雨窗口
- 如果偏好时段都有雨，找雨最小的时段，并提醒带伞
- 如果全天大雨，可以建议减少遛狗次数，每次适当延长
- 考虑温度和风速：高温(>35°C)避开正午，提醒带水注意地面烫脚；低温(<0°C)建议缩短时间；大风(>40km/h)提醒注意安全
- 柴犬有双层毛，耐寒但怕热，夏天尤其注意

## 输出要求
- 语气友好亲切，像朋友提醒一样，不要太正式
- 简洁，2-5句话，直接给出建议
- 一定要给出具体的时间点
- 如果需要带装备（伞、雨衣、水）一定要提醒
- 用用户设定的语言回复
"""


def _format_weather_data(
    forecast: list[HourlyWeather], target_date: datetime
) -> str:
    day_hours = [h for h in forecast if h.time.date() == target_date.date()]
    if not day_hours:
        return "无天气数据"

    lines = ["时间 | 降水(mm) | 温度(°C) | 风速(km/h) | 雨况"]
    lines.append("----|---------|---------|-----------|----")
    for h in day_hours:
        lines.append(
            f"{h.time.strftime('%H:%M')} | {h.precipitation_mm:.1f} | "
            f"{h.temperature_c:.1f} | {h.wind_speed_kmh:.1f} | {h.rain_level}"
        )
    return "\n".join(lines)


def _format_walk_habits(walks: list[WalkSession]) -> str:
    lines = [f"每天遛{len(walks)}次:"]
    for w in walks:
        lines.append(
            f"- {w.name}: 偏好{w.preferred_time}出门, "
            f"可接受范围{w.time_range[0]}-{w.time_range[1]}, "
            f"通常遛{w.duration_min}分钟"
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
## 基本信息
- 狗狗: {config.dog.name} ({config.dog.breed})
- 地点: {config.location.city}
- 日期: {target_date.strftime('%Y年%m月%d日')}
- 语言: {config.language}

## 遛狗习惯
{walk_habits}

## 逐小时天气预报
{weather_table}

请根据以上信息，给出明天的遛狗计划建议。"""

    client = anthropic.Anthropic()
    message = client.messages.create(
        model="claude-sonnet-4-5-20250514",
        max_tokens=512,
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    return message.content[0].text
