from enum import Enum


class NotificationChannel(str, Enum):
    SMS = "sms"
    EMAIL = "email"
    PIDGEON = "pidgeon"


class Notification:
    type: str
    private: bool
    channel: NotificationChannel
    text: str
