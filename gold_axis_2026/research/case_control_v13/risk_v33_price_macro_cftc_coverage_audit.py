#!/usr/bin/env python3
"""V33 audit exact latest data support, no synthetic future prices.

Measure true max input date for each of four metals, GVZ, USD H10,
Treasury rates and TWO CFTC contracts. Do not claim full 2026 scoring if
inputs are missing. This is a prerequisite to re-running risk models.
"""
import json
import pandas as pd
from pathlib import Path
import risk_v29_fourmetal_price_replay as v29
from risk_v31_macro_event_layer import events
O=Path(__file__).parent/"outputs"
END="2026-10-27"
D=O/"v33_staktrakr_4metals_2026_10_19_to_10_23_FIXED_COMMIT.csv"

def run():
    raw,cot,prior,panel,h=v29.historic_evidence()
    extra=pd.read_csv(D)
    assert len(extra)==20 and extra.date.nunique()==5 and set(extra.metal)=={"AU","AG","PT","PD"}
    old=pd.DataFrame([dict(date=r["date"],AU=r["metals"][0],AG=r["metals"][1],PT=r["metals"][2],PD=r["metals"][3]) for r in raw["prices"]])
    paired=extra.pivot(index="date",columns="metal",values="price_usd_oz")
    assert old.date.is_unique and paired.index.is_unique
    dates=pd.to_datetime(old.date)
    latest_input=dict(
        raw_prices_max=str(old.date.max()),
        original_price_source_rows=len(old),
        gvz_max=max(raw["gvz"]),
        dgs10_max=max(raw["macro"]["DGS10_FRB_H15"]),
        h10_usd_max=max(raw["macro"]["DTWEXBGS_FRB_H10"]),
        cftc_gc_latest_report=cot["GC"][-1]["date"],
        cftc_gc_latest_available=cot["GC"][-1]["available"],
        cftc_si_latest_report=cot["SI"][-1]["date"],
        cftc_si_latest_available=cot["SI"][-1]["available"],
        scored_model_max=str(max(x["origin"] for x in prior)),
        added_same_repo_metal_dates=paired.index.tolist(),
        discovered_weekday_source_price_max=str(paired.index.max()),
        user_requested_through=END,
        full_2026_history_available=False,
        keep_original_model_parameters=True,
        no_Neon_changes=True,
        snapshot_price_source_first_print_PIT_certified=False,
        additional_2026_events_after_2026_09_11_NOT_FOUND=True
    )
    check_dates=set(old.date)
    add=paired[~paired.index.isin(check_dates)]
    conflict=paired[paired.index.isin(check_dates)]
    for row in conflict.itertuples():
        v=old[old.date.eq(row.Index)].iloc[0]
        for met in ["AU","AG","PT","PD"]:
            assert abs(float(v[met])-float(getattr(row,met)))<1e-8
    full=pd.concat([old,pd.DataFrame([dict(date=str(day),AU=float(v.AU),AG=float(v.AG),PT=float(v.PT),PD=float(v.PD)) for day,v in add.iterrows()])],ignore_index=True)
    full=full.sort_values("date")
    assert full.date.is_unique and full.date.max()>="2026-10-23"
    full[full.date.between("2026-09-01",END)].to_csv(O/"v33_2026_09_10_same_source_fourmetal_coverage.csv",index=False)
    (O/"v33_max_input_date_gate.json").write_text(json.dumps(latest_input,indent=2)+"\n")
    print("V33_LAST_AVAILABLE_INPUTS",json.dumps(latest_input))
    print("V33_SOURCE_AUDIT_OK")
    return latest_input

if __name__=="__main__":run()
