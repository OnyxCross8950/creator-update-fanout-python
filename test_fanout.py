import unittest

from fanout import active_subscribers, publish_creator_update


class FakeClient:
    def __init__(self) -> None:
        self.payloads = []

    def publish(self, payload):
        self.payloads.append(payload)
        return {"accepted": True}


class FanoutDecisionTest(unittest.TestCase):
    def test_paused_subscriber_gets_no_delivery_message(self):
        subscribers = [
            {"subscriber_id": "a", "status": "active"},
            {"subscriber_id": "b", "status": "paused"},
        ]
        client = FakeClient()
        result = publish_creator_update(client, "c1", "asset9", subscribers)
        self.assertEqual(len(result), 1)
        self.assertEqual([item["subscriber_id"] for item in client.payloads], ["a"])
        self.assertEqual(active_subscribers(subscribers), [subscribers[0]])


if __name__ == "__main__":
    unittest.main()
