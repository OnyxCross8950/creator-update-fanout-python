"""Fan out one creator update as subscriber-specific queue messages."""
from typing import Any

from infrai import Client


def active_subscribers(subscribers: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [subscriber for subscriber in subscribers if subscriber.get("status") == "active"]


def publish_creator_update(
    client: Client, creator_id: str, asset_id: str, subscribers: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Publish one stable event per active subscriber and return queue responses."""
    results = []
    for subscriber in active_subscribers(subscribers):
        payload = {
            "event_id": f"{creator_id}:{asset_id}:{subscriber['subscriber_id']}",
            "creator_id": creator_id,
            "asset_id": asset_id,
            "subscriber_id": subscriber["subscriber_id"],
            "action": "deliver-digital-asset",
        }
        results.append(client.publish(payload))
    return results


if __name__ == "__main__":
    client = Client()
    subscribers = [
        {"subscriber_id": "fan-101", "status": "active"},
        {"subscriber_id": "fan-102", "status": "paused"},
        {"subscriber_id": "fan-103", "status": "active"},
    ]
    print(publish_creator_update(client, "creator-7", "asset-42", subscribers))
