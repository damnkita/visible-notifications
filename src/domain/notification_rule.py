from dataclasses import dataclass
from datetime import timedelta
from enum import Enum, auto
from typing import Any


class PropertyOperator(Enum):
    EQ = auto()
    IN = auto()
    NIN = auto()
    LT = auto()
    GT = auto()
    LTE = auto()
    GTE = auto()


@dataclass
class PropertyMatch:
    property_xpath: str
    value: Any
    operator: PropertyOperator


@dataclass
class EventProximity:
    event_type: str
    time_proximity: timedelta | None

    """
    Notification N is only sent upon an event A but only if event A is close enough to event B, AND event B meets following conditions...
    Unconditional match is also possible if events_conditions list is empty.
    """
    event_conditions: list[EventCondition]


class LogicOperator(Enum):
    AND = auto()
    NOT = auto()
    OR = auto()


@dataclass
class EventLogic:
    logic: LogicOperator
    event_conditions: list[EventCondition]


@dataclass
class EventCondition:
    property_match: PropertyMatch | None
    event_proximity: EventProximity | None
    event_logic: EventLogic | None


@dataclass
class NotificationRule:
    # the code of an email/sms/pidgeon to send
    notification_type: str

    # the event that has triggered this rule
    event_type: str

    # events with conditions to meet in order to send the notification
    event_conditions: list[EventCondition]

    # to postpone the notification a little
    delay: timedelta | None

    # whether to check event conditions again after a delay
    recheck: bool = False

    """
    Debounce limit: send not more than N messages
    Debounce period: send not more than N messages within this period, None = ever
    Debounce calendar day: ONLY IF the debounce period is 1 day, this parameter controls if a calendar day
        is meant or just 86400 seconds
    """
    debounce_period: timedelta | None = None
    debounce_limit: int | None = None
    debounce_calendar_day: bool = False
