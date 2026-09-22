from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import psycopg

IDENTITY = "DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_RESEARCH"
TABLE = "public.xau_intraday_research_cache_5m"
TZ = "America/New_York"
MIN_BARS = 240
MOMENTUM_DAYS = 20
RS_DAYS = 5
REF_DAYS = 250
Q = 0.80

@dataclass(frozen=True)
class Day:
    d: date
    close: float
    n_bars: int
    rs_plus_1d: float
    rs_minus_1d: float

def db_url() -> str:
    v = os.environ.get("NEON_DATABASE_URL", "").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def load_days(end_exclusive: str) -> list[Day]:
    sql = f"""
    with b as (
      select
        (observation_ts at time zone '{TZ}')::date as d,
        observation_ts,
        close::double precision as close,
        lag(close::double precision) over (
          partition by (observation_ts at time zone '{TZ}')::date
          order by observation_ts
        ) as prev_close
      from {TABLE}
      where observation_ts >= '2020-01-01'::timestamptz
        and observation_ts < %s::timestamptz
        and extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    ),
    intr as (
      select
        d, observation_ts, close,
        case when prev_close is not null and prev_close > 0
             then ln(close/prev_close)
             else null end as r
      from b
    )
    select
      d,
      count(*)::int as n_bars,
      (array_agg(close order by observation_ts desc))[1]::double precision as close,
      coalesce(sum(case when r > 0 then r*r else 0 end),0)::double precision as rs_plus_1d,
      coalesce(sum(case when r < 0 then r*r else 0 end),0)::double precision as rs_minus_1d
    from intr
    group by d
    having count(*) >= {MIN_BARS}
    order by d
    """
    with psycopg.connect(db_url(), autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only = on")
            cur.execute(sql, (end_exclusive,))
            raw = cur.fetchall()

    out: list[Day] = []
    for d, n_bars, close, rp, rm in raw:
        vals = [float(close), float(rp), float(rm)]
        if not all(math.isfinite(x) for x in vals):
            raise RuntimeError(f"NONFINITE_DAILY_ROW:{d}")
        if vals[0] <= 0 or vals[1] < 0 or vals[2] < 0:
            raise RuntimeError(f"INVALID_DAILY_ROW:{d}")
        out.append(Day(d, vals[0], int(n_bars), vals[1], vals[2]))
    if len(out) < 500:
        raise RuntimeError(f"INSUFFICIENT_DAILY_ROWS:{len(out)}")
    return out

def panel_hash(days: list[Day], through: date | None = None) -> str:
    rows = days if through is None else [x for x in days if x.d <= through]
    s = "\n".join(
        f"{x.d.isoformat()}|{x.close:.12f}|{x.n_bars}|{x.rs_plus_1d:.16g}|{x.rs_minus_1d:.16g}"
        for x in rows
    )
    return hashlib.sha256(s.encode()).hexdigest()

def nearest_rank_q80(a: np.ndarray) -> float:
    if len(a) != REF_DAYS:
        raise RuntimeError(f"BAD_QUANTILE_WINDOW:{len(a)}")
    if not np.all(np.isfinite(a)):
        raise RuntimeError("NONFINITE_QUANTILE_INPUT")
    rank = int(math.ceil(Q * len(a)))
    return float(np.sort(a)[rank - 1])

def build_signal_rows(days: list[Day]) -> list[dict]:
    n = len(days)
    close = np.array([x.close for x in days], dtype=float)
    rp1 = np.array([x.rs_plus_1d for x in days], dtype=float)
    rm1 = np.array([x.rs_minus_1d for x in days], dtype=float)

    rs_plus = np.full(n, np.nan)
    rs_minus = np.full(n, np.nan)
    for i in range(RS_DAYS - 1, n):
        rs_plus[i] = float(np.sum(rp1[i-RS_DAYS+1:i+1]))
        rs_minus[i] = float(np.sum(rm1[i-RS_DAYS+1:i+1]))

    rows = []
    first_signal_i = (RS_DAYS - 1) + (REF_DAYS - 1)
    first_signal_i = max(first_signal_i, MOMENTUM_DAYS)
    for i in range(first_signal_i, n - 1):
        if not (math.isfinite(rs_plus[i]) and math.isfinite(rs_minus[i])):
            continue

        qplus = nearest_rank_q80(rs_plus[i-REF_DAYS+1:i+1])
        qminus = nearest_rank_q80(rs_minus[i-REF_DAYS+1:i+1])

        high_plus = rs_plus[i] > qplus
        high_minus = rs_minus[i] > qminus
        if high_plus and high_minus:
            region = 1
        elif (not high_plus) and high_minus:
            region = 2
        elif (not high_plus) and (not high_minus):
            region = 3
        else:
            region = 4

        mom = math.log(close[i] / close[i-MOMENTUM_DAYS])
        tsm = 1 if mom > 0 else -1

        if region == 1:
            s1 = 0
            s2 = 0
        elif region == 2:
            s1 = -1
            s2 = -1 if tsm == 1 else 0
        elif region == 3:
            s1 = tsm
            s2 = tsm
        elif region == 4:
            s1 = 1
            s2 = 1 if tsm == -1 else 0
        else:
            raise AssertionError(region)

        next_ret = math.log(close[i+1] / close[i])
        if next_ret == 0:
            continue
        actual_up = int(next_ret > 0)

        rows.append({
            "origin_date": days[i].d.isoformat(),
            "target_date": days[i+1].d.isoformat(),
            "origin_close": close[i],
            "target_close": close[i+1],
            "target_log_return": next_ret,
            "actual_up": actual_up,
            "momentum_20d_log_return": mom,
            "tsm_signal": tsm,
            "rs_plus_5d": float(rs_plus[i]),
            "rs_minus_5d": float(rs_minus[i]),
            "q80_plus_250d": qplus,
            "q80_minus_250d": qminus,
            "region": region,
            "ttsm_s1_signal": s1,
            "ttsm_s2_signal": s2,
        })
    return rows

def signal_metrics(rows: list[dict], key: str) -> dict:
    if not rows:
        return {"n": 0}
    y = np.array([int(r["actual_up"]) for r in rows], dtype=int)
    s = np.array([int(r[key]) for r in rows], dtype=int)
    active = s != 0
    actual_up = y == 1
    actual_down = y == 0
    pred_up = s == 1
    pred_down = s == -1

    def safe(num, den):
        return float(num / den) if den else None

    active_n = int(np.sum(active))
    active_acc = safe(int(np.sum((pred_up == actual_up) & active)), active_n)

    au_active = actual_up & active
    ad_active = actual_down & active
    up_s_active = safe(int(np.sum(pred_up & actual_up)), int(np.sum(au_active)))
    down_s_active = safe(int(np.sum(pred_down & actual_down)), int(np.sum(ad_active)))
    if up_s_active is not None and down_s_active is not None:
        active_ba = (up_s_active + down_s_active) / 2
    else:
        active_ba = None

    full_up_s = safe(int(np.sum(pred_up & actual_up)), int(np.sum(actual_up)))
    full_down_s = safe(int(np.sum(pred_down & actual_down)), int(np.sum(actual_down)))
    down_precision = safe(int(np.sum(pred_down & actual_down)), int(np.sum(pred_down)))
    up_precision = safe(int(np.sum(pred_up & actual_up)), int(np.sum(pred_up)))
    if down_precision is not None and full_down_s is not None and (down_precision + full_down_s) > 0:
        down_f1 = 2 * down_precision * full_down_s / (down_precision + full_down_s)
    else:
        down_f1 = 0.0

    full_hit = float(np.mean((pred_up & actual_up) | (pred_down & actual_down)))

    return {
        "n": int(len(rows)),
        "coverage": float(np.mean(active)),
        "active_n": active_n,
        "active_accuracy": active_acc,
        "active_balanced_accuracy": active_ba,
        "active_up_sensitivity": up_s_active,
        "active_down_sensitivity": down_s_active,
        "full_timeline_hit_rate_neutral_as_miss": full_hit,
        "full_timeline_up_sensitivity": full_up_s,
        "full_timeline_down_sensitivity": full_down_s,
        "up_precision": up_precision,
        "down_precision": down_precision,
        "down_f1_full_timeline": down_f1,
        "false_down_rate_among_actual_up": safe(int(np.sum(pred_down & actual_up)), int(np.sum(actual_up))),
        "forecast_up": int(np.sum(pred_up)),
        "forecast_down": int(np.sum(pred_down)),
        "forecast_neutral": int(np.sum(s == 0)),
        "actual_up": int(np.sum(actual_up)),
        "actual_down": int(np.sum(actual_down)),
        "always_up_accuracy": float(np.mean(actual_up)),
        "always_down_accuracy": float(np.mean(actual_down)),
    }

def reversal_metrics(rows: list[dict], key: str) -> dict:
    if not rows:
        return {}
    y = np.array([int(r["actual_up"]) for r in rows], dtype=int)
    tsm = np.array([int(r["tsm_signal"]) for r in rows], dtype=int)
    s = np.array([int(r[key]) for r in rows], dtype=int)

    pool = (tsm == 1) & (y == 0)
    alerts = (tsm == 1) & (s == -1)
    captured = pool & (s == -1)
    false_alert = (tsm == 1) & (y == 1) & (s == -1)

    return {
        "up_momentum_actual_down_n": int(np.sum(pool)),
        "up_to_down_reversal_sensitivity": float(np.sum(captured) / np.sum(pool)) if np.sum(pool) else None,
        "down_alerts_while_up_momentum_n": int(np.sum(alerts)),
        "down_alert_precision_while_up_momentum": float(np.sum(captured) / np.sum(alerts)) if np.sum(alerts) else None,
        "false_down_alerts_while_up_momentum_n": int(np.sum(false_alert)),
        "false_down_alert_burden_while_up_momentum": float(np.sum(false_alert) / np.sum(alerts)) if np.sum(alerts) else None,
    }

def region_metrics(rows: list[dict]) -> dict:
    out = {}
    for reg in (1,2,3,4):
        rr = [r for r in rows if int(r["region"]) == reg]
        if not rr:
            out[str(reg)] = {"n": 0}
            continue
        downs = sum(int(r["actual_up"]) == 0 for r in rr)
        ups = sum(int(r["actual_up"]) == 1 for r in rr)
        upmom = [r for r in rr if int(r["tsm_signal"]) == 1]
        dnrate_upmom = (
            sum(int(r["actual_up"]) == 0 for r in upmom) / len(upmom)
            if upmom else None
        )
        out[str(reg)] = {
            "n": len(rr),
            "share": len(rr) / len(rows),
            "next_day_down_rate": downs / len(rr),
            "next_day_up_rate": ups / len(rr),
            "up_momentum_n": len(upmom),
            "next_day_down_rate_given_up_momentum": dnrate_upmom,
        }
    return out

def summarize(rows: list[dict], period_label: str) -> dict:
    return {
        "period": period_label,
        "n": len(rows),
        "TSM": {
            "metrics": signal_metrics(rows, "tsm_signal"),
            "reversal": reversal_metrics(rows, "tsm_signal"),
        },
        "TTSM_S1": {
            "metrics": signal_metrics(rows, "ttsm_s1_signal"),
            "reversal": reversal_metrics(rows, "ttsm_s1_signal"),
        },
        "TTSM_S2": {
            "metrics": signal_metrics(rows, "ttsm_s2_signal"),
            "reversal": reversal_metrics(rows, "ttsm_s2_signal"),
        },
        "regions": region_metrics(rows),
    }

def gate_2024(summary: dict, variant: str) -> bool:
    t = summary["TSM"]
    v = summary[variant]
    tm = t["metrics"]
    vm = v["metrics"]
    vr = v["reversal"]
    tr = t["reversal"]
    return bool(
        vm["full_timeline_down_sensitivity"] is not None
        and tm["full_timeline_down_sensitivity"] is not None
        and vm["full_timeline_down_sensitivity"] >= tm["full_timeline_down_sensitivity"] + 0.10
        and vr["up_to_down_reversal_sensitivity"] is not None
        and tr["up_to_down_reversal_sensitivity"] is not None
        and vr["up_to_down_reversal_sensitivity"] >= tr["up_to_down_reversal_sensitivity"] + 0.10
        and vm["active_balanced_accuracy"] is not None
        and vm["active_balanced_accuracy"] >= 0.52
        and vm["down_precision"] is not None
        and vm["down_precision"] >= 0.45
        and vm["coverage"] >= 0.50
    )

def transport_2025(summary: dict, variant: str, passed_2024: bool) -> bool:
    if not passed_2024:
        return False
    tm = summary["TSM"]["metrics"]
    vm = summary[variant]["metrics"]
    return bool(
        vm["full_timeline_down_sensitivity"] is not None
        and tm["full_timeline_down_sensitivity"] is not None
        and vm["full_timeline_down_sensitivity"] >= tm["full_timeline_down_sensitivity"] + 0.05
        and vm["active_balanced_accuracy"] is not None
        and vm["active_balanced_accuracy"] >= 0.50
        and vm["down_precision"] is not None
        and vm["down_precision"] >= 0.45
        and vm["coverage"] >= 0.50
    )

def rows_for_target_year(rows: list[dict], year: int) -> list[dict]:
    return [r for r in rows if int(r["target_date"][:4]) == year]

def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise RuntimeError(f"NO_ROWS_FOR_CSV:{path}")
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", choices=("pre2025","2025"), required=True)
    ap.add_argument("--outdir", required=True)
    ap.add_argument("--config")
    ap.add_argument("--pre-result")
    args = ap.parse_args()

    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    if args.stage == "pre2025":
        days = load_days("2025-01-01T05:00:00Z")
        signals = build_signal_rows(days)
        s22 = summarize(rows_for_target_year(signals, 2022), "2022")
        s23 = summarize(rows_for_target_year(signals, 2023), "2023")
        s24 = summarize(rows_for_target_year(signals, 2024), "2024")

        pass_s1 = gate_2024(s24, "TTSM_S1")
        pass_s2 = gate_2024(s24, "TTSM_S2")

        audit = {
            "identity": IDENTITY,
            "source_table": TABLE,
            "timezone": TZ,
            "minimum_bars_per_day": MIN_BARS,
            "retained_daily_rows_pre2025": len(days),
            "first_retained_day": days[0].d.isoformat(),
            "last_retained_day": days[-1].d.isoformat(),
            "panel_sha256_through_2024": panel_hash(days, date(2024,12,31)),
            "production_database_write": "NONE",
        }
        config = {
            "identity": IDENTITY,
            "momentum_days": MOMENTUM_DAYS,
            "semivariance_days": RS_DAYS,
            "reference_days": REF_DAYS,
            "quantile": Q,
            "quantile_method": "empirical_nearest_rank_ceil_qn",
            "source_mapping": {
                "region1": {"S1":0,"S2":0},
                "region2": {"S1":"DOWN_ALWAYS","S2":"DOWN_IF_TSM_UP_ELSE_NEUTRAL"},
                "region3": {"S1":"TSM","S2":"TSM"},
                "region4": {"S1":"UP_ALWAYS","S2":"UP_IF_TSM_DOWN_ELSE_NEUTRAL"},
            },
            "panel_sha256_through_2024": audit["panel_sha256_through_2024"],
            "frozen_before_2025": True,
        }
        pre = {
            "identity": IDENTITY,
            "status": "PRE2025_FROZEN",
            "2022_audit": s22,
            "2023_audit": s23,
            "2024_validation": s24,
            "2024_gate": {
                "TTSM_S1": pass_s1,
                "TTSM_S2": pass_s2,
            },
            "primary_pre2025_decision": (
                "PRE2025_DOWN_REVERSAL_SIGNAL_SUPPORTED"
                if pass_s1 else "PRE2025_DOWN_REVERSAL_SIGNAL_NOT_SUPPORTED"
            ),
        }

        (outdir/"GOLD_CONTROL_DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_SOURCE_AUDIT_2026-09-21.json").write_text(json.dumps(audit, indent=2), encoding="utf-8")
        (outdir/"GOLD_CONTROL_DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_FROZEN_CONFIG_2026-09-21.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
        (outdir/"GOLD_CONTROL_DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_PRE2025_RESULT_2026-09-21.json").write_text(json.dumps(pre, indent=2), encoding="utf-8")
        write_csv(outdir/"GOLD_CONTROL_DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_2022_SIGNALS_2026-09-21.csv", rows_for_target_year(signals, 2022))
        write_csv(outdir/"GOLD_CONTROL_DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_2023_SIGNALS_2026-09-21.csv", rows_for_target_year(signals, 2023))
        write_csv(outdir/"GOLD_CONTROL_DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_2024_SIGNALS_2026-09-21.csv", rows_for_target_year(signals, 2024))
        print("TTSM_PRE2025_FREEZE_SUCCESS")
        return

    if not args.config or not args.pre_result:
        raise RuntimeError("CONFIG_AND_PRE_RESULT_REQUIRED")

    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    pre = json.loads(Path(args.pre_result).read_text(encoding="utf-8"))
    if config.get("identity") != IDENTITY or pre.get("identity") != IDENTITY:
        raise RuntimeError("IDENTITY_MISMATCH")

    days = load_days("2026-01-02T05:00:00Z")
    prefix = panel_hash(days, date(2024,12,31))
    if prefix != config["panel_sha256_through_2024"]:
        raise RuntimeError("PRE2025_PANEL_PREFIX_CHANGED")

    signals = build_signal_rows(days)
    rows25 = rows_for_target_year(signals, 2025)
    s25 = summarize(rows25, "2025")
    pass_s1_2024 = bool(pre["2024_gate"]["TTSM_S1"])
    pass_s2_2024 = bool(pre["2024_gate"]["TTSM_S2"])
    transport_s1 = transport_2025(s25, "TTSM_S1", pass_s1_2024)
    transport_s2 = transport_2025(s25, "TTSM_S2", pass_s2_2024)

    result = {
        "identity": IDENTITY,
        "status": "LOCKED_2025_REPLAY_COMPLETE",
        "2024_gate": pre["2024_gate"],
        "2025_challenge": s25,
        "2025_transport": {
            "TTSM_S1": transport_s1,
            "TTSM_S2": transport_s2,
        },
        "primary_2025_transport_decision": (
            "2025_TRANSPORT_SUPPORTED" if transport_s1 else "2025_TRANSPORT_NOT_SUPPORTED"
        ),
    }
    (outdir/"GOLD_CONTROL_DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_2025_RESULT_2026-09-21.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    write_csv(outdir/"GOLD_CONTROL_DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_2025_SIGNALS_2026-09-21.csv", rows25)

    s24 = pre["2024_validation"]
    lines = [
        "# GOLD CONTROL — TTSM REALIZED-SEMIVARIANCE XAU V1 RESULT",
        "",
        f"**Identity:** `{IDENTITY}`  ",
        "**Manifest update:** deferred pending user review.  ",
        "",
        "## Direction metrics",
        "",
        "| Period | Model | Coverage | Active BA | Full DOWN sens | DOWN precision | DOWN F1 | UP->DOWN reversal sens | Forecast U/D/N |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for label, ss in [("2024", s24), ("2025", s25)]:
        for name in ("TSM","TTSM_S1","TTSM_S2"):
            m=ss[name]["metrics"]; rv=ss[name]["reversal"]
            lines.append(
                f"| {label} | {name} | {m['coverage']:.4f} | {m['active_balanced_accuracy']:.4f} | "
                f"{m['full_timeline_down_sensitivity']:.4f} | "
                f"{(m['down_precision'] if m['down_precision'] is not None else float('nan')):.4f} | "
                f"{m['down_f1_full_timeline']:.4f} | "
                f"{(rv['up_to_down_reversal_sensitivity'] if rv['up_to_down_reversal_sensitivity'] is not None else float('nan')):.4f} | "
                f"{m['forecast_up']}/{m['forecast_down']}/{m['forecast_neutral']} |"
            )
    lines += [
        "",
        "## Frozen decisions",
        "",
        f"- 2024 TTSM-S1 gate: **{'PASS' if pass_s1_2024 else 'FAIL'}**.",
        f"- 2024 TTSM-S2 gate: **{'PASS' if pass_s2_2024 else 'FAIL'}**.",
        f"- 2025 TTSM-S1 transport: **{'PASS' if transport_s1 else 'FAIL'}**.",
        f"- 2025 TTSM-S2 transport: **{'PASS' if transport_s2 else 'FAIL'}**.",
        "- 2025 did not alter any source parameter or rule.",
        "- No manifest change was made by the model workflow.",
    ]
    (outdir/"GOLD_CONTROL_DIRECTION_TTSM_REALIZED_SEMIVARIANCE_XAU_V1_RESULT_2026-09-21.md").write_text("\n".join(lines)+"\n", encoding="utf-8")
    print("TTSM_2025_REPLAY_SUCCESS")

if __name__ == "__main__":
    main()
