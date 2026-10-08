"""Original PRAMV V1 architecture, Jan-Aug20 2026 restricted macro PIT candidate.

Exact prior-authored PSF M4 signature+FPCA code; frozen pre2026 same threshold,
two late halfhour reversal + same-day macro-pair veto, FOMC known future dates.
Macro consensus archived PIT vintage not independently proven; NOT production
nor intact original 2026-10-07 frozen study identity. Never no-event imputation.
"""
from __future__ import annotations
from pathlib import Path
import sys,os,json,time
import pandas as pd,numpy as np,psycopg
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_pramv_2021_2025_history_expansion_20261008 as legacy_macro
import gold_execution_psf_ovn_20261007 as psf
import gold_execution_2026_full_trajectory_cbr_20261008 as source
import gold_execution_pramv_repaired_full_retrain_20261008 as replay
NAME="GOLD_EXECUTION_2026_RESTRICTED_ORIGINAL_PRAMV_M4_RETEST_20261008"
SOURCE_QC=AX/"GOLD_EXECUTION_2026_PRAMV_MACRO_PIT_SOURCE_READINESS_20261008.json"
V2_2025=AX/"GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_GOVERNED_V2_20261008.csv"
EVENT_TYPES=legacy_macro.PAIRS
FED_JAN_AUG=["2026-01-28","2026-03-18","2026-04-29","2026-06-17","2026-07-29"]
SCOPE_START=pd.Timestamp("2026-01-01")
SCOPE_END=pd.Timestamp("2026-08-21")
def macro_2026():
    qc=json.loads(SOURCE_QC.read_text())
    series=[s for pair in EVENT_TYPES.values() for s in pair]
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=30) as cn:
      with cn.cursor() as c:
        c.execute("SET TRANSACTION READ ONLY")
        c.execute("""SELECT series_id,observation_ts,value,available_as_of,retrieved_at,lineage_id
             FROM observations WHERE series_id=ANY(%s)
             AND observation_ts >= '2026-01-01' AND observation_ts <'2026-08-21'
             ORDER BY series_id,observation_ts,retrieved_at""",(series,))
        rows=c.fetchall()
    raw=pd.DataFrame(rows,columns=["series_id","event_ts","value","available","retrieved","lineage"])
    for name in ("event_ts","available","retrieved"):
        raw[name]=pd.to_datetime(raw[name],utc=True,errors="coerce")
    results=[];gates={}
    for key,(act,exp) in EVENT_TYPES.items():
        a=raw[raw.series_id==act].sort_values("retrieved").drop_duplicates("event_ts",keep="last")
        e=raw[raw.series_id==exp].sort_values("retrieved").drop_duplicates("event_ts",keep="last")
        z=a.merge(e,on="event_ts",how="outer",indicator=True,suffixes=("_act","_exp"))
        if len(z)!=8 or (z._merge!="both").any() or z.value_act.isna().any() or z.value_exp.isna().any():
            raise RuntimeError("JAN_AUG_MACRO_EIGHT_RELEASE_PAIRS_NOT_CERTIFIED:"+key)
        for row in z.itertuples(index=False):
            if pd.isna(row.available_act) or pd.isna(row.available_exp):
                raise RuntimeError("MACRO_ASOF_MISSING_"+key)
            ready=max(row.available_act,row.available_exp)
            if ready < row.event_ts or ready>row.event_ts+pd.Timedelta(hours=1):
                raise RuntimeError("2026_MACRO_RELEASE_STAMP_NOT_READY:"+key)
            results.append({"event_type":key,"event_ts_utc":row.event_ts,
               "actual":float(row.value_act),"consensus":float(row.value_exp),
               "surprise":float(row.value_act-row.value_exp),
               "actual_available_as_of_utc":row.available_act,
               "consensus_available_as_of_utc":row.available_exp,
               "surprise_ready_at_utc":ready,"pair_complete":True,
               "actual_lineage_id":row.lineage_act,"consensus_lineage_id":row.lineage_exp,
               "pit_use":"2026_RETROSPECTIVE_CONSENSUS_ARCHIVAL_NOT_CERTIFIED"})
        gates[key]={"accepted_release_pairs":len(z),
             "macro_release_dates":sorted(z.event_ts.dt.date.astype(str).tolist())}
    existing=qc.get("source_series_receipts",{}).get("MACRO_EVENT_V3_FOMC_SCORE",{})
    if set(FED_JAN_AUG)!=set(existing.get("release_dates_UTC",[])):
        raise RuntimeError("FED_2026_5_SOURCE_NOT_MATCH_OFFICIAL_CALENDAR")
    for d in FED_JAN_AUG:
        event=pd.Timestamp(d).tz_localize("America/New_York")+pd.Timedelta(hours=14)
        event=event.tz_convert("UTC")
        results.append({"event_type":"FOMC","event_ts_utc":event,
            "actual":np.nan,"consensus":np.nan,"surprise":np.nan,
            "actual_available_as_of_utc":pd.NaT,
            "consensus_available_as_of_utc":pd.NaT,
            "surprise_ready_at_utc":pd.NaT,"pair_complete":False,
            "actual_lineage_id":"OFFICIAL_ADVANCE_SCHEDULE_FED_2026",
            "consensus_lineage_id":None,
            "pit_use":"SCHEDULE_ONLY_NO_FUTURE_SURPRISE"})
    gates["FOMC"]={"five_meetings":FED_JAN_AUG,"original_source_vintage_gap":"September missing; NOT in scope"}
    return pd.DataFrame(results),gates
