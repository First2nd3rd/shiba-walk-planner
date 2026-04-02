from __future__ import annotations

from linebot.v3.messaging import (
    ApiClient,
    Configuration,
    MessagingApi,
    PushMessageRequest,
    TextMessage,
)

from src.config import NotificationsConfig


def send_line_message(config: NotificationsConfig, message: str) -> None:
    """Push a text message to a LINE user via Messaging API."""
    if not config.line_channel_access_token or not config.line_user_id:
        raise ValueError(
            "LINE credentials missing. Set LINE_CHANNEL_ACCESS_TOKEN and "
            "LINE_USER_ID in .env or config.yaml."
        )

    configuration = Configuration(access_token=config.line_channel_access_token)
    with ApiClient(configuration) as client:
        api = MessagingApi(client)
        api.push_message(
            PushMessageRequest(
                to=config.line_user_id,
                messages=[TextMessage(text=message)],
            )
        )


def send_notification(config: NotificationsConfig, message: str) -> None:
    """Dispatch notification based on configured platform."""
    if config.platform == "line":
        send_line_message(config, message)
    else:
        raise ValueError(f"Unsupported notification platform: {config.platform}")
