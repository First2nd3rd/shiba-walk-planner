from __future__ import annotations

from linebot.v3.messaging import (
    ApiClient,
    BroadcastRequest,
    Configuration,
    MessagingApi,
    TextMessage,
)

from src.config import NotificationsConfig


def send_line_message(config: NotificationsConfig, message: str) -> None:
    """Broadcast a text message to all LINE friends."""
    if not config.line_channel_access_token:
        raise ValueError(
            "LINE credentials missing. Set LINE_CHANNEL_ACCESS_TOKEN in .env or config.yaml."
        )

    configuration = Configuration(access_token=config.line_channel_access_token)
    with ApiClient(configuration) as client:
        api = MessagingApi(client)
        api.broadcast(
            BroadcastRequest(
                messages=[TextMessage(text=message)],
            )
        )


def send_notification(config: NotificationsConfig, message: str) -> None:
    """Dispatch notification based on configured platform."""
    if config.platform == "line":
        send_line_message(config, message)
    else:
        raise ValueError(f"Unsupported notification platform: {config.platform}")
