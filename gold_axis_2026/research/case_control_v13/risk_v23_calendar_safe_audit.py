#!/usr/bin/env python3
"""V23 strictly research-only corrective audit of unchanged V22 decision signals.

Do not use a sparse CFTC-eligible decision panel as a trading-session calendar.
Read the complete daily PRICE calendar, not future outcomes, for evaluation.
The historical source is retrospective/reconstructed, NOT first-print PIT.
No changes to trained BASE14, CFTC21, alerts, or production/Neon.
"""
from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

O = Path(__file__).parent / "outputs"
BAD_DATE = "2026-02-27"
GAPS = (4, 6, 10)
POLICIES = {
    "BASE14_ORIGINAL_RED": lambda t: t.BASE14_original_alert_level.eq("RED"),
    "V22_ACTIVE_RED_ONLY": lambda t: t.active_RED_phase.astype(bool),
    "V22_ACTIVE_AND_YELLOW": lambda t: (t.active_RED_phase | t.yellow_carry).astype(bool),
    "V22_PRIORITIZED_PLUS_WATCH": lambda t: t.effective_review.astype(bool),
    "V22_WATCH_ONLY": lambda t: t.watch.astype(bool),
}

def _require(ok, label):
    if not bool(ok):
        raise ValueError("V23_CALENDAR_GATE_" + label)

def outcome_for_origin(prices: pd.DataFrame, date: str, horizon: int = 10):
    """Exactly the next N PRICE observations; do not bridge bad data or long gaps.

    Returns (status, minimum percentage return), with NaN for unknown outcomes.
    This function is for ex-post audit ONLY, never for decisions or model fitting.
    """
    lookup = prices.index[prices.date.eq(date)]
    _require(len(lookup) == 1, "MISSING_ORIGIN_" + date)
    i = int(lookup[0])
    q = prices.iloc[i + 1:i + 1 + horizon]
    if len(q) < horizon:
        return ("UNKNOWN_NOT_MATURE", np.nan)
    dates = pd.to_datetime(pd.concat([prices.iloc[[i]].date, q.date], ignore_index=True))
    if dates.diff().dt.days.iloc[1:].gt(7).any():
        return ("UNKNOWN_PRICE_CALENDAR_GAP", np.nan)
    if q.quarantined.any():
        return ("UNKNOWN_QUARANTINED_FUTURE_PRICE", np.nan)
    value = 100.0 * (q.price.min() / float(prices.iloc[i].price) - 1.0)
    return ("TRUE_DROP_5PCT" if value <= -5 else "FALSE_DROP_5PCT", value)

def build_daily():
    old = pd.read_csv(O / "v22_daily_decisions.csv").sort_values("origin").reset_index(drop=True)
    prices = pd.read_csv(O / "v23_price_calendar_RESEARCH_NOT_PIT.csv").sort_values("date").reset_index(drop=True)
    _require(len(old) == 647 and old.origin.is_unique, "DECISION_COUNT")
    _require(len(prices) == 713 and prices.date.is_unique, "PRICE_CALENDAR_COUNT")
    _require(prices.price.notna().all() and (prices.price > 0).all(), "PRICE_FINITE_POSITIVE")
    _require(prices.quarantined.sum() == 1 and
             prices.loc[prices.quarantined, "date"].iloc[0] == BAD_DATE,
             "EXACT_KNOWN_BAD_PRICE")
    _require(prices.source.str.contains("NOT_PIT").all(), "RESEARCH_PROVENANCE_REQUIRED")
    by_date = prices.set_index("date")
    _require(old.origin.isin(by_date.index).all(), "MISSING_DECISION_PRICE")
    expected = by_date.loc[old.origin, "price"].to_numpy(float)
    _require(np.allclose(old.price.to_numpy(float), expected, atol=1e-8, rtol=0),
             "SOURCE_PRICE_PARITY")
    _require(~by_date.loc[old.origin, "quarantined"].any(), "QUARANTINED_DECISION_ORIGIN")
    new = [outcome_for_origin(prices, str(date)) for date in old.origin]
    old["ten_day_status"] = [x[0] for x in new]
    old["next10_min_pct_AUDIT_ONLY"] = [x[1] for x in new]
    old["ten_day_mature"] = old.ten_day_status.isin(("TRUE_DROP_5PCT", "FALSE_DROP_5PCT"))
    old["ten_day_unknown"] = ~old.ten_day_mature
    old["horizon_is_complete_price_sessions"] = True
    old["horizon_price_source_PIT_certified"] = False
    _require((old.ten_day_mature == old.next10_min_pct_AUDIT_ONLY.notna()).all(),
             "LABEL_MATURITY_CONSISTENCY")
    _require((old.loc[old.origin == "2026-02-10", "ten_day_status"].iloc[0]
              == "FALSE_DROP_5PCT"), "FEB10_FALSE_NOT_TRUE")
    _require((old.loc[old.origin == "2026-02-17", "ten_day_status"].iloc[0]
              == "UNKNOWN_QUARANTINED_FUTURE_PRICE"), "FEB17_QUARANTINE")
    _require(old.loc[old.origin == "2026-09-21", "ten_day_mature"].iloc[0],
             "SEPTEMBER_HORIZON_WITH_OCTOBER_PRICE")
    old.to_csv(O / "v23_calendar_safe_daily.csv", index=False)
    return old, prices

def _clusters_hit(g, mask):
    positive = g.y5_AUDIT_ONLY.astype(bool).to_numpy()
    starts = np.flatnonzero(positive & ~np.r_[False, positive[:-1]])
    totals = int(len(starts))
    hit = 0
    for start in starts:
        end = start
        while end + 1 < len(g) and positive[end + 1]:
            end += 1
        hit += int(bool(mask[start:end + 1].any()))
    return (hit, totals)

def daily_metrics(d):
    rows = []
    for year, g in d.groupby("year"):
        g = g.reset_index(drop=True)
        pos = g.y5_AUDIT_ONLY.astype(bool).to_numpy()
        nextday = g.y1_AUDIT_ONLY.astype(bool).to_numpy()
        for policy, fn in POLICIES.items():
            flagged = fn(g).to_numpy(bool)
            ten_true = g.ten_day_status.eq("TRUE_DROP_5PCT").to_numpy(bool)
            ten_false = g.ten_day_status.eq("FALSE_DROP_5PCT").to_numpy(bool)
            ten_unknown = ~(ten_true | ten_false)
            hits, total = _clusters_hit(g, flagged)
            rows.append(dict(year=int(year), policy=policy, eligible_origins=len(g),
                             flagged_days=int(flagged.sum()),
                             false5_days=int((flagged & ~pos).sum()),
                             true5_days=int((flagged & pos).sum()),
                             nextday3_hit=int((flagged & nextday).sum()),
                             nextday3_total=int(nextday.sum()),
                             five_day_clusters_hit=hits, five_day_clusters_total=total,
                             true10_days=int((flagged & ten_true).sum()),
                             false10_days=int((flagged & ten_false).sum()),
                             unknown10_days=int((flagged & ten_unknown).sum())))
    m = pd.DataFrame(rows)
    _require((m.flagged_days == m.true10_days + m.false10_days + m.unknown10_days).all(),
             "DAILY_LABEL_PARTITION")
    m.to_csv(O / "v23_calendar_safe_daily_metrics.csv", index=False)
    return m

def episode_metrics(d):
    episodes, rows = [], []
    for gap in GAPS:
        for year, g in d.groupby("year"):
            for policy, fn in POLICIES.items():
                selected = g.loc[fn(g)].sort_values("origin").reset_index(drop=True)
                groups = []
                active = []
                for _, r in selected.iterrows():
                    if active and (pd.Timestamp(r.origin) - pd.Timestamp(active[-1].origin)).days > gap:
                        groups.append(active)
                        active = []
                    active.append(r)
                if active:
                    groups.append(active)
                for chunk in groups:
                    statuses = [str(v.ten_day_status) for v in chunk]
                    if "TRUE_DROP_5PCT" in statuses:
                        state = "TRUE"
                    elif any(s.startswith("UNKNOWN_") for s in statuses):
                        state = "UNKNOWN"
                    else:
                        state = "FALSE"
                    episodes.append(dict(year=int(year), policy=policy, gap_days=int(gap),
                                         first=str(chunk[0].origin), last=str(chunk[-1].origin),
                                         days=len(chunk), episode_status=state,
                                         five_day_target_any=any(bool(v.y5_AUDIT_ONLY) for v in chunk),
                                         independent_economic_event=False))
                p = [x for x in episodes if x["year"] == int(year)
                     and x["policy"] == policy and x["gap_days"] == int(gap)]
                rows.append(dict(year=int(year), policy=policy, gap_days=int(gap),
                                 episodes_total=len(p),
                                 episodes_true10=sum(x["episode_status"] == "TRUE" for x in p),
                                 episodes_false10=sum(x["episode_status"] == "FALSE" for x in p),
                                 episodes_unknown10=sum(x["episode_status"] == "UNKNOWN" for x in p)))
    ep, m = pd.DataFrame(episodes), pd.DataFrame(rows)
    _require((m.episodes_total == m.episodes_true10 + m.episodes_false10 + m.episodes_unknown10).all(),
             "EPISODE_LABEL_PARTITION")
    ep.to_csv(O / "v23_calendar_safe_episodes.csv", index=False)
    m.to_csv(O / "v23_calendar_safe_episode_metrics.csv", index=False)
    return ep, m

def main():
    d, prices = build_daily()
    daily = daily_metrics(d)
    _, episode = episode_metrics(d)
    feb10 = d.loc[d.origin == "2026-02-10"].iloc[0]
    summary = dict(model_retrained=False, original_alert_modified=False,
       research_only=True, firstprint_price_PIT_certified=False,
       macro_CFTC_firstprint_PIT_certified=False,
       fully_blind_validation_2026=False, label_days_are_not_independent_crashes=True,
       ten_day_horizon="next ten COMPLETE PRICE observations, no sparse decision rows",
       suspicious_price_origin="2026-02-27", suspicious_price_quarantined_not_replaced=True,
       complete_price_rows=len(prices), scored_days=len(d),
       feb10_2026_new_next10_min_pct=float(feb10.next10_min_pct_AUDIT_ONLY),
       feb10_old_sparse_next10_pct=-10.5409,
       uncertain_10day_origins=int(d.ten_day_unknown.sum()),
       source_cutoff=str(prices.date.iloc[-1]))
    (O / "v23_validation_manifest.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False)+"\n")
    print("V23_CORRECTED_DAILY_RESULTS")
    print(daily.to_string(index=False))
    print("V23_CORRECTED_EPISODES_4_DAY_GAP")
    print(episode.loc[episode.gap_days == 4].to_string(index=False))
    print("V23_RESEARCH_LIMITS", json.dumps(summary, ensure_ascii=False))

if __name__ == "__main__":
    main()
