"""Origin-safe multi-horizon tail early-warning audit, separate from frozen PRAMV V1.

Research, not production. Reconstructs 2023–2025 from frozen archived PSF
M4 target returns. No 2025 return is used in the risk-score threshold.
The 2025 archive was open during the design, therefore no untouched OOS claim.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from scipy.stats import hypergeom
from sklearn.metrics import roc_auc_score

AX = Path(__file__).resolve().parents[1]
PSF = AX / "GOLD_EXECUTION_PSF_OVN_PREDICTIONS_2026-10-07.csv"
PAIR = AX / "GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv"
MACRO_LEDGER = AX / "GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv"
ROWS = AX / "GOLD_EXECUTION_DUAL_HAZARD_ROWS_2026-10-08.csv"
METRICS = AX / "GOLD_EXECUTION_DUAL_HAZARD_METRICS_2026-10-08.csv"
SUMMARY = AX / "GOLD_EXECUTION_DUAL_HAZARD_SUMMARY_2026-10-08.json"

def main():
    p = pd.read_csv(PSF)
    p = p.loc[p.family.eq("M4_SIG_FPCA_MACRO"), ["date","year","ret_target","pred","y"]]
    p = p.sort_values("date").drop_duplicates("date", keep="last").reset_index(drop=True)
    assert p.date.is_unique
    assert p.groupby("year").size().to_dict() == {2023:256,2024:259,2025:254}
    assert np.isfinite(p.ret_target.to_numpy(float)).all()

    # Shift BEFORE rolling so no value from the predicted overnight window
    # (17:00 -> next eligible 09:00) can enter its own 17:00 forecast.
    for w in (5,20,60):
        p[f"rv{w}"] = np.sqrt(p.ret_target.astype(float).pow(2).shift(1).rolling(w, min_periods=w).mean())
    p = p.dropna(subset=["rv5","rv20","rv60"]).copy()
    p["score"] = np.sqrt(.5*p.rv5.pow(2) + .3*p.rv20.pow(2) + .2*p.rv60.pow(2))
    # Label is continuous target log-return; a 2% cutoff is on absolute
    # *log-return* and is distinct from log(1.02).
    p["tail1"] = p.ret_target.abs().ge(.01)
    p["tail2"] = p.ret_target.abs().ge(.02)

    # Unsupervised SCORE DISTRIBUTION cutoff on development years only.
    hist = np.sort(p.loc[p.year.le(2024), "score"].to_numpy(float))
    assert len(hist) == 455
    threshold = float(hist[int(np.floor(.8*(len(hist)-1)))])
    p["risk_vol"] = p.score.ge(threshold)

    # Event availability and published calendar: extra research challenger,
    # NOT a replacement for any frozen PRAMV macro-veto rule.
    c = pd.read_csv(PAIR)
    c = c.loc[c.policy.eq("PAIR_ALL"),
              ["date","macro_released","upcoming_fomc"]].drop_duplicates("date")
    p = p.merge(c, on="date", how="left", validate="one_to_one")
    # CRITICAL COVERAGE AUDIT: the raw 2025 macro ledger has ZERO FOMC
    # entries plus missing NFP/CPI months. Filled zero flags are not
    # evidence that no macro event was scheduled. Quarantine composite
    # scores for entire incomplete calendar years.
    ledger = pd.read_csv(MACRO_LEDGER)
    ledger["year"] = pd.to_datetime(ledger.event_ts_utc, utc=True).dt.year
    counts = ledger.groupby(["year","event_type"]).size()
    required = {"FOMC":8, "NFP":12, "AHE":12, "UNEMP":12, "CPI":12}
    covered_year = {year: all(int(counts.get((year, name), 0)) == n
                              for name,n in required.items())
                    for year in (2023,2024,2025)}
    assert covered_year == {2023:True,2024:True,2025:False}, covered_year
    p["calendar_source_ready"] = (
        p.year.map(covered_year).fillna(False).astype(bool) &
        p.macro_released.notna() & p.upcoming_fomc.notna()
    )
    raw_calendar = (p.macro_released.eq(1) | p.upcoming_fomc.eq(1))
    p["risk_calendar"] = raw_calendar.where(p.calendar_source_ready, pd.NA).astype("boolean")
    p["risk_combined"] = (p.risk_vol.astype("boolean") | p.risk_calendar).where(
        p.calendar_source_ready, pd.NA)
    p.to_csv(ROWS, index=False)

    rows = []
    for year in (2023,2024,2025):
        g = p.loc[p.year.eq(year)].copy()
        for name in ("risk_vol","risk_combined","risk_calendar"):
            valid = g.loc[g[name].notna()].copy()
            selected = valid.loc[valid[name].astype(bool)]
            d = dict(year=year,policy=name,n=len(valid),alerts=len(selected),
                     alert_rate=len(selected)/len(valid) if len(valid) else np.nan)
            for label in ("tail1","tail2"):
                total = int(valid[label].sum())
                hit = int(selected[label].sum())
                d[f"{label}_events"] = total
                d[f"{label}_caught"] = hit
                d[f"{label}_recall"] = hit/total if total else np.nan
                d[f"{label}_precision"] = hit/len(selected) if len(selected) else np.nan
            d["auc1"] = float(roc_auc_score(valid.tail1,valid.score)) if valid.tail1.nunique()==2 else np.nan
            d["auc2"] = float(roc_auc_score(valid.tail2,valid.score)) if valid.tail2.nunique()==2 else np.nan
            rows.append(d)
    out = pd.DataFrame(rows)
    out.to_csv(METRICS,index=False)

    z = out[(out.year.eq(2025)) & (out.policy.eq("risk_vol"))].iloc[0]
    assert (int(z.n),int(z.alerts),int(z.tail1_events),int(z.tail1_caught),
            int(z.tail2_events),int(z.tail2_caught)) == (254,95,43,25,7,6)
    assert abs(threshold-0.007644177328023349) < 1e-12

    nominal_p = float(hypergeom.sf(5,254,95,7))
    details = p[(p.year.eq(2025)) & (p.tail2)][
        ["date","ret_target","score","risk_vol","risk_calendar","risk_combined"]].to_dict("records")
    result = {
        "status":"RETROSPECTIVE_DIAGNOSTIC_NOT_FROZEN_OOS",
        "target":"17:00 -> next eligible 09:00 Europe/Istanbul",
        "source":"frozen M4 ret_target archive",
        "score":"sqrt(0.5*RV5^2 + 0.3*RV20^2 + 0.2*RV60^2)",
        "rv_definition":"sqrt(mean(previous w completed overnight log returns squared))",
        "dev_2023_2024_score_count":len(hist),
        "score_cutoff_80pct_dev_only":threshold,
        "event_warning":"2025 macro event ledger incomplete: FOMC=0, NFP=11, CPI=10; the combined event head is UNAVAILABLE for entire 2025 and NOT deployable.",
        "2025_nominal_random_selection_hypergeom_p_6_of_7":nominal_p,
        "p_caution":"NOT confirmatory: exploratory protocol, archive already opened, serial correlation, multiple candidate variants.",
        "calendar_coverage_by_year":covered_year,
        "metrics":out.to_dict("records"),
        "extreme_2025":details,
        "next":"Freeze before newly unseen origins, assess source readiness and first executable bank quotes."
    }
    SUMMARY.write_text(json.dumps(result,indent=2,default=str)+"\n")
    print(out.to_string(index=False))
    print("Saved:", ROWS, METRICS, SUMMARY)

if __name__ == "__main__":
    main()
