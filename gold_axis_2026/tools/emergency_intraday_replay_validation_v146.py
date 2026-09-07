from __future__ import annotations

import argparse
import json
import os
import sys
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

ROOT = Path(__file__).resolve().parents[2]
R4_SRC = ROOT / "gold_axis_2026" / "r4_1" / "src"
sys.path.insert(0, str(R4_SRC))

from gold_r4.contracts import Direction, ReversalAlert  # noqa: E402
from gold_r4.emergency import EmergencyState  # noqa: E402

SYMBOL = "XAU/USD"
INTERVAL = "1min"
TIME_SERIES_URL = "https://api.twelvedata.com/time_series"
EARLIEST_URL = "https://api.twelvedata.com/earliest_timestamp"
ANCHOR_FILE = ROOT / "gold_axis_2026" / "patch_repro_v1" / "locked_replay_v6_monthly_level_43.csv"
ANCHOR_COLUMN = "patch_v6"
THRESHOLD = 0.04
PAGE_OUTPUTSIZE = 5000
MIN_REQUEST_INTERVAL_SECONDS = float(os.environ.get("TWELVE_MIN_REQUEST_INTERVAL_SECONDS", "8.5"))
_LAST_REQUEST_MONOTONIC = 0.0


@dataclass
class MonthMetrics:
    month: str
    anchor: float
    observed_minutes: int
    first_ts: str | None
    last_ts: str | None
    min_price: float | None
    max_price: float | None
    min_displacement: float | None
    max_displacement: float | None
    up_level_rows: int
    down_level_rows: int
    up_level_episodes: int
    down_level_episodes: int
    up_alert_rows: int
    down_alert_rows: int
    up_alert_episodes: int
    down_alert_episodes: int
    shock_direction_transitions: int
    cross_through_transitions: int
    cross_through_without_expected_alert: int
    gap_gt_120s_count_unclassified: int
    max_gap_seconds_unclassified: float | None
    provider_pages: int


def _api_key() -> str:
    value = os.environ.get("TWELVE_DATA_API_KEY", "").strip()
    if not value:
        raise RuntimeError("TWELVE_DATA_API_KEY is not set")
    return value


def _session() -> requests.Session:
    s = requests.Session()
    s.headers.update(
        {
            "Authorization": f"apikey {_api_key()}",
            "User-Agent": "GoldControl-Emergency-Intraday-Replay-V146/1.0",
        }
    )
    return s


def _pace_request() -> None:
    global _LAST_REQUEST_MONOTONIC
    now = time.monotonic()
    elapsed = now - _LAST_REQUEST_MONOTONIC
    if _LAST_REQUEST_MONOTONIC > 0 and elapsed < MIN_REQUEST_INTERVAL_SECONDS:
        time.sleep(MIN_REQUEST_INTERVAL_SECONDS - elapsed)
    _LAST_REQUEST_MONOTONIC = time.monotonic()


def _request_json(session: requests.Session, url: str, params: dict) -> dict:
    waits = [0, 10, 20, 30]
    last_error: Exception | None = None
    for wait in waits:
        if wait:
            time.sleep(wait)
        try:
            _pace_request()
            r = session.get(url, params=params, timeout=(8, 90))
            try:
                payload = r.json()
            except ValueError as exc:
                r.raise_for_status()
                raise RuntimeError("TWELVE_NON_JSON_RESPONSE") from exc
            if payload.get("status") == "error":
                code = payload.get("code")
                msg = payload.get("message")
                if str(code) in {"429", "500", "502", "503", "504"}:
                    last_error = RuntimeError(f"TWELVE_RETRYABLE_ERROR:{code}:{msg}")
                    continue
                raise RuntimeError(f"TWELVE_API_ERROR:{code}:{msg}")
            r.raise_for_status()
            return payload
        except (requests.RequestException, RuntimeError) as exc:
            last_error = exc
    raise RuntimeError(f"TWELVE_REQUEST_FAILED:{last_error}")


def _earliest_timestamp(session: requests.Session) -> str | None:
    payload = _request_json(session, EARLIEST_URL, {"symbol": SYMBOL, "interval": INTERVAL})
    for key in ("datetime", "timestamp", "earliest_timestamp"):
        if payload.get(key) is not None:
            return str(payload[key])
    data = payload.get("data")
    if isinstance(data, dict):
        for key in ("datetime", "timestamp", "earliest_timestamp"):
            if data.get(key) is not None:
                return str(data[key])
    return None


def _month_bounds(month: str) -> tuple[pd.Timestamp, pd.Timestamp]:
    start = pd.Timestamp(f"{month}-01", tz="UTC")
    end = (start + pd.offsets.MonthBegin(1)) - pd.Timedelta(seconds=1)
    return start, end


def _fetch_month(session: requests.Session, month: str) -> tuple[list[tuple[pd.Timestamp, float]], int]:
    """Fetch a full calendar month using deterministic backward 5000-row pages.

    Twelve documents a 5000-record request ceiling. Each request is bounded by
    the month start and a moving end_date. When a page is full, the next page
    ends one minute before the earliest returned row. Duplicate/conflicting
    minutes and non-progress are fail-closed.
    """
    start, end = _month_bounds(month)
    rows: dict[pd.Timestamp, float] = {}
    cursor_end = end
    pages = 0

    while cursor_end >= start:
        payload = _request_json(
            session,
            TIME_SERIES_URL,
            {
                "symbol": SYMBOL,
                "interval": INTERVAL,
                "start_date": start.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": cursor_end.strftime("%Y-%m-%d %H:%M:%S"),
                "outputsize": PAGE_OUTPUTSIZE,
                "timezone": "UTC",
                "format": "JSON",
            },
        )
        pages += 1
        meta = payload.get("meta") or {}
        if meta.get("symbol") not in (None, SYMBOL):
            raise RuntimeError(f"TWELVE_SYMBOL_MISMATCH:{month}:{meta.get('symbol')}")
        if meta.get("interval") not in (None, INTERVAL):
            raise RuntimeError(f"TWELVE_INTERVAL_MISMATCH:{month}:{meta.get('interval')}")

        values = payload.get("values") or []
        if not values:
            break

        page_rows: dict[pd.Timestamp, float] = {}
        for item in values:
            ts = pd.to_datetime(item.get("datetime"), utc=True, errors="coerce")
            if pd.isna(ts):
                continue
            ts = pd.Timestamp(ts).floor("min")
            if ts < start or ts > cursor_end:
                continue
            close = pd.to_numeric(item.get("close"), errors="coerce")
            if pd.isna(close) or float(close) <= 0:
                raise RuntimeError(f"TWELVE_INVALID_CLOSE:{month}:{item.get('datetime')}")
            val = float(close)
            if ts in page_rows and page_rows[ts] != val:
                raise RuntimeError(f"TWELVE_PAGE_DUPLICATE_CONFLICT:{month}:{ts.isoformat()}")
            page_rows[ts] = val

        if not page_rows:
            raise RuntimeError(f"TWELVE_PAGE_NO_VALID_ROWS:{month}:{cursor_end.isoformat()}")

        for ts, val in page_rows.items():
            if ts in rows and rows[ts] != val:
                raise RuntimeError(f"TWELVE_DUPLICATE_MINUTE_CONFLICT:{month}:{ts.isoformat()}")
            rows[ts] = val

        earliest = min(page_rows)
        if earliest <= start or len(values) < PAGE_OUTPUTSIZE:
            break
        next_end = earliest - pd.Timedelta(minutes=1)
        if next_end >= cursor_end:
            raise RuntimeError(f"TWELVE_PAGINATION_NON_PROGRESS:{month}:{cursor_end.isoformat()}")
        cursor_end = next_end

    return sorted(rows.items(), key=lambda x: x[0]), pages


def _episodes(values: list[str], target: str) -> int:
    n = 0
    prev = None
    for value in values:
        if value == target and prev != target:
            n += 1
        prev = value
    return n


def _validate_month(
    month: str,
    anchor: float,
    points: list[tuple[pd.Timestamp, float]],
    provider_pages: int,
) -> MonthMetrics:
    if anchor <= 0:
        raise RuntimeError(f"INVALID_ANCHOR:{month}:{anchor}")
    if not points:
        return MonthMetrics(
            month, anchor, 0, None, None, None, None, None, None,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None, provider_pages,
        )

    state = EmergencyState(level_threshold_abs=THRESHOLD, reversal_threshold_abs=THRESHOLD)
    levels: list[str] = []
    alerts: list[str] = []
    cross_through = 0
    cross_through_missing_alert = 0
    transitions = 0

    prices = [price for _, price in points]
    displacements = [price / anchor - 1.0 for price in prices]

    for ts, close in points:
        before = state.shock_direction
        level, alert = state.update(ts, close, anchor)
        after = state.shock_direction
        levels.append(level.value)
        alerts.append(alert.value)
        if after != before:
            transitions += 1
            if before in (Direction.UP, Direction.DOWN) and after in (Direction.UP, Direction.DOWN) and before != after:
                cross_through += 1
                expected = ReversalAlert.DOWN_ALERT if before == Direction.UP else ReversalAlert.UP_ALERT
                if alert != expected:
                    cross_through_missing_alert += 1

    gaps: list[float] = []
    for i in range(1, len(points)):
        gap = (points[i][0] - points[i - 1][0]).total_seconds()
        if gap > 120:
            gaps.append(gap)

    return MonthMetrics(
        month=month,
        anchor=anchor,
        observed_minutes=len(points),
        first_ts=points[0][0].isoformat(),
        last_ts=points[-1][0].isoformat(),
        min_price=min(prices),
        max_price=max(prices),
        min_displacement=min(displacements),
        max_displacement=max(displacements),
        up_level_rows=sum(v == Direction.UP.value for v in levels),
        down_level_rows=sum(v == Direction.DOWN.value for v in levels),
        up_level_episodes=_episodes(levels, Direction.UP.value),
        down_level_episodes=_episodes(levels, Direction.DOWN.value),
        up_alert_rows=sum(v == ReversalAlert.UP_ALERT.value for v in alerts),
        down_alert_rows=sum(v == ReversalAlert.DOWN_ALERT.value for v in alerts),
        up_alert_episodes=_episodes(alerts, ReversalAlert.UP_ALERT.value),
        down_alert_episodes=_episodes(alerts, ReversalAlert.DOWN_ALERT.value),
        shock_direction_transitions=transitions,
        cross_through_transitions=cross_through,
        cross_through_without_expected_alert=cross_through_missing_alert,
        gap_gt_120s_count_unclassified=len(gaps),
        max_gap_seconds_unclassified=max(gaps) if gaps else None,
        provider_pages=provider_pages,
    )


def _load_anchors(start_month: str, end_month: str) -> list[tuple[str, float]]:
    df = pd.read_csv(ANCHOR_FILE)
    required = {"month", ANCHOR_COLUMN}
    missing = required - set(df.columns)
    if missing:
        raise RuntimeError(f"ANCHOR_FILE_MISSING_COLUMNS:{sorted(missing)}")
    df["month"] = df["month"].astype(str)
    mask = (df["month"] >= start_month) & (df["month"] <= end_month)
    out: list[tuple[str, float]] = []
    for _, row in df.loc[mask].sort_values("month").iterrows():
        value = pd.to_numeric(row[ANCHOR_COLUMN], errors="coerce")
        if pd.isna(value) or float(value) <= 0:
            raise RuntimeError(f"INVALID_ANCHOR:{row['month']}:{value}")
        out.append((str(row["month"]), float(value)))
    return out


def _write_outputs(report: dict, month_rows: list[MonthMetrics], json_path: Path, csv_path: Path) -> None:
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    pd.DataFrame([asdict(x) for x in month_rows]).to_csv(csv_path, index=False)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start-month", default="2023-01")
    parser.add_argument("--end-month", default="2026-07")
    parser.add_argument("--output-json", default="emergency_intraday_replay_v146.json")
    parser.add_argument("--output-csv", default="emergency_intraday_replay_v146_months.csv")
    args = parser.parse_args()

    generated_at = datetime.now(timezone.utc).isoformat()
    json_path = Path(args.output_json)
    csv_path = Path(args.output_csv)
    month_rows: list[MonthMetrics] = []
    report: dict = {
        "contract": "GOLD_CONTROL_EMERGENCY_INTRADAY_REPLAY_VALIDATION_V146",
        "generated_at": generated_at,
        "code_sha": os.environ.get("GOLD_CODE_SHA", "NOT_PROVIDED"),
        "provider": "Twelve Data",
        "symbol": SYMBOL,
        "interval": INTERVAL,
        "requested_timezone": "UTC",
        "evidence_class": "HISTORICAL_RESEARCH_RETRIEVAL",
        "prospective_claim": False,
        "database_write": "NONE",
        "raw_market_values_logged": False,
        "raw_market_values_artifacted": False,
        "anchor_source": str(ANCHOR_FILE.relative_to(ROOT)),
        "anchor_column": ANCHOR_COLUMN,
        "level_threshold_abs": THRESHOLD,
        "reversal_threshold_abs": THRESHOLD,
        "threshold_retuned": False,
        "session_calendar_authority": "UNRESOLVED_DO_NOT_CLASSIFY_GAPS_AS_MISSING",
        "validation_scope": {
            "start_month": args.start_month,
            "end_month": args.end_month,
            "page_outputsize": PAGE_OUTPUTSIZE,
            "pagination": "BACKWARD_END_DATE_ONE_MINUTE_BEFORE_EARLIEST_RETURNED_ROW",
            "min_request_interval_seconds": MIN_REQUEST_INTERVAL_SECONDS,
        },
    }

    try:
        anchors = _load_anchors(args.start_month, args.end_month)
        if not anchors:
            raise RuntimeError("NO_ANCHORS_IN_REQUESTED_RANGE")
        session = _session()
        report["provider_earliest_timestamp_1min"] = _earliest_timestamp(session)
        for month, anchor in anchors:
            points, pages = _fetch_month(session, month)
            metrics = _validate_month(month, anchor, points, pages)
            month_rows.append(metrics)
            print(json.dumps({
                "month": month,
                "provider_pages": pages,
                "observed_minutes": metrics.observed_minutes,
                "level_episodes": metrics.up_level_episodes + metrics.down_level_episodes,
                "reversal_episodes": metrics.up_alert_episodes + metrics.down_alert_episodes,
                "cross_through": metrics.cross_through_transitions,
            }, sort_keys=True), flush=True)

        total_minutes = sum(x.observed_minutes for x in month_rows)
        zero_months = [x.month for x in month_rows if x.observed_minutes == 0]
        total_level_episodes = sum(x.up_level_episodes + x.down_level_episodes for x in month_rows)
        total_alert_episodes = sum(x.up_alert_episodes + x.down_alert_episodes for x in month_rows)
        total_alert_rows = sum(x.up_alert_rows + x.down_alert_rows for x in month_rows)
        total_cross = sum(x.cross_through_transitions for x in month_rows)
        cross_missing = sum(x.cross_through_without_expected_alert for x in month_rows)
        months_level = sum((x.up_level_episodes + x.down_level_episodes) > 0 for x in month_rows)
        months_reversal = sum((x.up_alert_episodes + x.down_alert_episodes) > 0 for x in month_rows)

        report["aggregate"] = {
            "months_requested_with_anchor": len(anchors),
            "months_retrieved": len(month_rows),
            "zero_observation_months": zero_months,
            "observed_minutes": total_minutes,
            "provider_pages": sum(x.provider_pages for x in month_rows),
            "months_with_level_episode": months_level,
            "months_with_reversal_episode": months_reversal,
            "level_episodes": total_level_episodes,
            "reversal_alert_episodes": total_alert_episodes,
            "reversal_alert_rows": total_alert_rows,
            "cross_through_transitions": total_cross,
            "cross_through_without_expected_alert": cross_missing,
        }
        report["gates"] = {
            "DATA_COVERAGE": "PASS" if not zero_months else "BLOCKED_ZERO_OBSERVATION_MONTHS",
            "V146_CROSS_THROUGH_INVARIANT": "PASS" if cross_missing == 0 else "FAIL",
            "THRESHOLD_4PCT_EMPIRICAL_BEHAVIOR": "MEASURED_NOT_TUNED",
            "FALSE_ALARM_RATE": "NOT_PROVEN_NO_INDEPENDENT_LABEL_CONTRACT",
            "SESSION_GAP_VALIDITY": "NOT_PROVEN_SESSION_CALENDAR_UNRESOLVED",
            "PRODUCTION_PROMOTION": "BLOCKED_PENDING_GOVERNANCE_AND_RELEASE_GATES",
        }
        report["status"] = (
            "PASS_REPLAY_EXECUTION_WITH_METHOD_LIMITATIONS"
            if not zero_months and cross_missing == 0
            else "BLOCKED_OR_FAIL"
        )
        _write_outputs(report, month_rows, json_path, csv_path)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0 if report["status"] == "PASS_REPLAY_EXECUTION_WITH_METHOD_LIMITATIONS" else 2
    except Exception as exc:
        report["status"] = "BLOCKED"
        report["error"] = f"{type(exc).__name__}:{exc}"
        _write_outputs(report, month_rows, json_path, csv_path)
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
