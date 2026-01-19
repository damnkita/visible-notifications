from pathlib import Path

import yaml

from domain import Notification
from domain.notification import NotificationChannel


class StaticNotificationRepository:
    def __init__(self) -> None:
        self._notifications: list[Notification] = []
        self._load_notifications()

    def _load_notifications(self) -> None:
        yaml_path = Path("./notifications.yaml")

        if not yaml_path.exists():
            raise FileNotFoundError(
                f"notifications.yaml not found at {yaml_path.absolute()}"
            )

        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse notifications.yaml: {e}") from e

        if not data or "notifications" not in data:
            raise ValueError("notifications.yaml must contain a 'notifications' list")

        notifications_data = data["notifications"]
        if not isinstance(notifications_data, list):
            raise ValueError("'notifications' in notifications.yaml must be a list")

        for idx, item in enumerate(notifications_data):
            try:
                notification = Notification()
                notification.type = item["type"]
                notification.private = item["private"]
                notification.channel = NotificationChannel(item["channel"])
                self._notifications.append(notification)
            except (KeyError, ValueError, TypeError) as e:
                raise ValueError(
                    f"Critical: Invalid notification at index {idx} in notifications.yaml: {e}"
                ) from e

    async def get_all(self) -> list[Notification]:
        return self._notifications.copy()

    async def get_by_type(self, notification_type: str) -> Notification | None:
        for notification in self._notifications:
            if notification.type == notification_type:
                return notification
        return None
