from __future__ import annotations

import importlib.util
import json
import os
import sys
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

V3_PATH = Path(__file__).with_name("market_shock_challenger_v3.py")
_spec = importlib.util.spec_from_file_location("market_shock_challenger_v3_replay_shared", V3_PATH)
if not _spec or not _spec.loader:
    raise RuntimeError(f"V3_MODULE_NOT_FOUND:{V3_PATH}")
v3 = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = v3
_spec.loader.exec_module(v3)

START = pd.Timestamp("2020-04-06 00:00:00", tz="UTC")
END = pd.Timestamp("2025-12-31 23:59:59", tz="UTC")
CUTOFF = pd.Timestamp("2025-01-01 00:00:00", tz="UTC")
OUTDIR = Path("market_shock_v3_2025_replay")


def _direction_label(x: float) -> str:
    if x > 0:
        return "UP"
    if x < 0:
        return "DOWN"
    return "NEUTRAL"


def build_episodes(shock: pd.DataFrame) -> pd.DataFrame:
    if shock.empty:
        return pd.DataFrame(
            columns=[
                "episode_id", "start_ts", "end_ts", "ny17_start_date", "ny17_end_date",
                "direction", "bars", "states", "max_score5", "max_score30",
                "max_abs_5m_return_pct", "max_abs_30m_move_pct", "bns_any_expost",
            ]
        )

    s = shock.sort_values("ts").copy().reset_index(drop=True)
    direction = s["shock_direction"].map(_direction_label)
    gap = s["ts"].diff().dt.total_seconds()
    new_episode = gap.isna() | gap.gt(600) | direction.ne(direction.shift(1))
    s["episode_id"] = new_episode.cumsum().astype(int)
    s["direction_label"] = direction

    rows: list[dict] = []
    for episode_id, g in s.groupby("episode_id", sort=True):
        states = ",".join(sorted(set(g["shock_state"].astype(str))))
        rows.append(
            {
                "episode_id": int(episode_id),
                "start_ts": pd.Timestamp(g["ts"].iloc[0]).isoformat(),
                "end_ts": pd.Timestamp(g["ts"].iloc[-1]).isoformat(),
                "ny17_start_date": str(g["ny17_bucket"].iloc[0]),
                "ny17_end_date": str(g["ny17_bucket"].iloc[-1]),
                "direction": str(g["direction_label"].iloc[0]),
                "bars": int(len(g)),
                "states": states,
                "max_score5": float(g["score5"].max(skipna=True)) if g["score5"].notna().any() else None,
                "max_score30": float(g["score30"].max(skipna=True)) if g["score30"].notna().any() else None,
                "max_abs_5m_return_pct": float((g["ret"].abs() * 100.0).max(skipna=True)) if g["ret"].notna().any() else None,
                "max_abs_30m_move_pct": float((g["move30"].abs() * 100.0).max(skipna=True)) if g["move30"].notna().any() else None,
                "bns_any_expost": bool(g["bns_day_sig_expost"].any()),
            }
        )
    return pd.DataFrame(rows)


def build_daily(seg: pd.DataFrame, episodes: pd.DataFrame) -> pd.DataFrame:
    x = seg.copy()
    x["direction_label"] = x["shock_direction"].map(_direction_label)
    shock = x[x["shock_sig"]].copy()

    grouped = x.groupby("ny17_bucket", sort=True)
    rows: list[dict] = []
    for bucket, g in grouped:
        sg = shock[shock["ny17_bucket"].eq(bucket)]
        up = int((sg["shock_direction"] > 0).sum())
        down = int((sg["shock_direction"] < 0).sum())
        if up > down:
            net_direction = "UP"
        elif down > up:
            net_direction = "DOWN"
        elif up or down:
            net_direction = "MIXED"
        else:
            net_direction = "OFF"
        ep_starts = int((episodes["ny17_start_date"].eq(str(bucket))).sum()) if not episodes.empty else 0
        rows.append(
            {
                "date": str(bucket),
                "market_shock_v3": bool(len(sg) > 0),
                "shock_bars": int(len(sg)),
                "shock_episode_starts": ep_starts,
                "up_shock_bars": up,
                "down_shock_bars": down,
                "net_shock_direction": net_direction,
                "compound_bars": int(sg["compound_sig"].sum()) if not sg.empty else 0,
                "instant_jump_only_bars": int((sg["lm_sig"] & ~sg["evt30_sig"]).sum()) if not sg.empty else 0,
                "fast_move_only_bars": int((sg["evt30_sig"] & ~sg["lm_sig"]).sum()) if not sg.empty else 0,
                "max_score5": float(sg["score5"].max(skipna=True)) if not sg.empty and sg["score5"].notna().any() else None,
                "max_score30": float(sg["score30"].max(skipna=True)) if not sg.empty and sg["score30"].notna().any() else None,
                "bns_day_sig_expost": bool(g["bns_day_sig_expost"].any()),
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    OUTDIR.mkdir(parents=True, exist_ok=True)
    client = v3.TwelveClient()
    earliest = client.earliest()
    raw = client.history(START, END)
    data = v3.build_returns(raw)

    train = data[data["ts"] < CUTOFF].copy()
    if len(train) < 100000:
        raise RuntimeError(f"TRAIN_TOO_SMALL:2025:{len(train)}")
    periodicity = v3.fit_periodicity(train)
    train_scored = v3.add_scores(train, periodicity)
    evt30 = v3.fit_evt(train_scored["score30"])
    segment_report, seg, bns = v3.score_segment(data, 2025, periodicity, evt30)

    shock = seg[seg["shock_sig"]].copy().sort_values("ts").reset_index(drop=True)
    shock["direction"] = shock["shock_direction"].map(_direction_label)
    shock_export = shock[
        [
            "ts", "ny17_bucket", "shock_state", "direction", "score5", "score30",
            "ret", "move30", "period_source", "lm_sig", "evt30_sig", "compound_sig",
            "bns_day_sig_expost", "gap_reopen_context", "gap_reopen_warmup",
        ]
    ].copy()
    shock_export["return_5m_pct"] = shock_export.pop("ret") * 100.0
    shock_export["move_30m_pct"] = shock_export.pop("move30") * 100.0

    episodes = build_episodes(shock)
    daily = build_daily(seg, episodes)

    shock_export.to_csv(OUTDIR / "MARKET_SHOCK_V3_2025_SIGNAL_BARS.csv", index=False)
    episodes.to_csv(OUTDIR / "MARKET_SHOCK_V3_2025_EPISODES.csv", index=False)
    daily.to_csv(OUTDIR / "MARKET_SHOCK_V3_2025_DAILY.csv", index=False)
    bns.to_csv(OUTDIR / "MARKET_SHOCK_V3_2025_BNS_EXPOST.csv", index=False)

    meta = {
        "replay_id": "MARKET_SHOCK_V3_2025_DETAILED_REPLAY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "code_sha": os.environ.get("GOLD_CODE_SHA", "NOT_PROVIDED"),
        "source": "Twelve Data XAU/USD 5min",
        "provider_earliest_timestamp_5m": earliest,
        "history_start": START.isoformat(),
        "history_end": END.isoformat(),
        "train_end_exclusive": CUTOFF.isoformat(),
        "training_rows": int(len(train)),
        "2025_rows": int(len(seg)),
        "2025_adjusted_scoring_coverage": segment_report["adjusted_scoring_coverage"],
        "2025_shock_bars": int(shock["shock_sig"].sum()),
        "2025_episodes_direction_split": episodes["direction"].value_counts().to_dict() if not episodes.empty else {},
        "2025_episode_count_direction_sensitive": int(len(episodes)),
        "2025_original_episode_count_direction_agnostic": int(segment_report["market_shock_v3"]["episodes"]),
        "2025_shock_rate": segment_report["market_shock_v3"]["signal_rate"],
        "2025_up_shock_bars": segment_report["up_shock_bars"],
        "2025_down_shock_bars": segment_report["down_shock_bars"],
        "2025_compound_bars": segment_report["compound_bars"],
        "2025_instant_jump_only_bars": segment_report["instant_jump_only_bars"],
        "2025_fast_move_only_bars": segment_report["fast_move_only_bars"],
        "periodicity_exact_slots": int(len(periodicity.exact)),
        "periodicity_tod_slots": int(len(periodicity.tod)),
        "evt30": asdict(evt30),
        "lm_critical_999": float(v3.lm_critical(v3.LM_MAIN_ALPHA)),
        "database_write": "NONE",
        "random_split": "NONE",
        "future_data_in_2025_fit": False,
        "raw_full_price_history_artifacted": False,
        "notes": [
            "This replay exports all 2025 Market Shock V3 signal bars, not only the top-N aggregate report.",
            "BNS is retained as ex-post diagnostic only and is not part of the live Market Shock V3 vote.",
            "Direction-sensitive episodes split when the shock direction changes; the original V3 episode count is also retained for reconciliation.",
        ],
    }
    (OUTDIR / "MARKET_SHOCK_V3_2025_SUMMARY.json").write_text(
        json.dumps(meta, indent=2, sort_keys=True), encoding="utf-8"
    )

    print(json.dumps(meta, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
