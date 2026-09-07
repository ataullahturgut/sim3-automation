from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from gold_axis_2026.tools import market_shock_challenger_v1 as v1
from gold_axis_2026.tools import market_shock_direction_audit_v1 as direction_audit
from gold_axis_2026.tools.market_shock_challenger_v1_lm_sn_fix import lm_critical as corrected_lm_critical

YEARS = (2024, 2025, 2026)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", default="2020-04-06 00:00:00")
    parser.add_argument("--end", default="2026-08-31 23:59:59")
    parser.add_argument("--output", default="market_shock_unified_replay_v1.json")
    args = parser.parse_args()

    # Methodology patch is intentionally isolated to Lee-Mykland Eq. (13) S_n.
    v1.lm_critical = corrected_lm_critical

    report: dict = {
        "contract": "GOLD_CONTROL_MARKET_SHOCK_UNIFIED_REPLAY_V1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "code_sha": os.environ.get("GOLD_CODE_SHA", "NOT_PROVIDED"),
        "provider": "Twelve Data",
        "symbol": v1.SYMBOL,
        "interval": v1.INTERVAL,
        "evidence_class": "HISTORICAL_RESEARCH_RETRIEVAL",
        "prospective_claim": False,
        "database_write": "NONE",
        "raw_market_values_logged": False,
        "raw_market_values_artifacted": False,
        "retrieval_architecture": {
            "five_minute_history_fetches": 1,
            "shared_by": ["LM_SN_CORRECTED_REPLAY", "REALIZED_MOVE_COVERAGE", "FORWARD_DIRECTION_AUDIT"],
            "purpose": "AVOID_DUPLICATE_PROVIDER_CREDITS_WITHOUT_PERSISTING_RAW_MARKET_VALUES",
        },
        "methodology_patch": {
            "scope": "ISOLATED_ONE_FORMULA_PATCH",
            "changed": "LM_S_N_ONLY",
            "v1_formula": "1/(2*c*sqrt(2*log(n)))",
            "corrected_formula": "1/(c*sqrt(2*log(n)))",
            "local_variance_changed": False,
            "periodicity_changed": False,
            "evt_changed": False,
            "consensus_rule_changed": False,
            "synthetic_protocol_changed": False,
        },
        "direction_audit_contract": {
            "forward_horizons_minutes_frozen_before_run": list(direction_audit.FORWARD_HORIZONS_MIN),
            "large_move_proxy_thresholds_pct_frozen_before_run": list(direction_audit.ABS_MOVE_THRESHOLDS_PCT),
            "jump_direction": "CONTEMPORANEOUS_REALIZED_DIRECTION_NOT_FUTURE_FORECAST",
            "post_signal_direction": "INDEPENDENT_REALIZED_FORWARD_RETURN",
            "false_positive_rate": "NOT_PROVEN_NO_AUTHORITATIVE_EVENT_LABEL_SET",
        },
        "production_promotion": "BLOCKED_RESEARCH_ONLY",
    }

    try:
        client = v1.TwelveClient()
        report["provider_earliest_timestamp_5m"] = client.earliest()
        start = pd.Timestamp(args.start, tz="UTC")
        end = pd.Timestamp(args.end, tz="UTC")

        # Critical credit-saving step: fetch once, reuse in every 5m audit below.
        raw = client.history(start, end)
        data = v1.build_returns(raw)
        close_map = {pd.Timestamp(ts): float(close) for ts, close in zip(data["ts"], data["close"])}

        report["history"] = {
            "rows": int(len(data)),
            "first_ts": data["ts"].min().isoformat(),
            "last_ts": data["ts"].max().isoformat(),
            "valid_5m_returns": int(data["ret"].notna().sum()),
            "gaps_gt_10min": int(data["gap_s"].gt(600).sum()),
        }

        fit_reports = []
        segment_reports = []
        synthetic_reports = []
        direction_reports = []
        top_events = []

        for year in YEARS:
            train = data[data["ts"] < pd.Timestamp(f"{year}-01-01", tz="UTC")].copy()
            test = data[data["ts"].dt.year.eq(year)].copy()
            if year == 2026:
                test = test[test["ts"] < pd.Timestamp("2026-09-01", tz="UTC")].copy()
            if len(train) < 100000 or len(test) < 10000:
                raise RuntimeError(f"SEGMENT_COVERAGE_TOO_SMALL:{year}:{len(train)}:{len(test)}")

            periodicity = v1.fit_periodicity(train)
            train_scored = v1.add_scores(train, periodicity)
            evt5 = v1.fit_evt(train_scored["score5"])
            evt30 = v1.fit_evt(train_scored["score30"])
            scored_all = v1.add_scores(data, periodicity)
            seg_report, seg = v1.summarize_segment(scored_all, year, evt5, evt30)
            synth = v1.synthetic_injection(seg, evt5, evt30, year)
            episodes = direction_audit._episode_starts(seg)

            fit_reports.append({
                "year": year,
                "train_end_exclusive": f"{year}-01-01T00:00:00+00:00",
                "train_rows": int(len(train)),
                "periodicity_slots": int(len(periodicity)),
                "evt5": asdict(evt5),
                "evt30": asdict(evt30),
                "lm_critical_95": corrected_lm_critical(0.05),
                "lm_critical_99": corrected_lm_critical(0.01),
                "lm_critical_999": corrected_lm_critical(0.001),
            })
            segment_reports.append(seg_report)
            synthetic_reports.append(synth)
            top_events.extend(v1.top_consensus_events(seg, year, n=20))
            direction_reports.append({
                "year": year,
                "consensus_signal_bars": int(seg_report["consensus"]["signal_bars"]),
                "consensus_episodes": int(seg_report["consensus"]["episodes"]),
                "consensus_signal_rate": float(seg_report["consensus"]["signal_rate"]),
                "episode_starts_count": int(len(episodes)),
                "large_realized_move_coverage_5m": direction_audit._coverage(seg, "ret"),
                "large_realized_move_coverage_30m": direction_audit._coverage(seg, "move30"),
                "post_signal_forward_direction": direction_audit._forward_outcomes(episodes, close_map),
                "signal_magnitude_distribution": direction_audit._signal_magnitude(seg),
            })
            print(json.dumps({
                "year": year,
                "consensus_bars": seg_report["consensus"]["signal_bars"],
                "consensus_episodes": seg_report["consensus"]["episodes"],
                "synthetic_2pct_power": synth["consensus_power_by_abs_size"][str(0.02)],
                "recall_5m_1pct": direction_reports[-1]["large_realized_move_coverage_5m"]["1.0"]["coverage_recall"],
                "fwd30_continuation": direction_reports[-1]["post_signal_forward_direction"]["30"]["continuation_hit_rate"],
            }, sort_keys=True), flush=True)

        power2 = [x["consensus_power_by_abs_size"][str(0.02)] for x in synthetic_reports]
        monotone = all(x["monotone_with_2pct_tolerance"] for x in synthetic_reports)
        consensus_rates = [x["consensus"]["signal_rate"] for x in segment_reports]

        report["fits"] = fit_reports
        report["segments"] = segment_reports
        report["synthetic_injection"] = synthetic_reports
        report["direction_audit"] = direction_reports
        report["top_consensus_events"] = sorted(
            top_events,
            key=lambda x: max(x["score5"], x["score30"] or 0),
            reverse=True,
        )[:30]
        report["gates"] = {
            "FORECAST_INDEPENDENCE": "PASS",
            "WALK_FORWARD_NO_FUTURE_TRAINING": "PASS",
            "SYNTHETIC_POWER_MONOTONE": "PASS" if monotone else "REVIEW",
            "MIN_2PCT_SYNTHETIC_CONSENSUS_POWER": float(min(power2)),
            "MAX_HISTORICAL_CONSENSUS_BAR_RATE": float(max(consensus_rates)),
            "TRUE_FALSE_POSITIVE_RATE_REAL_HISTORY": "NOT_PROVEN_NO_AUTHORITATIVE_EVENT_LABEL_SET",
            "SESSION_CALENDAR": "NOT_PROVEN_GAPS_GT_10MIN_EXCLUDED_NOT_CLASSIFIED",
            "FORWARD_DIRECTION_IS_PROSPECTIVE_EVIDENCE": False,
            "PRODUCTION_PROMOTION": "BLOCKED_RESEARCH_ONLY",
        }
        report["status"] = "HISTORICAL_UNIFIED_REPLAY_COMPLETE_NOT_PRODUCTION_GATE"
        Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except Exception as exc:
        report["status"] = "BLOCKED"
        report["error"] = f"{type(exc).__name__}:{exc}"
        Path(args.output).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
