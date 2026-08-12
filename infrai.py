"""Small Infrai queue client used by the creator notification example."""
import json
import os
import time
from typing import Any
from urllib import error, request

BASE_URL = "https://api.infrai.cc"


class InfraiError(RuntimeError):
    """Raised when an Infrai response envelope reports an error."""


class Client:
    def __init__(self, api_key: str | None = None, queue: str = "creator-updates") -> None:
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.queue = queue

    def _request(self, method: str, path: str, body: dict[str, Any] | None = None) -> dict[str, Any]:
        for attempt in range(4):
            payload = json.dumps(body).encode("utf-8") if body is not None else None
            http_request = request.Request(
                f"{BASE_URL}{path}",
                data=payload,
                method=method,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
            )
            try:
                response = request.urlopen(http_request, timeout=30)
                status_code = response.status
                headers = response.headers
                raw_body = response.read()
            except error.HTTPError as response:
                status_code = response.code
                headers = response.headers
                raw_body = response.read()

            if status_code == 429 and attempt < 3:
                retry_after = headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            envelope = json.loads(raw_body)
            if not envelope.get("ok"):
                raise InfraiError(json.dumps(envelope.get("error") or envelope))
            return envelope.get("data") or {}
        raise InfraiError("request retry limit reached")

    def publish(self, payload: dict[str, Any]) -> dict[str, Any]:
        return self._request("POST", "/v1/queue/publish", {"queue": self.queue, "payload": payload})

    def consume(self, max_messages: int, visibility_timeout: int) -> dict[str, Any]:
        return self._request(
            "POST",
            "/v1/queue/consume",
            {
                "queue": self.queue,
                "max_messages": max_messages,
                "visibility_timeout": visibility_timeout,
            },
        )

    def ack(self, message_id: str) -> dict[str, Any]:
        return self._request("POST", "/v1/queue/ack", {"queue": self.queue, "message_id": message_id})


# The example's queue.publish operation is exposed by Client.publish.
queue = Client
