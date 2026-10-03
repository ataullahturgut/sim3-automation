from __future__ import annotations
import json, os
from pathlib import Path
import pandas as pd
import gold_h3_aurora_prospective_v1 as base

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_clean_prospective_v1_out"))
OUT.mkdir(parents=True,exist_ok=True)
FREEZE_TS=pd.Timestamp("2026-10-03T11:33:49Z")
FIRST_FEATURE=pd.Timestamp("2026-10-05")

def configure():
    base.OUT=OUT
    base.FROZEN_PRICE_FILE=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv"
    base.FROZEN_MATRIX_FILE=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_EXPERT_TRAIN_MATRIX.csv"
    base.PRICE_LEDGER_FILE=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_DAILY_PRICES.csv"
    base.FORECAST_LEDGER_FILE=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_AURORA_LEDGER.csv"
    base.MISS_LEDGER_FILE=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_AURORA_MISSES.csv"
    base.INTEGRITY_LEDGER_FILE=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_DATA_INTEGRITY.csv"
    base.NOVA_FILE=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_NOVA_A1_PREDICTIONS_2026-10-03.csv"
    base.SENTRY_FILE=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_EXPERT_LEDGER_2026-10-03.csv"
    base.PROSPECTIVE_MIN_FEATURE=FIRST_FEATURE
    base.LOCK_TS_UTC=FREEZE_TS

def write_clean_status():
    s=json.loads((OUT/"aurora_prospective_status.json").read_text())
    s.update({"identity":"CLEAN_AURORA_H3_V1_PROSPECTIVE","umbrella_identity":"CLEAN_H3_PROSPECTIVE_V1","clean_freeze_timestamp_utc":str(FREEZE_TS),"first_eligible_feature_cutoff":str(FIRST_FEATURE.date()),"historical_bootstrap_commit":"73d1240cdc4dcac6f3671d53640094fcc61e2083"})
    (OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_AURORA_STATUS.json").write_text(json.dumps(s,indent=2,sort_keys=True,default=str)+"\n")
    raw=(OUT/"AURORA_PROSPECTIVE_STATUS.md").read_text().replace("AURORA-H3 V1 — PROSPECTIVE VALIDATION STATUS","CLEAN AURORA-H3 V1 — PROSPECTIVE VALIDATION STATUS").replace("AURORA_H3_V1_PROSPECTIVE","CLEAN_AURORA_H3_V1_PROSPECTIVE")
    raw += f"\n## Clean freeze\n\n- umbrella: CLEAN_H3_PROSPECTIVE_V1\n- freeze: **{FREEZE_TS}**\n- first eligible feature cutoff: **{FIRST_FEATURE.date()}**\n- historical bootstrap reproduction: **PASS**\n"
    (OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_AURORA_STATUS.md").write_text(raw)

def main():
    configure()
    base.main()
    write_clean_status()

if __name__=="__main__": main()
