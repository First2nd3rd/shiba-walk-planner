# Shiba Walk Planner - Design Outline

## Problem Statement

柴犬每天都要遛，不管天气如何。女朋友不喜欢自己查天气。需要一个工具：
- 分析次日/当天的**逐小时天气预报**
- 找出**最适合遛狗的时间窗口**（雨停的时段 > 雨小的时段）
- **提前一天晚上**或**当天早上**推送遛狗计划

## Core Logic: Walk Window Optimizer

```
输入: 逐小时天气预报 (24h)
输出: 推荐的遛狗时间段 (1-2个窗口, 每个30-60min)

算法:
1. 获取未来24小时逐小时降水量 + 降水概率
2. 找出所有"无雨窗口" (降水量 = 0, 连续 >= 30min)
   -> 如果有: 推荐最佳窗口 (优先早晚合适时段)
3. 如果全天都有雨: 找"雨最小窗口" (降水量最低的连续时段)
   -> 推荐该时段 + 提醒带伞/穿雨衣
4. 附加因素: 温度极端(>35°C/<-5°C), 大风, 雷暴 -> 调整建议
```

## Example Scenarios

| 天气情况 | 推送内容 |
|---------|---------|
| 明天下午2-5点有雨，其他时间晴 | "明天上午10点前或傍晚6点后遛狗最好，下午2-5点有雨避开" |
| 明天全天断续小雨 | "明天雨断断续续，早上8-9点和下午3-4点雨最小(0.5mm/h)，建议这两个时段出门，带伞" |
| 明天暴雨一整天 | "明天暴雨，下午4点雨势最弱(2mm/h)，速战速决，给狗穿雨衣" |
| 明天晴天35°C | "明天大晴天但很热！早上7点前或晚上7点后遛，避开正午，带水，注意地面烫脚" |
| 明天晴天15°C | "明天天气很好！随时可以遛~" |

## Architecture

```
[Cron: 前一天20:00 + 当天07:00]
        |
        v
[Weather API] -- 获取逐小时预报(24h)
        |
        v
[Walk Window Optimizer] -- 分析降水/温度/风力，找最佳时段
        |
        v
[Claude API] -- 生成自然语言消息 (友好、简洁、可执行)
        |
        v
[WeChat] -- 推送给女朋友
```

## Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Language | Python 3.11+ | 简单，生态好 |
| Weather API | OpenWeatherMap One Call 3.0 | 逐小时预报，免费1000次/天 |
| AI | Claude API | 生成友好的中文消息 |
| Messaging | WeChat (企业微信/服务号) | 女朋友日常使用，推送自然 |
| Scheduler | cron / GitHub Actions | 每天2次触发 |

## Project Structure

```
shiba-walk-planner/
  .env.example          # API keys template
  config.yaml           # 地点、时间、狗名、语言等配置
  requirements.txt
  src/
    main.py             # 入口
    weather.py          # 天气API + 逐小时数据解析
    optimizer.py        # 核心: 遛狗时间窗口分析算法
    ai_message.py       # Claude API 生成消息
    notifier.py         # 消息推送 (WeChat)
    config.py           # 配置加载
  tests/
```

## optimizer.py - Core Algorithm Sketch

```python
def find_walk_windows(hourly_forecast: list[HourlyWeather]) -> WalkPlan:
    """
    分析逐小时天气，返回推荐遛狗窗口

    优先级:
    1. 无雨时段 (precip = 0)，优先选早晚适合遛狗的时间
    2. 小雨时段 (precip < 1mm/h)
    3. 雨最小时段 (precip最低的连续1h)

    过滤条件:
    - 避开极端温度 (>35°C, <-5°C 降低优先级)
    - 避开雷暴时段
    - 避开大风 (>50km/h)
    - 窗口最短30min
    """
```

## Config Example

```yaml
dog:
  name: "Hihi"
  breed: "Shiba Inu"

location:
  city: "東京都中央区晴海"
  lat: 35.6605
  lon: 139.7868

schedule:
  evening_reminder: "20:00"   # 前一天晚上推送明天计划
  morning_reminder: "07:00"   # 当天早上推送当天计划
  timezone: "Asia/Tokyo"

preferences:
  walk_earliest: "06:00"      # 最早可接受遛狗时间
  walk_latest: "22:00"        # 最晚可接受遛狗时间
  walk_duration_min: 30       # 最短遛狗时长(分钟)
  preferred_times: ["08:00", "18:00"]  # 偏好时段

language: "zh"

notifications:
  platform: "wechat"
```

## MVP Scope

1. OpenWeatherMap 逐小时天气获取
2. Walk window optimizer 核心算法
3. Claude API 生成中文消息
4. WeChat 推送 (企业微信应用 或 服务号模板消息)
5. Cron 每天2次 (晚8点 + 早7点)
