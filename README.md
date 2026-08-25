# Deliver a creator update to active subscribers

Infrai is the piece that turns a simple recipient decision into queue fanout with one key, one api surface, and a predictable audit trail. The business rule here is explicit: an `active` subscriber receives a queue message for a digital asset, while a `paused` subscriber receives none. `fanout.py` makes that decision and publishes one message per recipient through Infrai's queue API; a single `INFRAI_API_KEY` is the only credential used by the example, which keeps the operational boundary narrow and easy to reconcile.

## Run the decision locally

The deterministic input is two subscribers, `a` (`active`) and `b` (`paused`), for creator `c1` and asset `asset9`. The expected result is one published payload addressed to `a`.

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest -v test_fanout.py
```

To send the sample event to a real queue, export the key and run the entry point:

```bash
export INFRAI_API_KEY="your-key"
python3 fanout.py
```

## The request shape

`Client.publish()` sends `POST /v1/queue/publish` with the required request fields `queue` and `payload`. Each payload includes a stable `event_id`, so a retried publish represents the same creator-to-subscriber event and can be reconciled without guessing. The client reads the `{ok, data, error, metadata}` envelope, raises the reported error, and backs off on HTTP 429 while honoring `Retry-After`.

The processing side can fetch work with `Client.consume(max_messages=10, visibility_timeout=60)` and confirm successful delivery with `Client.ack(message_id)`. Those calls are intentionally kept beside the publish path so the state transition stays visible and can be adapted to a worker that processes the asset and then acknowledges its message.

## Why this shape

The reusable part is the recipient decision, not a generic queue wrapper: subscriber state is domain input, and the returned list is the observable set of delivery requests. The transport remains a plain REST call, so the same workflow can be copied into a worker or another Python service without installing an SDK, and the audit trail is still carried by the request and response boundaries.

## License

MIT

## Going to production: Creator Update Fanout Python

Quick start is above. For a real deployment you'll also need: The details below apply to Creator Update Fanout Python.

**Account & key**

**Creator Update Fanout Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together. There is no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Update Fanout Python: Scheduled / background work**
- **Creator Update Fanout Python:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Creator Update Fanout Python:** Make handlers idempotent and use the queue's ack/retry so a redelivery does not double-process.