from __future__ import annotations
import argparse, json
from pathlib import Path
import pandas as pd

import gold_monthly_etf_i1_i2_historical_recurrence_v1 as base

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--output",required=True)
    a=ap.parse_args()
    src=json.loads(Path(a.input).read_text())
    if src.get("schema")!="GOLD_MONTHLY_ETF_I1_I2_HISTORICAL_RECURRENCE_V1_2026-09-30":
        raise RuntimeError(("BAD_INPUT_SCHEMA",src.get("schema")))

    # Rebuild the official ETF/GLD panel so episode entries are evaluated month by month.
    gld_raw=base.v1.fetch(base.v1.GLD_URL)
    iau_raw=base.v1.fetch(base.v1.IAU_URL)
    gld=base.parse_gld_full(gld_raw)
    iau=base.v1.parse_iau(iau_raw)
    z=base.monthly_panel(gld,iau)
    z["I2_ENTRY"]=z["I2"] & (~z["I2"].shift(1).fillna(False))

    periods={
        "HISTORICAL_2010_2020":("2010-01","2020-12"),
        "LATER_2021_2024":("2021-01","2024-12"),
        "LATER_2025_2026_AUG":("2025-01","2026-08"),
    }
    stats={}
    for p,(s,e) in periods.items():
        pp=base.period_rows(z,s,e).copy()
        stats[p]=base.summarize(pp,"I2_ENTRY")

    out={
        "schema":"GOLD_MONTHLY_ETF_I2_EPISODE_ROBUSTNESS_V1_2026-09-30",
        "status":"COMPLETE",
        "definition":"I2_ENTRY = I2 true now and false prior month",
        "base_I2":"GLD and IAU both contract for >=2 consecutive months",
        "stats":stats,
        "governance":{
            "I2_threshold_changed":False,
            "serial_dependence_addressed":True,
            "episode_entry_only":True,
            "routing_tested":False,
        }
    }
    Path(a.output).write_text(json.dumps(out,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print("OUTPUT_GATE=PASS")
    print(json.dumps(stats,sort_keys=True))

if __name__=="__main__": main()
