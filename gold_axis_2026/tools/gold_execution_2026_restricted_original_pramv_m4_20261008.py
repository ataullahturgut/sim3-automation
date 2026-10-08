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

def report(qq,source_id,nt):
    d=qq.copy()
    def met(frame,pcol):
        if frame.empty:return {"n":0,"accuracy":None,"BA":None,"DOWN_recall":None,"UP_recall":None}
        y=frame.y.to_numpy(int);p=frame[pcol].to_numpy(int)
        down=y==0;up=y==1
        dn=float(np.mean(p[down]==0)) if down.any() else None
        ur=float(np.mean(p[up]==1)) if up.any() else None
        return {"n":len(frame),"accuracy":float(np.mean(p==y)),
            "BA":.5*(dn+ur) if dn is not None and ur is not None else None,
            "DOWN_recall":dn,"UP_recall":ur}
    r=d[d.rfr_cond]
    v1=d[d.PRAMV_active]
    m3=d[d.M3_priceonly_active]
    reject=r[~r.m4_agree | r.macro_veto]
    both=r[(r.m4_agree)&(~r.macro_veto)]
    correct=float(np.mean(reject.rfr_dir==reject.y)) if len(reject) else None
    return {"source_test":source_id,
      "period":"2026_JAN_TO_AUG20_RESTRICTED",
      "eligible_source_feature_n":len(d),"training_matured_pre_2026_n":nt,
      "same_day_macro_released_before_17_n":int(d.macro_veto.sum()),
      "rfr_reverse_n":len(r),"rfr_reverse_accuracy":met(r,"rfr_dir")["accuracy"],
      "m4_full_BA":met(d,"m4_dir")["BA"],
      "m4_full_Brier":float(np.mean((d.m4_prob-d.y)**2)),
      "m3_full_BA":met(d,"m3_dir")["BA"],
      "M3_confirm_n":len(m3),"M3_price_confirm_accuracy":met(m3,"rfr_dir")["accuracy"],
      "M3_price_confirm_BA":met(m3,"rfr_dir")["BA"],
      "full_rebuilt_PRAMV_active_n":len(v1),
      "full_rebuilt_PRAMV_coverage":len(v1)/len(d),
      "full_rebuilt_PRAMV_accuracy":met(v1,"rfr_dir")["accuracy"],
      "full_rebuilt_PRAMV_BA":met(v1,"rfr_dir")["BA"],
      "full_rebuilt_PRAMV_DOWN_recall":met(v1,"rfr_dir")["DOWN_recall"],
      "full_rebuilt_PRAMV_UP_recall":met(v1,"rfr_dir")["UP_recall"],
      "M4_rejected_RFR_n":len(reject),
      "M4_rejected_RFR_accuracy":correct,
      "M4_accepted_RFR_accuracy":met(both,"rfr_dir")["accuracy"],
      "PRAMV_signals_wrong_ge_1pct":int(np.sum(
          (v1.rfr_dir!=v1.y)&(v1.ret_OVN.abs()>=.01))),
      "PRAMV_idealized_two_sided_signed_log_sum_no_spread":float(np.sum(
        np.where(v1.rfr_dir==1,1,-1)*v1.ret_OVN.to_numpy(float))),
      "2026_pair_release_consensus_vintage_certified":False,
      "bank_trading_verified":False}

def main():
    tic=time.monotonic()
    calendar,meta=macro_and_history()
    q,t,sets=source.source_sets()
    reports=[];private=[]
    for label,px,tx in sets:
        qfull=pd.concat([q,px]).sort_index()
        if qfull.index.duplicated().any():raise RuntimeError("PROVIDER_DUPLICATED_QUOTES")
        targets=pd.concat([t,tx],ignore_index=True)
        if targets.date.duplicated().any():raise RuntimeError("DATE_MIXING")
        dataset=features(qfull,targets,calendar)
        scored,n_train=forecast_model(dataset)
        reports.append(report(scored,label,n_train))
        private.append(scored[["date","y","m3_prob","m4_prob","rfr_cond","rfr_dir",
                        "m4_agree","macro_veto","PRAMV_active","M3_priceonly_active",
                        "ret_OVN"]].assign(source_test=label))
        print("ORIGINAL_PRAMV_2026_PARTIAL",label,reports[-1],flush=True)
    out=pd.DataFrame(reports)
    stem=str(AX/NAME)
    out.to_csv(stem+"_METRICS.csv",index=False)
    pd.concat(private,ignore_index=True).to_csv(stem+"_DATED_PRIVATE.csv",index=False)
    state={"status":"ORIGINAL_ARCHITECTURE_M4_RFR_MACRO_RESTRICTED_2026_JAN_AUG_EXECUTED",
       "old_frozen_2026_10_07_PRAMV_V1_unchanged":True,
       "2026_status":"Retrospective quote-source restricted, macro release-era consensus vintage not independently certified",
       "training_2021_2025_macro":"private NEON/official 2025 complete; 2020 excluded",
       "2026_source_macro":"2026 Jan-Aug 8 CPI and 8 employment paired first prints; Fed 5 scheduled dates",
       "source_rows_mixed":False,
       "note":"2026 September/October macro M4 BLOCKED due Sept16 FOMC and Sept11 CPI missing",
       "training_no_2026_targets":True,
       "original_M4_original_PSFPCA_signature_code":True,
       "no_bank_executable_PnL":True,
       "no_untouched_2026_heldout_claim":True,
       "macro_event_source_quality":meta,
       "runtime_s":int(time.monotonic()-tic)}
    Path(stem+"_SUMMARY.json").write_text(json.dumps(state,indent=2,default=str)+"\n")
    print("FULL_SOURCE_RECONSTRUCTED_PRAMV_2026",out.to_string(index=False),flush=True)
    print("SOURCE_BOUNDED_PRAMV_STATE",json.dumps(state,default=str),flush=True)

if __name__=="__main__":
    try:main()
    except Exception as e:
        import traceback
        tb=traceback.extract_tb(e.__traceback__)[-1]
        state={"status":"2026_RESTRICTED_PRAMV_M4_MACRO_HARD_GATE_BLOCKED",
          "type":type(e).__name__,"reason":str(e)[:120],
          "function":tb.name,"line":tb.lineno,
          "no_2026_PRAMV_success_claim":True}
        (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(state,indent=2)+"\n")
        print("STRICT_MACRO_PRAMV_NO_SCORE",json.dumps(state),flush=True)
