from __future__ import annotations

import argparse
import json
import os
import time
from datetime import datetime, timezone
from typing import Any

import websocket

CONTRACT = "GOLD_CONTROL_TWELVE_XAU_WS_PREFLIGHT_V145"
WS_URL = "wss://ws.twelvedata.com/v1/quotes/price?apikey={apikey}"
SYMBOL = "XAU/USD"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _result(status: str, **kwargs: Any) -> dict[str, Any]:
    return {"contract": CONTRACT, "checked_at": _now(), "symbol": SYMBOL, "status": status, **kwargs}


def probe(timeout_seconds: float = 20.0) -> dict[str, Any]:
    api_key = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not api_key:
        return _result("BLOCKED", blocker="TWELVE_DATA_API_KEY_NOT_CONFIGURED")

    ws = None
    events: list[dict[str, Any]] = []
    try:
        ws = websocket.create_connection(
            WS_URL.format(apikey=api_key),
            timeout=min(8.0, timeout_seconds),
            origin="https://twelvedata.com",
        )
        ws.send(json.dumps({"action": "subscribe", "params": {"symbols": SYMBOL}}))
        deadline = time.monotonic() + timeout_seconds
        while time.monotonic() < deadline:
            try:
                raw = ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            if not raw:
                continue
            try:
                event = json.loads(raw)
            except Exception:
                events.append({"unparsed": str(raw)[:300]})
                continue
            events.append(event)

            event_type = str(event.get("event") or event.get("type") or "").lower()
            symbol = str(event.get("symbol") or "")
            if event_type in {"price", "quote"} and symbol == SYMBOL:
                price = event.get("price")
                timestamp = event.get("timestamp")
                try:
                    price_num = float(price)
                except Exception:
                    price_num = float("nan")
                if price_num > 0 and timestamp is not None:
                    return _result(
                        "PROVEN",
                        source="Twelve Data WebSocket",
                        endpoint="wss://ws.twelvedata.com/v1/quotes/price",
                        price=price_num,
                        provider_event_timestamp=timestamp,
                        receive_timestamp=_now(),
                        event_sample={k: event.get(k) for k in ("event", "symbol", "timestamp", "price") if k in event},
                        observed_event_count=len(events),
                    )

            if event_type in {"error", "subscribe-status", "status"}:
                text = json.dumps(event, default=str).lower()
                if any(token in text for token in ("not authorized", "permission", "upgrade", "not available", "failed")):
                    return _result(
                        "BLOCKED",
                        blocker="TWELVE_DATA_WS_ENTITLEMENT_OR_SUBSCRIPTION_REJECTED",
                        provider_event=event,
                        observed_event_count=len(events),
                    )

        return _result(
            "NOT_PROVEN",
            blocker="NO_VALID_XAU_USD_PRICE_EVENT_WITHIN_PROBE_WINDOW",
            observed_event_count=len(events),
            event_samples=events[-5:],
        )
    except Exception as exc:
        return _result("BLOCKED", blocker="TWELVE_DATA_WS_CONNECTION_OR_PROTOCOL_ERROR", error=f"{type(exc).__name__}:{exc}")
    finally:
        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeout-seconds", type=float, default=20.0)
    parser.add_argument("--out", default="twelve_xau_ws_preflight_v145.json")
    args = parser.parse_args()
    result = probe(args.timeout_seconds)
    with open(args.out, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2, ensure_ascii=False, default=str)
        handle.write("\n")
    print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
    # This is an entitlement/readiness probe. A blocked source is a valid audit
    # outcome and must not be confused with a code failure.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
