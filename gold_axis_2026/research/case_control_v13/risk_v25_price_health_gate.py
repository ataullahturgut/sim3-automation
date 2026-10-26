#!/usr/bin/env python3
"""V25 fail-closed research price health gate: NO price mutation, NO live promotion.

Reads aggregate Neon SELECT evidence (not full copyrighted benchmark re-publication).
Source-level freshness or first-print PIT is NOT established by time-series smoothness.
"""
import argparse,json
from pathlib import Path
import pandas as pd
BASE=Path(__file__).parent
O=BASE/"outputs"

def verify():
    annual=pd.read_csv(O/"v25_independent_price_yearly_comparison.csv")
    discrep=pd.read_csv(O/"v25_independent_price_large_discrepancies.csv")
    anomalies=pd.read_csv(O/"v25_2026_fourmetal_confirmed_outlier.csv")
    impact=pd.read_csv(O/"v25_february_monthly_target_sensitivity.csv")
    price=pd.read_csv(O/"v23_price_calendar_RESEARCH_NOT_PIT.csv")
    partial=pd.read_csv(O/"v25_historical_partial_holiday.csv")
    manifest=json.loads((O/"v25_independent_price_comparison_manifest.json").read_text())
    expected={"AU":4041,"AG":4041,"PT":4040,"PD":4040}
    assert set(annual.metal)=={"AU","AG","PT"} and annual.year.nunique()==16
    for metal,n in expected.items():
        if metal!="PD":
            assert int(annual.loc[annual.metal.eq(metal),"db_days"].sum())==n
    assert int(annual.paired_with_external.sum())==11068
    assert int(annual.loc[annual.year.eq(2025),"paired_with_external"].sum())==0
    assert len(discrep)==49 and set(discrep.metal)=={"AU","AG","PT"}
    assert (discrep.difference_pct.abs()>5).all()
    assert manifest["uncovered_palladium"] and manifest["no_auto_substitution"]
    assert set(anomalies.metal)=={"AU","AG","PT","PD"}
    assert anomalies.date.eq("2026-02-27").all()
    assert anomalies.data_health_status.eq("REJECT_QUARANTINE").all()
    assert (anomalies.drop_prev_pct<-25).all()
    assert (anomalies.rebound_next_pct>40).all()
    assert set(impact.metal)=={"AU","AG","PT","PD"}
    assert (impact.change_if_excluded_usd_per_oz>0).all()
    assert not impact.exclude_is_corrected_target.any()
    assert price.date.eq("2026-02-27").sum()==1
    assert price.loc[price.date.eq("2026-02-27"),"quarantined"].iloc[0]
    assert abs(float(price.loc[price.date.eq("2026-02-27"),"price"].iloc[0])-3516.02)<.001
    assert partial.date.tolist()==["2021-12-24"]
    assert partial.missing_metals.tolist()==["PT|PD"]
    report={
       "project":"GOLD_CONTROL_V25_FOUR_METAL_DATA_HEALTH",
       "mode":"RESEARCH_ONLY",
       "source_daily_total_2010_2025":sum(expected.values()),
       "independent_compared_AU_AG_PT_days":int(annual.paired_with_external.sum()),
       "independent_compared_PD_days":0,
       "2025_external_comparison_days_in_this_dataset":0,
       "2026_all_four_external_daily_validation_complete":False,
       "comparisons_above_5pct_requiring_definition_review":len(discrep),
       "those_49_are_confirmed_errors":False,
       "known_bad_2026_02_27_metals":sorted(anomalies.metal.tolist()),
       "known_bad_day":str(anomalies.date.iloc[0]),
       "one_2021_partial_holiday_day":"2021-12-24",
       "all_four_metals_trading_day_intersection_is_required":True,
       "february_2026_target_is_contaminated":True,
       "march_2026_origin_features_may_be_contaminated":True,
       "monthly_H1_train_replay_safe":False,
       "large_drop_risk_model_replay_safe_to_certify":False,
       "source_definition_LBMA_AM_PM_vs_snapshot_harmonized":False,
       "PIT_gold_prices_verified":False,
       "PIT_CFTC_GVZ_macro_verified":False,
       "data_health_certified":False,
       "raw_Neon_modified":False,
       "old_monthly_forecast_records_modified":False,
       "further_action":"Reconcile official/independent source definitions, isolate February and downstream affected origins, obtain actual external checks for PD and 2025/2026, then audit-only rerun"
    }
    return report

def require_certified(result):
    """Call this before ANY claim of clean H1 training or live risk deployment."""
    if not result["data_health_certified"]:
        raise RuntimeError(
          "PRICE_HEALTH_BLOCKED_V25: QUARANTINED_2026_02_27_FOUR_METALS; "
          "PALLADIUM_AND_2025_2026_EXTERNAL_COVERAGE_MISSING; "
          "PRICE_DEFINITION_AND_PIT_UNVERIFIED. NO_TRAINING_OR_LIVE_PROMOTION.")
    return True

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--mode",choices=("report","certify"),default="report")
    args=parser.parse_args()
    result=verify()
    (O/"v25_price_health_gate_result.json").write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n")
    print("V25_PRICE_HEALTH",json.dumps(result,ensure_ascii=False))
    if args.mode=="certify":
        require_certified(result)

if __name__=="__main__":main()
