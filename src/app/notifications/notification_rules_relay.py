from glom import glom

from app.notifications.notification_intent import NotificationIntent
from app.persistence.event_repository import EventRepository
from app.persistence.notification_history_record_repository import (
    NotificationHistoryRecordRepository,
)
from domain import Event, Notification, NotificationRule
from domain.notification_rule import EventCondition, LogicOperator, PropertyOperator


class NotificationRulesRelay:
    def __init__(
        self,
        event_repo: EventRepository,
        notification_history_repo: NotificationHistoryRecordRepository,
        notification_rules: list[NotificationRule],
        notifications: list[Notification],
    ) -> None:
        self._event_repo = event_repo
        self._notification_history_repo = notification_history_repo
        self._notification_rules_triggers: dict[str, list[NotificationRule]] = {
            rule.event_type: [] for rule in notification_rules
        }

        self._notifications: dict[str, Notification] = {
            notification.type: notification for notification in notifications
        }

        for rule in notification_rules:
            self._notification_rules_triggers[rule.event_type].append(rule)

    async def route(self, event: Event) -> list[NotificationIntent]:
        if event.type not in self._notification_rules_triggers:
            return []

        rules = self._notification_rules_triggers[event.type]

        if len(rules) == 0:
            return []

        intents, debounced_intents = [], []

        # for every rule that references this event type, let's check if conditions allow sending the notification
        # (one event can trigger several notifications)
        for rule in rules:
            # delays
            if rule.delay is not None:
                raise NotImplementedError(
                    "Sorry, for now delayed notification is not supported"
                )

            # conditions check
            match = await self._check_event_against_conditions(
                event, rule.event_conditions
            )
            if not match:
                continue

            # frequency debounce
            if rule.debounce_limit is not None and rule.debounce_period is not None:
                sent_count = await self._notification_history_repo.count_by_user_and_type_within_time(
                    user_id=event.user_id,
                    notification_type=rule.notification_type,
                    timerange=rule.debounce_period,
                )

                if sent_count >= rule.debounce_limit:
                    debounced_intents.append(
                        NotificationIntent(
                            notification_type=rule.notification_type,
                            delay=rule.delay,
                            debounced_because=f"Notification {rule.notification_type} has occured {sent_count} times which is GTE than {rule.debounce_limit}",
                        )
                    )
                    continue

            intents.append(
                NotificationIntent(
                    notification_type=rule.notification_type,
                    delay=rule.delay,
                    debounced_because=None,
                )
            )

        return intents + debounced_intents

    async def _check_event_against_conditions(
        self,
        event: Event,
        conditions: list[EventCondition],
    ) -> bool:
        """
        1. Is there a notification in memory? If not, then skip
        2. Conditions, per each:
            2.1 Is there a property match? If yes and does not match, it's a skip
            2.2 Is there an event proxymity? If yes and no matching event, then skip
            2.3 Is there a logic record? If yes, and embedded rules are falsy, then skip
        """

        for condition in conditions:
            # if it's a property match
            if condition.property_match:
                if condition.property_match.operator not in (
                    PropertyOperator.EQ,
                    PropertyOperator.GTE,
                ):
                    raise NotImplementedError(
                        "Sorry, the only supported PropertyOperator for now is EQ"
                    )
                event_dict = event.to_dict()

                # EQ
                if condition.property_match.operator is PropertyOperator.EQ and str(
                    condition.property_match.value
                ) != str(glom(event_dict, condition.property_match.property_xpath)):
                    return False

                # GTE
                if condition.property_match.operator is PropertyOperator.GTE and float(
                    glom(event_dict, condition.property_match.property_xpath)
                ) < float(condition.property_match.value):
                    return False

            # if it's event proximity
            if condition.event_proximity:
                assert condition.event_proximity.time_proximity is not None
                events_within_range = await self._event_repo.find_for_user_within_time(
                    condition.event_proximity.event_type,
                    event.user_id,
                    condition.event_proximity.time_proximity,
                )

                if len(events_within_range) == 0:
                    return False

                if len(condition.event_proximity.event_conditions) != 0:
                    raise NotImplementedError(
                        "Sorry, embedded events conditions aren't supported for now"
                    )

            # if it's event logic (not a single set of conditions but a bunch of other conditions with some logic operator)
            if condition.event_logic:
                if condition.event_logic.logic is not LogicOperator.AND:
                    raise NotImplementedError(
                        "Sorry, the only supported LogicOperator for now is AND"
                    )

                results = await self._check_event_against_conditions(
                    event, condition.event_logic.event_conditions
                )

                if not results:
                    return False

        return True
