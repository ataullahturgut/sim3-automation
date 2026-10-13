#!/usr/bin/env python3
"""R80 strict-asof XAU/USD observation -> event-state -> SHADOW-only decision stream.
NO live data adapter connected. NO bank trade commands. NO model alpha claimed.
Input: JSONL objects: {"kind":"spot"|"bank"|"monthly", "event_at":UTC ISO,
"received_at":UTC ISO, ...}. Write a JSON status per SPOT event.
Usage: python gold_axis_2026/tools/gold_r80_paper_live_watch.py --input events.jsonl
"""
from __future__ import annotations
import argparse
import collections
import datetime as dt
import json
import math
import sys
from zoneinfo import ZoneInfo

TR = ZoneInfo("Europe/Istanbul")
MAX_FEED_LAG_SECONDS = 90
MAX_BANK_LAG_SECONDS = 90
MAX_SPREAD_BP = 25.0  # provisional safety veto, NOT empirical bank spread
ONSET_LOG_ABS = 0.0075
LABEL_HORIZON_MINUTES = 120


def timestamp(value):
    try:
        t = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (TypeError, ValueError, AttributeError) as e:
        raise ValueError("invalid offset-aware timestamp") from e
    if t.tzinfo is None or t.utcoffset() is None:
        raise ValueError("timestamp must have explicit UTC offset")
    return t.astimezone(dt.timezone.utc)


def parse(event):
    kind = event.get("kind")
    if kind not in {"spot", "bank", "monthly"}:
        raise ValueError("unsupported event kind")
    t = timestamp(event["event_at"])
    r = timestamp(event["received_at"])
    if r < t:
        raise ValueError("received_at before event_at")
    out = dict(event, kind=kind, _ts=t, _recv=r)
    if kind == "spot":
        if event.get("instrument") != "XAUUSD" or event.get("provider") is None:
            raise ValueError("spot instrument/provider required")
        a, b = float(event["ask"]), float(event["bid"])
        if not (math.isfinite(a) and math.isfinite(b) and 0 < b <= a):
            raise ValueError("invalid spot bid/ask")
        out["_mid"] = (a + b) / 2
        out["_spread_bp"] = 10000 * (a - b) / out["_mid"]
    if kind == "bank":
        if event.get("instrument") != "XAUUSD":
            raise ValueError("bank and spot instrument must match (no gram/currency conversions)")
        a, b = float(event["ask"]), float(event["bid"])
        if not (math.isfinite(a) and math.isfinite(b) and 0 < b <= a):
            raise ValueError("invalid bank bid/ask")
        out["_spread_bp"] = 10000 * (a - b) / ((a + b) / 2)
    if kind == "monthly":
        if event.get("evidence_class") != "PROSPECTIVE_APPROVED":
            # Preserve replay rows for audit, never treat reconstructed direction as usable.
            out["_approved"] = False
        else:
            out["_approved"] = True
        if event.get("direction") not in ("UP", "DOWN"):
            raise ValueError("monthly direction must be UP/DOWN")
        if not isinstance(event.get("target_month"), str):
            raise ValueError("monthly target_month required (YYYY-MM)")
    return out


def iso(t):
    return t.isoformat().replace("+00:00", "Z")


class ShadowEngine:
    def __init__(self):
        self.last_receipt = None
        self.bars = collections.deque(maxlen=48)
        self.bank = None
        self.monthly = None
        self.onset = None
        self.pending = []
        self.matured = []
        self.snapshots = []

    def accept(self, raw):
        e = parse(raw)
        t, now = e["_ts"], e["_recv"]
        if self.last_receipt and now < self.last_receipt:
            raise ValueError("input stream not in receive-time order")
        self.last_receipt = now
        if e["kind"] == "monthly":
            self.monthly = e
            return None
        if e["kind"] == "bank":
            self.bank = e
            return None

        # At first arrival of any current spot bar, process only previously matured labels.
        if (now-t).total_seconds() <= MAX_FEED_LAG_SECONDS:
            self._mature(now, t, e["_mid"])
        if self.bars and t <= self.bars[-1][0]:
            raise ValueError("non-increasing spot quote event time")
        feed_delay = (now - t).total_seconds()
        if feed_delay <= MAX_FEED_LAG_SECONDS:
            self.bars.append((t, e["_mid"]))

        local = now.astimezone(TR)
        in_session = local.weekday() < 5 and dt.time(9, 0) <= local.time() <= dt.time(16, 30)
        source_ok = feed_delay <= MAX_FEED_LAG_SECONDS
        bank_ok = (
            self.bank is not None and self.bank["_recv"] <= now and
            0 <= (now-self.bank["_recv"]).total_seconds() <= MAX_BANK_LAG_SECONDS and
            self.bank["_spread_bp"] <= MAX_SPREAD_BP
        )
        month_ok = (
            self.monthly is not None and self.monthly["_approved"] and
            self.monthly["_recv"] <= now and self.monthly["target_month"] == local.strftime("%Y-%m")
        )

        recent = [(tt, p) for tt, p in self.bars
                  if 0 <= (t-tt).total_seconds() <= 90*60]
        lookback = [(tt, p) for tt, p in recent
                    if 45*60 <= (t-tt).total_seconds() <= 75*60]
        move = math.log(e["_mid"]/lookback[-1][1]) if lookback and len(recent) >= 5 else None
        # Observed at receive time, NOT a future-prediction or a 15m intra-bar high.
        if source_ok and in_session and move is not None:
            new_sign = "UP" if move >= ONSET_LOG_ABS else (
                "DOWN" if move <= -ONSET_LOG_ABS else None)
            if new_sign and (self.onset is None or self.onset["sign"] != new_sign):
                self.onset = {"sign":new_sign, "at":t, "received_at":now,
                              "reference_mid":e["_mid"], "onset_logret":move}
                self.pending.append({"origin":t, "due":t+dt.timedelta(minutes=LABEL_HORIZON_MINUTES),
                                     "reference_mid":e["_mid"], "sign":new_sign})
            elif move is not None and abs(move) <= ONSET_LOG_ABS/3:
                self.onset = None

        if self.onset and t-self.onset["at"]>dt.timedelta(hours=2):
            self.onset = None

        candidate = "SAT" if month_ok and self.monthly["direction"] == "UP" and self.onset and self.onset["sign"] == "DOWN" else (
            "AL" if month_ok and self.monthly["direction"] == "DOWN" and self.onset and self.onset["sign"] == "UP" else None)
        reasons = []
        if not source_ok: reasons.append("STALE_SPOT_SOURCE")
        if not in_session: reasons.append("OUTSIDE_BANK_DECISION_SESSION")
        if not bank_ok: reasons.append("BANK_QUOTE_OR_SPREAD_NOT_VERIFIED")
        if not month_ok: reasons.append("MONTHLY_ISSUE_VINTAGE_UNVERIFIED")
        if self.onset is None: reasons.append("NO_CONFIRMED_ONSET")
        reasons.append("NO_PROSPECTIVELY_VALIDATED_CONDITIONAL_ALPHA")
        result = {
            "decision_at":iso(now), "spot_event_at":iso(t), "provider":e["provider"],
            "mid_usd_oz":round(e["_mid"],4),
            "spot_spread_bp":round(e["_spread_bp"],2),
            "source_delay_s":round(feed_delay,1),
            "observed_onset":self.onset["sign"] if self.onset else "NONE",
            "observed_last_hour_logret_pct":round(100*move,3) if move is not None else None,
            "candidate_if_model_validated":candidate,
            "monthly_state_verified":self.monthly["direction"] if month_ok else None,
            "bank_spread_bp":round(self.bank["_spread_bp"],2) if bank_ok else None,
            "recommendation":"BEKLE",
            "mode":"SHADOW_NO_TRADE",
            "reason_codes":reasons, "matured_outcomes":len(self.matured)}
        self.snapshots.append(result)
        return result

    def _mature(self, now, t, observed_mid):
        for x in list(self.pending):
            # STRICT: do not assign label earlier than requested horizon.
            # First quote at/after horizon is an approximation; future live label contract
            # must enforce exact quote and max sample delay as G2 before model training.
            if t >= x["due"] and now >= x["due"]:
                if t-x["due"] <= dt.timedelta(minutes=15):
                    outcome = int((1 if x["sign"]=="UP" else -1) *
                                  math.log(observed_mid/x["reference_mid"]) > 0)
                    self.matured.append({"origin":iso(x["origin"]), "due":iso(x["due"]),
                                         "observed_label_at":iso(t), "continuation":outcome})
                self.pending.remove(x)


def run(events):
    engine = ShadowEngine()
    for event in events:
        r = engine.accept(event)
        if r is not None:
            yield r


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="event JSONL path, or - for stdin")
    args = parser.parse_args()
    def events():
        if args.input == "-":
            for line in sys.stdin:
                if line.strip(): yield json.loads(line)
        else:
            with open(args.input, encoding="utf8") as f:
                for line in f:
                    if line.strip(): yield json.loads(line)
    for output in run(events()):
        print(json.dumps(output, ensure_ascii=False, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
