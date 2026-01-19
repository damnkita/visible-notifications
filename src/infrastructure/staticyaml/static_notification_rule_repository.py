from datetime import timedelta
from pathlib import Path

import yaml
from pytimeparse2 import parse

from domain import NotificationRule
from domain.notification_rule import (
    EventCondition,
    EventProximity,
    PropertyMatch,
    PropertyOperator,
)


class StaticNotificationRuleRepository:
    def __init__(self) -> None:
        self._rules: list[NotificationRule] = []
        self._load_rules()

    def _load_rules(self) -> None:
        yaml_path = Path(__file__).parent / "../../notification_rules.yml"

        if not yaml_path.exists():
            raise FileNotFoundError(
                f"notification_rules.yml not found at {yaml_path.absolute()}"
            )

        try:
            with open(yaml_path) as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise RuntimeError(f"Failed to parse notification_rules.yml: {e}") from e

        if not data or "rules" not in data:
            raise ValueError("notification_rules.yml must contain a 'rules' list")

        rules_data = data["rules"]
        if not isinstance(rules_data, list):
            raise ValueError("'rules' in notification_rules.yml must be a list")

        for idx, item in enumerate(rules_data):
            try:
                rule = self._parse_rule(item)
                self._rules.append(rule)
            except (KeyError, ValueError, TypeError) as e:
                raise ValueError(
                    f"Invalid rule at index {idx} in notification_rules.yml: {e}"
                ) from e

    def _parse_rule(self, data: dict) -> NotificationRule:
        # Parse event_conditions
        event_conditions = []
        conditions_data = data.get("event_conditions", [])

        for condition_data in conditions_data:
            condition = self._parse_event_condition(condition_data)
            event_conditions.append(condition)

        # Parse delay
        delay = None
        if data.get("delay_seconds"):
            delay = timedelta(seconds=data["delay_seconds"])

        # Parse debounce_period
        debounce_period = None
        if data.get("debounce_period_seconds"):
            debounce_period = timedelta(seconds=data["debounce_period_seconds"])

        return NotificationRule(
            notification_type=data["notification_type"],
            event_type=data["event_type"],
            event_conditions=event_conditions,
            delay=delay,
            recheck=data.get("recheck", False),
            debounce_period=debounce_period,
            debounce_limit=data.get("debounce_limit"),
            debounce_calendar_day=data.get("debounce_calendar_day", False),
        )

    def _parse_event_condition(self, data: dict) -> EventCondition:
        property_match = None
        event_proximity = None
        event_logic = None

        # Parse property_match
        if data.get("property_match"):
            pm_data = data["property_match"]
            property_match = PropertyMatch(
                property_xpath=pm_data["property_xpath"],
                value=pm_data["value"],
                operator=PropertyOperator[pm_data["operator"].upper()],
            )

        # Parse event_proximity
        if data.get("event_proximity"):
            ep_data = data["event_proximity"]
            time_prox = ep_data.get("time_proximity")

            # Parse time_proximity (can be "1d", "24h", or seconds)
            time_proximity_td = None
            if time_prox:
                if isinstance(time_prox, (int, float)):
                    time_proximity_td = timedelta(seconds=time_prox)
                elif isinstance(time_prox, str):
                    seconds = parse(time_prox)
                    if seconds is None:
                        raise ValueError(f"Invalid time format: {time_prox}")
                    assert isinstance(seconds, int)
                    time_proximity_td = timedelta(seconds=seconds)

            event_proximity = EventProximity(
                event_type=ep_data["event_type"],
                time_proximity=time_proximity_td,
                event_conditions=ep_data.get("event_conditions", []),
            )

        # Parse event_logic (not implemented yet, placeholder)
        if data.get("event_logic"):
            # TODO: Implement event_logic parsing when needed
            pass

        return EventCondition(
            property_match=property_match,
            event_proximity=event_proximity,
            event_logic=event_logic,
        )

    async def get_all(self) -> list[NotificationRule]:
        return self._rules.copy()

    async def get_by_event_type(self, event_type: str) -> list[NotificationRule]:
        return [rule for rule in self._rules if rule.event_type == event_type]
