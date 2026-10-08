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

def macro_and_history():
    raw=legacy_macro.conn_load()
    prev,history_qc=legacy_macro.raw_calendar(raw)
    official=pd.read_csv(V2_2025,low_memory=False)
    newer,new_qc=macro_2026()
    whole=pd.concat([prev,official,newer],ignore_index=True)
    for col in ("event_ts_utc","surprise_ready_at_utc",
                "actual_available_as_of_utc","consensus_available_as_of_utc"):
        whole[col]=pd.to_datetime(whole[col],utc=True,errors="coerce")
    if whole.duplicated(["event_type","event_ts_utc"]).any():
        raise RuntimeError("MACRO_MULTISOURCE_DUPLICATE_EVENT")
    whole=whole.sort_values("event_ts_utc")
    root=AX/"_PRIVATE_REPLAY_PRAMV_2026_MACRO"
    root.mkdir(exist_ok=True)
    macro_path=root/"composite_2021_2026_janaug.csv"
    whole.to_csv(macro_path,index=False)
    old=psf.MACRO
    try:
        psf.MACRO=macro_path
        full=psf.macro_table()
    finally:psf.MACRO=old
    return full,{"source_2021_2022":history_qc,"source_2026_Jan_Aug":new_qc}

def features(q,t,macro):
    orig=psf.build(q,macro)
    df=orig.drop(columns=[k for k in ("y","ret","ret_target","next_date","year","day_gate",
        "overnight_gate","y_OVN","ret_OVN") if k in orig.columns])
    labels=t[["date","year","next_date","ret_OVN","overnight_gate"]]
    df=df.merge(labels,on="date",validate="one_to_one")
    df=df[df.ret_OVN.notna() & df.overnight_gate.eq("COMPLETE_SINGLE_SOURCE")]
    df=df[df.date.dt.dayofweek<=3].copy()
    df["y"]=df.ret_OVN.gt(0).astype(int)
    # Do not treat the noncomparable December 18 2025 CPI statistic as a
    # source-ready comparable MoM surprise. It was pre-identified and excluded.
    exclude=set(replay.EXCLUDE)
    df=df[~df.date.dt.strftime("%Y-%m-%d").isin(exclude)]
    df=df[df.year>=2021].copy()
    cols=[x for x in psf.FAMILIES["M4_SIG_FPCA_MACRO"]
        if x not in ("pc1","pc2")]+psf.PATHCOLS
    df=df.dropna(subset=cols).sort_values("date")
    if df.duplicated("date").any():raise RuntimeError("DUPLICATE_PRAMV_EVENT_ISSUE")
    return df

def forecast_model(df):
    tr=df[(df.date<SCOPE_START)&(df.next_date<=SCOPE_START)]
    te=df[(df.date>=SCOPE_START)&(df.date<SCOPE_END)]
    if len(tr)<600 or len(te)<50:raise RuntimeError("M4_TRAIN_OR_2026_TEST_SOURCE_INCOMPLETE")
    if not (tr.year<=2025).all() or not (te.year==2026).all():
        raise RuntimeError("2026_MACRO_FIT_DATE_FORBIDDEN")
    if te.macro_released.isna().any() or te.upcoming_fomc.isna().any():
        raise RuntimeError("UNRESOLVED_2026_RELEASE_STATE")
    original=psf.FAMILIES
    try:
        psf.FAMILIES={n:original[n] for n in ("M3_SIG_FPCA","M4_SIG_FPCA_MACRO")}
        scores=psf.frozen_models(tr,te)
    finally:psf.FAMILIES=original
    te=te.copy()
    te["m3_prob"]=scores["M3_SIG_FPCA"]
    te["m4_prob"]=scores["M4_SIG_FPCA_MACRO"]
    te["rfr_cond"]=(np.sign(te.r1600_1630)!=np.sign(te.r1630_1700))&(
        te.r1600_1630.ne(0)&te.r1630_1700.ne(0))
    te["rfr_dir"]=te.r1600_1630.gt(0).astype(int)
    te["m3_dir"]=te.m3_prob.ge(.5).astype(int)
    te["m4_dir"]=te.m4_prob.ge(.5).astype(int)
    te["macro_veto"]=te.macro_released.eq(1)
    te["m4_agree"]=te.rfr_dir.eq(te.m4_dir)
    te["m3_agree"]=te.rfr_dir.eq(te.m3_dir)
    te["PRAMV_active"]=te.rfr_cond & te.m4_agree & ~te.macro_veto
    te["M3_priceonly_active"]=te.rfr_cond & te.m3_agree
    return te,len(tr)
