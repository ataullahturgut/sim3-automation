"""PRAMV original frozen rule: full ARCHITECTURE recreation on restored 2025
Fed statement schedule and uniform 2020-25 XAU BID 15m target source.

2023/24 historical events & pair surprise sourced in legacy ledger
(available-as-of assertions originally reconstructed in 2026 -- explicit
historical vintage caveat); 2025 eight FOMC dates from official Fed prior
2024 calendar; 2025-12-18 BLS 2-month CPI non-comparable and excluded.
M4 PCA/signature/price/non-macro features and original fixed hyperparameters,
RFR reversal-first-impulse and 17:00 publication/veto unchanged. Full new
source label and original paired baseline re-fit, no 2025 tuning.
Cannot train 2020-2022 M4 without contemporaneously verified macro calendar;
never replace missing macro with zero. Thus train 2023-24, and 2025 frozen.
"""
from pathlib import Path
import os,sys,json,hashlib,time
from datetime import datetime,timezone
import numpy as np,pandas as pd
from sklearn.metrics import confusion_matrix
from scipy.stats import binomtest

AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/'tools'))
import gold_execution_psf_ovn_20261007 as psf
import gold_execution_lit_stage3_selective_20261007 as l3
import gold_execution_2020_2025_all_existing_model_replay_20261008 as c
CAL=AX/'GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_GOVERNED_V2_20261008.csv'
AUDIT=AX/'GOLD_EXECUTION_PRAMV_OFFICIAL_2025_MACRO_SOURCE_QC_20261008.json'
BASE='GOLD_EXECUTION_PRAMV_V1_MACRO_REPAIRED_CLEAN_SOURCE_FULL_RERUN_20261008'
OUT=AX/(BASE+'_SUMMARY.json')
MET=AX/(BASE+'_YEARLY_METRICS.csv')
PRED=AX/(BASE+'_DATED_PREDICTIONS.csv')
CHECK=AX/(BASE+'_FOMC_ABLATION.csv')
M4="M4_SIG_FPCA_MACRO"
OLDMACRO=AX/'GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv'
EXCLUDE=set(["2025-12-18"])
def mkt_q():
    q,t=c.source_load()
    # Avoid silent 2020-22 missing macro histories being treated as 'no event'.
    q=q[q.index>=pd.Timestamp("2023-01-01",tz="UTC")]
    return q,t
def merged_feature(q,t,m):
    d=c.merge_truth(psf.build(q,m),t)
    d["y"]=d.y_OVN
    d["ret_target"]=d.ret_OVN
    d=d[(d.y.notna())&(~d.date.dt.strftime('%Y-%m-%d').isin(EXCLUDE))].copy()
    required=[x for x in psf.FAMILIES[M4] if x not in ('pc1','pc2')]+psf.PATHCOLS
    d=d.dropna(subset=required)
    if not d.next_date.gt(d.date).all():raise RuntimeError("NEXT_DATE_NOT_AHEAD")
    if not (d.overnight_gate=="COMPLETE_SINGLE_SOURCE").all():
        raise RuntimeError("UNAPPROVED_SOURCE_OVERNIGHT")
    return d.sort_values("date").reset_index(drop=True)

def probabilities(d):
    out=[]
    for row in d[d.year.isin([2023,2024])].itertuples(index=False):
        current=d[d.date.eq(row.date)].iloc[0]
        hist=d[(d.date<row.date)&(d.next_date<=row.date)]
        if len(hist)<psf.MIN_TRAIN or hist.y.nunique()<2:continue
        p=psf.fit_family(hist,current,M4)
        out.append({"date":row.date,"year":row.year,"m4_p_up":p,
           "m4_pred":int(p>=.5),"training_n":len(hist),"period":"EXPANDING_2023_2024",
           "macro_released":int(row.macro_released),
           "upcoming_fomc":int(row.upcoming_fomc),
           "y":int(row.y)})
    frozen=d[(d.year<=2024)&(d.next_date<=pd.Timestamp('2025-01-01'))]
    test=d[d.year==2025]
    if len(frozen)<300:raise RuntimeError("2023_24_FROZEN_HISTORY_TOO_SMALL")
    if len(test)<200:raise RuntimeError("NEW_SOURCE_2025_COVERAGE_TOO_THIN")
    pca_features=psf.FAMILIES
    try:
        psf.FAMILIES={M4:pca_features[M4]}
        pp=psf.frozen_models(frozen,test)[M4]
    finally:psf.FAMILIES=pca_features
    for row,p in zip(test.itertuples(index=False),pp):
        out.append({"date":row.date,"year":int(row.year),"m4_p_up":float(p),
             "m4_pred":int(p>=.5),"training_n":len(frozen),
             "period":"FROZEN_2025_RETROSPECTIVE",
             "macro_released":int(row.macro_released),
             "upcoming_fomc":int(row.upcoming_fomc),
             "y":int(row.y)})
    return pd.DataFrame(out).sort_values("date").reset_index(drop=True)

def pair_model(q,t,macro):
    x=c.merge_truth(l3.build(q,macro),t)
    x["y"]=x.y_OVN
    x["ret"]=x.ret_OVN
    x=x[x.y.notna() & ~x.date.dt.strftime('%Y-%m-%d').isin(EXCLUDE)].copy()
    out=l3.pair_predictions(x)
    if out.empty:raise RuntimeError("PAIR_REPLAY_EMPTY")
    return out[["date","pred_pair","p_pair","r16","r1630","year"]].drop_duplicates("date")

def summarize(x,den):
    if len(x)==0:return {"n":0,"coverage":0}
    y=x.y.to_numpy(dtype=int);p=x.rfr_pred.to_numpy(dtype=int)
    b=x.pair_pred.to_numpy(dtype=int)
    tn,fp,fn,tp=map(int,confusion_matrix(y,p,labels=[0,1]).ravel())
    tpr=tp/(tp+fn) if tp+fn else None
    tnr=tn/(tn+fp) if tn+fp else None
    ok=p==y;bk=b==y
    rescue=int((ok&~bk).sum());broken=int((~ok&bk).sum())
    return {
      "n":len(x),"coverage":len(x)/den,"accuracy":float(ok.mean()),
      "balanced_accuracy":float((tpr+tnr)/2) if tpr is not None and tnr is not None else None,
      "up_recall":tpr,"down_recall":tnr,
      "tn":tn,"fp":fp,"fn":fn,"tp":tp,
      "pred_up_share":float(np.mean(p)),
      "pair_same_n":len(x),"pair_accuracy":float(bk.mean()),
      "pair_balanced_accuracy":float(((np.mean(b[y==1]==1)+np.mean(b[y==0]==0))/2))
                 if len(set(y))==2 else None,
      "rescued":rescue,"broken":broken,"net_rescued":rescue-broken,
      "mcnemar_exact_p":float(binomtest(rescue,rescue+broken,.5).pvalue)
              if rescue+broken else 1.,
      "one_sided_binomial_vs_50_p":float(binomtest(int(ok.sum()),len(x),.5,alternative="greater").pvalue)
    }
def execute_gate(m4,pair,eligible):
    q=m4.merge(pair,on=["date","year"],how="inner",validate="one_to_one")
    q=q.merge(eligible[["date","year","overnight_span_type"]],on=["date","year"],
             how="inner",validate="one_to_one")
    if (q.year<=2024).sum()<300 or (q.year==2025).sum()<200:
        raise RuntimeError("GATE_OUTER_COVERAGE_LOST")
    q["prior_halfhour_sign_opposed"]=(np.sign(q.r16)!=np.sign(q.r1630))&(
      q.r16.notna()&q.r1630.notna()&(q.r16!=0)&(q.r1630!=0))
    q["rfr_pred"]=(q.r16>0).astype(int)
    q["macro_veto"]=(q.macro_released==1)
    q["agreement"]=q.rfr_pred.eq(q.m4_pred)
    q["active"]=(~q.macro_veto)&q.prior_halfhour_sign_opposed&q.agreement
    q["hold_type"]=np.where(pd.to_datetime(q.date).dt.dayofweek==4,"FRI_TO_MON_64H","REGULAR_16H")
    q["gate_pred"]=q.rfr_pred.where(q.active)
    q["pair_pred"]=q.pred_pair.astype(int)
    q["correct"]=np.where(q.active,q.rfr_pred.eq(q.y),False)
    assert q.loc[q.active,"rfr_pred"].eq(q.loc[q.active,"m4_pred"]).all()
    assert not q.loc[q.active,"macro_veto"].any()
    return q

def main():
    started=time.monotonic()
    a=json.loads(AUDIT.read_text())
    if a['status']!='OFFICIAL_2025_EVENT_CALENDAR_REPAIRED_WITH_RESTRICTED_SURPRISE_VINTAGE':
        raise RuntimeError("REPAIRED_MACRO_NOT_ACCEPTED")
    if a['2025_fomc_inserted']!=8:raise RuntimeError("OFFICIAL_FOMC_INCOMPLETE")
    psf.MACRO=CAL
    q,t=mkt_q()
    m=psf.macro_table()
    m_old=pd.read_csv(OLDMACRO)
    # Guard: critical CPI Dec 18 is an unknown monthly surprise, not an event-free day.
    exception=m[(m.event_ts_utc.dt.date==pd.Timestamp('2025-12-18').date())&
        (m.event_type=='CPI')]
    if len(exception)!=1 or exception.surprise_ready_at_utc.notna().any():
        raise RuntimeError("CPI_UNPAIRED_LEAKAGE")
    if not (m[(m.event_type=='FOMC')&(m.event_ts_utc.dt.year==2025)].shape[0]==8):
        raise RuntimeError("FOMC_NOT_READY")
    d=merged_feature(q,t,m)
    predictions=probabilities(d)
    pair=pair_model(q,t,m)
    eligible=d[["date","year"]].copy()
    eligible["overnight_span_type"]=np.where(eligible.date.dt.dayofweek==4,
              "FRI_TO_MON_64H","REGULAR_16H")
    g=execute_gate(predictions,pair,eligible)
    # label equality exact same new-source y for all paired fitted streams
    assert g.y.notna().all()
    rows=[]
    for year in [2023,2024,2025]:
        n=int(((t.year==year)&t.y_OVN.notna()&
          ~t.date.dt.strftime("%Y-%m-%d").isin(EXCLUDE)).sum())
        base=g[g.year==year]
        for scope,ds in [("ALL",base),("REGULAR_16H",base[base.hold_type=="REGULAR_16H"]),
                   ("FRI_TO_MON_64H",base[base.hold_type=="FRI_TO_MON_64H"])]:
            den=n if scope=="ALL" else int(((t.year==year)&t.y_OVN.notna()&
              ((t.date.dt.dayofweek==4) if scope=="FRI_TO_MON_64H" else
               (t.date.dt.dayofweek!=4))&
               ~t.date.dt.strftime("%Y-%m-%d").isin(EXCLUDE)).sum())
            z=ds[ds.active]
            r=summarize(z,den)
            r.update({'year':year,'scope':scope,'original_price_complete_target_dates':den,
              'm4_model_predicted_dates':len(ds),'veto_n':int(ds.macro_veto.sum()),
              'fomc_upcoming_origin_n':int(ds.upcoming_fomc.sum()),
              'reversal_precondition_n':int(ds.prior_halfhour_sign_opposed.sum()),
              'agreement_n':int(ds.agreement.sum())})
            rows.append(r)
    M=pd.DataFrame(rows)
    g["date"]=pd.to_datetime(g.date).dt.strftime("%Y-%m-%d")
    # Only dated binary source-based projections, no raw raw data / prices.
    g.to_csv(PRED,index=False)
    M.to_csv(MET,index=False)
    # Historical missing-FOMC 2025 is a strict ablation: rerun identical source,
    # identical trained 2023-24 coefficients, just omit eight future Fed dates.
    old=pd.read_csv(OLDMACRO)
    old["event_ts_utc"]=pd.to_datetime(old.event_ts_utc,utc=True)
    psf.MACRO=OLDMACRO
    mo=psf.macro_table()
    old_feat=merged_feature(q,t,mo)
    tr=d[(d.year<=2024)&(d.next_date<=pd.Timestamp('2025-01-01'))]
    te=old_feat[old_feat.year==2025].copy()
    old_families=psf.FAMILIES
    try:
        psf.FAMILIES={M4:old_families[M4]}
        oldp=psf.frozen_models(tr,te)[M4]
    finally:psf.FAMILIES=old_families
    abl=te[["date","upcoming_fomc"]].copy()
    abl["base_m4_up_prob"]=oldp
    abl["base_m4_direction"]=(oldp>=.5).astype(int)
    abl=abl.merge(predictions[predictions.year==2025][["date","m4_p_up","m4_pred","upcoming_fomc"]],
                   on="date",validate="one_to_one",suffixes=("_before","_repaired"))
    abl["m4_direction_changed"]=abl.base_m4_direction!=abl.m4_pred
    abl["new_calendar_changes_upcoming"]=abl.upcoming_fomc_before!=abl.upcoming_fomc_repaired
    abl.to_csv(CHECK,index=False)
    totals={
      "status":"PRAMV_ORIGINAL_RULE_M4_RFR_MACRO_VETO_COMPLETED_RESTRICTED_HISTORICAL_REPLAY",
      "asof":"2026-10-08","price_source":c.SOURCE,
      "macro_event_calendar":CAL.name,
      "macro_event_calendar_sha256":a["calendar_sha256"],
      "source_window":"2020–2025 BID archive; M4 requires macro inputs so exact M4 fitting/label scoring limited 2023–2025; 2020–22 NEVER imputed no-news",
      "original_method_identity":"Frozen M4 Signature+FPCA+PIT-claimed macro; 16-16:30 impulse vs 16:30-17 reversal; released paired surprise veto; agreement; 0.5 logistic threshold; C=1.",
      "changed_original_thresholds":False,
      "method_created_from_scratch":False,
      "original_frozen_PRAMV_V1_overwritten":False,
      "claim_original_frozen_model_identical":False,
      "reason_retraining_not_identical":"Original training sample/market vendor changed and 2020–22 macro proof unavailable; this is PRAMV-V1-architecture new-source research replay, not an untouched frozen V1 prospective test.",
      "training_2023":"Original expanding PIT-matured history, >=120 old labeled rows before decision",
      "training_2024":"Original expanding PIT-matured history",
      "training_2025":"2023/2024 trained freeze; no future 2025 targets in 2025 fit",
      "macro_vintage_warning":a['consensus_pit_caution'],
      "2025_cpi_dec18":"not comparable MoM, excluded rather than falsely treating no macro release or inventing a surprise",
      "2025_fomc_eight_from_2024_prior_calendar":True,
      "2025_previous_missing_calendar_issue_dates_changed":int(abl.new_calendar_changes_upcoming.sum()),
      "2025_m4_directions_changed_by_fomc_repair":int(abl.m4_direction_changed.sum()),
      "overlap_model_dates":len(g),
      "gate_total_active":int(g.active.sum()),
      "m4_train_history_from_2020_22":False,
      "not_bank_executable":True,
      "not_untouched_2025_oos":True,
      "Friday_64h_metrics_separate":True,
      "model_metrics_file":MET.name,
      "dated_model_predictions_file":PRED.name,
      "fomc_ablation_file":CHECK.name,
      "full_pramv_workflow_valid_for_restricted_retrospective":True,
      "elapsed_sec":int(time.monotonic()-started)}
    OUT.write_text(json.dumps(totals,indent=2)+"\n")
    print("PRAMV_FULL_MODEL_RESULT",json.dumps(totals,indent=2),flush=True)
    print("PRAMV_YEARLY_METRICS",M.to_string(index=False),flush=True)
if __name__=='__main__':main()
