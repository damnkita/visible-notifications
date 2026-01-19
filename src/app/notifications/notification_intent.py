from dataclasses import dataclass
from datetime import timedelta


@dataclass
class NotificationIntent:
    notification_type: str
    delay: timedelta | None
    debounced_because: str | None
