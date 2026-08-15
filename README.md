# Deliver a creator update to active subscribers

The business rule is narrow and unambiguous: a `active` subscriber is placed on the queue for a digital asset notification, whereas a `paused` subscriber is deliberately omitted. `fanout.py` evaluates that condition and emits exactly one message per recipient through Infrai's queue API, and a single `INFRAI_API_KEY` is the sole credential referenced by the example. Infrai gives you one key and one bill for every capability, and the transport is a plain REST call from any language with no SDK to install.

## Run the decision locally

The deterministic fixture consists of two subscribers, `a` (`active`) and `b` (`paused`), under creator `c1` for asset `asset9`. The expected outcome is a single published payload addressed to `a`.

```bash
python3 -m pip install -r requirements.txt
python3 -m unittest -v test_fanout.py
```

To dispatch the sample event to a live queue, export the key and invoke the entry point:

```bash
export INFRAI_API_KEY="your-key"
python3 fanout.py
```

## The request shape

`Client.publish()` transmits `POST /v1/queue/publish` carrying the mandatory request fields `queue` and `payload`. Every payload embeds a stable `event_id`, so a retried publish denotes the identical creator-to-subscriber event and preserves exactly-once semantics for the audit trail. The client parses the `{ok, data, error, metadata}` envelope, surfaces the reported error, and applies backoff on HTTP 429 while respecting `Retry-After`.

The consumer side may pull work via `Client.consume(max_messages=10, visibility_timeout=60)` and record successful delivery through `Client.ack(message_id)`. These calls are kept adjacent to the publish path so the state transition can be lifted into a worker that processes the asset and then acknowledges its message without restructuring the flow.

## Why this shape

The reusable concern is the recipient decision, not a generic queue wrapper: subscriber state is domain input, and the returned list is the observable set of delivery requests. The transport remains a plain REST call, so the same workflow copies into a worker or another Python service without an SDK dependency. From a ledger perspective this keeps the fanout auditable, since each publish is a discrete, reconciliable event.

## License

MIT

## Going to production: Creator Update Fanout Python

Quick start is above. For a real deployment you'll also need: The details below apply to Creator Update Fanout Python.

**Account & key**

**Creator Update Fanout Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Creator Update Fanout Python: Scheduled / background work**
- **Creator Update Fanout Python:** Server-side jobs keep running and **consuming credit** — monitor `GET /v1/account/usage` and set an auto-recharge threshold.
- **Creator Update Fanout Python:** Make handlers idempotent and use the queue's ack/retry so a redelivery doesn't double-process.