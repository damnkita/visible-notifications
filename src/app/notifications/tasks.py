from infrastructure.taskiq import broker


@broker.task
async def send_notification(user_id: str, notification_type: str, payload: dict) -> None:
    # TODO: Implement actual notification sending logic
    print(f"Sending {notification_type} notification to {user_id}: {payload}")
