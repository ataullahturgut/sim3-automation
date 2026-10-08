"""2026-10-08 scientifically governed reproducibility on newly vetted XAU BID source.
Reruns EXISTING LIT Stage1 and Stage2 logistic and OLS implementations,
unmodified model specifications. 2020-22 warmup, prequential 2023-24 DEV,
fixed 2025 retrospective transport. Does NOT claim PRAMV/M4 re-training.
Existing 2023-2025 predictions in other families get label-transport AUDIT
only, and SESSION-horizon families are explicitly BLOCKED incompatible.
Never changes legacy original files or train on target period results.
"""
from __future__ import annotations
import os,json,sys,hashlib,time,glob
from pathlib import Path
from datetime import datetime,timezone
import numpy as np,pandas as pd,psycopg
from sklearn.metrics import confusion_matrix
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_lit_stage1_20261007 as l1
import gold_execution_lit_stage2_20261007 as l2
SOURCE="EVTRADINGLABS_DUKASCOPY_DERIVED_XAUUSD_M15_BIDASK_2020_2025_V1"
TABLE="gold_research_evduka_xau15m_bidask_candidate"
TARGET="gold_research_evduka_xau_session_target_candidate_v1"
OUT="GOLD_EXECUTION_2020_2025_SINGLE_MODELS_CLEAN_SOURCE_REPLAY_20261008"
OS=AX/(OUT+"_SUMMARY.json")
OM=AX/(OUT+"_METRICS.csv")
OI=AX/(OUT+"_INVENTORY.csv")
OT=AX/(OUT+"_SOURCE_TRANSPORT_METRICS.csv")
ROWS=AX/(OUT+"_EXACT_PREDICTIONS.csv")

def source_load():
    with psycopg.connect(os.environ["NEON_DATABASE_URL"],connect_timeout=20) as con:
        with con.cursor() as c:
            c.execute(f"""SELECT bar_start_utc,bid_open,bid_close FROM {TABLE}
              WHERE source_id=%s AND bar_start_utc>='2020-01-01' AND bar_start_utc<'2026-01-01'
              ORDER BY bar_start_utc""",(SOURCE,))
            bars=c.fetchall()
            c.execute(f"""SELECT issue_date,year,next_expected_date,day_y,overnight_y,
              day_bid_logret,overnight_bid_logret,day_gate,overnight_gate
              FROM {TARGET} WHERE source_id=%s ORDER BY issue_date""",(SOURCE,))
            labels=c.fetchall()
    q=pd.DataFrame(bars,columns=["ts","open","close"])
    q["ts"]=pd.to_datetime(q.ts,utc=True)
    if len(q)!=141890 or q.ts.duplicated().any():raise RuntimeError("FROZEN_SOURCE_ID_MISMATCH")
    t=pd.DataFrame(labels,columns=["date","year","next_date","y_DAY","y_OVN","ret_DAY","ret_OVN","day_gate","overnight_gate"])
    if len(t)!=1549 or t.date.duplicated().any():raise RuntimeError("LABEL_COVERAGE_IDENTITY_MISMATCH")
    t["date"]=pd.to_datetime(t.date)
    t["next_date"]=pd.to_datetime(t.next_date)
    for k in ["y_DAY","y_OVN","ret_DAY","ret_OVN"]: t[k]=pd.to_numeric(t[k],errors="coerce")
    q=q.set_index("ts")
    return q,t

def merge_truth(d,t):
    # Preserve original source-specific features; overwrite all outcome columns with
    # the independently verified (not recomputed by model) target PRICE SOURCE.
    d=d.drop(columns=[c for c in ["ret_DAY","y_DAY","ret_OVN","y_OVN","ret","y","next_date","year","day_gate","overnight_gate"] if c in d.columns],errors="ignore")
    d["date"]=pd.to_datetime(d.date)
    out=d.merge(t,on="date",how="inner",validate="one_to_one")
    if len(out)<1400:raise RuntimeError("NEW_SOURCE_FEATURE_DATE_COVERAGE_THIN")
    if "next_date" not in out:raise RuntimeError("NO_SOURCE_FROZEN_NEXT_DATE")
    if not ((out.loc[out.y_DAY.notna(),"day_gate"]=="COMPLETE_SINGLE_SOURCE").all() and
          (out.loc[out.y_OVN.notna(),"overnight_gate"]=="COMPLETE_SINGLE_SOURCE").all()):
        raise RuntimeError("INVALID_LABEL_GATE_DURING_REPLAY")
    return out

def score_df(d,model,year,pred,prob,target,origin,kind):
    if len(d)==0:return None
    y=d.actual_y.to_numpy(int) if "actual_y" in d else d.y.to_numpy(int)
    p=d[pred].to_numpy(int)
    tn,fp,fn,tp=map(int,confusion_matrix(y,p,labels=[0,1]).ravel())
    out={"model":model,"year":int(year),"kind":kind,"target":target,"origin":origin,
      "n":len(d),"accuracy":float((p==y).mean()),
      "balanced_accuracy":float(((tn/(tn+fp)) if tn+fp else np.nan)+
                                ((tp/(tp+fn)) if tp+fn else np.nan))/2,
      "up_recall":float(tp/(tp+fn)) if tp+fn else None,
      "down_recall":float(tn/(tn+fp)) if tn+fp else None,
      "tn":tn,"fp":fp,"fn":fn,"tp":tp,
      "pred_up_share":float(p.mean()),
      "scope":"DEVELOPMENT_HISTORY_EXAMINED" if year<2025 else "RETROSPECTIVE_2025_NOT_UNSEEN"}
    if prob and prob in d:
        pp=d[prob].to_numpy(float)
        out["brier"]=float(np.mean((pp-y)**2))
    return out

def derive_weekend(d):
    dow=pd.to_datetime(d["date"]).dt.dayofweek
    return np.where(dow==4,"FRI_TO_MON_64H","NEXT_WEEKDAY_16H")

def all_specs_retrain(q,t):
    z1=merge_truth(l1.build(q),t)
    # Delayed decision DAYD has distinct origin 09:30, not same 09:00 price
    z1["ret_DAYD"]=np.nan
    idx=q.index
    for i,r in z1.iterrows():
        if np.isfinite(r.ret_DAY):
            d=r.date.date()
            a=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=6,minutes=30)
            end=pd.Timestamp(d,tz="UTC")+pd.Timedelta(hours=13,minutes=45)
            if a in idx and end in idx:
                z1.at[i,"ret_DAYD"]=float(np.log(q.at[end,"close"]/q.at[a,"open"]))
    z1["y_DAYD"]=np.where(z1.ret_DAYD.notna(),(z1.ret_DAYD>0).astype(int),np.nan)
    outcomes=[]
    rows=[]
    specs={}
    for spec,(target,feat,fam) in l1.SPECS.items():
        # Legacy spec 09:30 is a different execution clock, never relabel as 09:00
        a=l1.predict(z1,spec,target,feat,fam)
        if a.empty:continue
        a["model_id"]=spec
        a["family"]="LIT_STAGE1"
        a["venue_scope"]=derive_weekend(a)
        a["target_new"]=target
        a["prediction_origin_TR"]="09:30" if target=="DAYD" else "09:00" if target=="DAY" else "17:00"
        a["old_source_imported_predictions"]=False
        rows.append(a)
        for (year,win),sub in a.groupby(["year","venue_scope"]):
            if target=="OVN" or win=="NEXT_WEEKDAY_16H":
                for model,pred,prob in [("LOGIT","pred_logit","p_logit"),("OLS_SIGN","pred_ols",None)]:
                    m=score_df(sub,spec+"/"+model,year,pred,prob,target,
                               a.prediction_origin_TR.iloc[0],"TRAINED_ON_NEW_SOURCE",None)
                    outcomes.append(m)
        specs[spec]={"kind":"ACTUAL_REFIT","architecture":"Original LIT Stage1 fixed specifications", "origin":"09:30 separate" if target=="DAYD" else "09:00" if target=="DAY" else "17:00"}
        print("TRAINED_LIT1",spec,len(a),flush=True)
    z2=merge_truth(l2.build(q),t)
    z2["ret"]=z2.ret_OVN
    z2["y"]=z2.y_OVN
    for spec,feat in l2.SPECS.items():
        a=l2.fit_predict(z2,spec,feat)
        if a.empty:continue
        a["model_id"]=spec
        a["family"]="LIT_STAGE2"
        a["venue_scope"]=derive_weekend(a)
        a["target_new"]="OVN"
        a["prediction_origin_TR"]="17:00"
        a["old_source_imported_predictions"]=False
        rows.append(a)
        for (year,win),sub in a.groupby(["year","venue_scope"]):
            for model,pred,prob in [("LOGIT","pred_logit","p"),("OLS_SIGN","pred_ols",None)]:
                outcomes.append(score_df(sub,spec+"/"+model,year,pred,prob,"OVN","17:00","TRAINED_ON_NEW_SOURCE"))
        specs[spec]={"kind":"ACTUAL_REFIT","architecture":"Original LIT Stage2 fixed state specification","origin":"17:00"}
        print("TRAINED_LIT2",spec,len(a),flush=True)
    predictions=pd.concat(rows,ignore_index=True,sort=False)
    predictions.to_csv(ROWS,index=False)
    return outcomes,specs,len(predictions)

# Archive-only model transport. Absolutely not a refit and not interchangeable
# with new-source-origin-generated feature forecasts.
ORIGINALS=[
("GOLD_EXECUTION_LIT_STAGE1_PREDICTIONS_2026-10-07.csv","spec","pred_logit","target"),
("GOLD_EXECUTION_LIT_STAGE2_PREDICTIONS_2026-10-07.csv","spec","pred_logit","OVN"),
("GOLD_EXECUTION_LIT_STAGE3_SELECTIVE_PREDICTIONS_2026-10-07.csv","policy","pred","OVN"),
("GOLD_EXECUTION_PSF_OVN_PREDICTIONS_2026-10-07.csv","family","pred","OVN"),
("GOLD_EXECUTION_MS_PSF_OVN_PREDICTIONS_2026-10-07.csv","family","pred","OVN"),
("GOLD_EXECUTION_FSMR_STAGE4_PREDICTIONS_2026-10-07.csv","model","pred","OVN"),
("GOLD_EXECUTION_PRAMV_GATE_ROWS_2026-10-07.csv","PRAMV_V1","gate_pred","OVN"),
("GOLD_EXECUTION_RFR_NOMACRO_ROWS_2026-10-07.csv","RFR_NOMACRO","rule_pred","OVN"),
("GOLD_EXECUTION_GVZ_SIGNED_TAIL_FULLWARMUP_PREDICTIONS_2026-10-08.csv","model","pred","OVN"),
]
def transport(t):
    seen={};metrics=[];inventory=[]
    lookup=t.set_index("date")
    for name,modelcol,pred,tspec in ORIGINALS:
        p=AX/name
        if not p.exists():
            inventory.append({"filename":name,"status":"NOT_AVAILABLE","reason":"archive file absent"})
            continue
        d=pd.read_csv(p,low_memory=False)
        if "date" not in d.columns or pred not in d.columns:
            inventory.append({"filename":name,"status":"NOT_COMPARABLE","reason":"no matching archived dated binary forecast column","columns":";".join(d.columns)})
            continue
        d["date"]=pd.to_datetime(d.date,errors="coerce")
        d=d[d.date.notna() & d.date.dt.year.isin([2023,2024,2025])].copy()
        if name.startswith("GOLD_EXECUTION_LIT_STAGE3_") and "active" in d.columns:
            d=d[d.active.astype(str).str.lower().eq("true")]
        if "eligible_nomacro" in d.columns:
            d=d[d.eligible_nomacro.astype(str).str.lower().eq("true")]
        if modelcol not in d.columns:
            d["model_name"]=modelcol
            modelcol="model_name"
        if tspec=="target" and "target" in d.columns:
            d["target_type"]=d.target.astype(str)
        else: d["target_type"]=tspec
        d=d[d.target_type.isin(["DAY","OVN","DAYD"])].copy()
        d[pred]=pd.to_numeric(d[pred],errors="coerce")
        d=d[d[pred].isin([0,1])]
        subcount=0
        for (mname,goal),z in d.groupby([modelcol,"target_type"]):
            if goal=="DAYD":
                inventory.append({"filename":name,"model":mname,"status":"SEPARATE_09_30_TARGET_NO_09_00_MATCH",
                     "reason":"09:30 origin target is not 09:00 target"})
                continue
            col="y_DAY" if goal=="DAY" else "y_OVN"
            n0=len(z)
            joined=z.merge(t[["date","year",col]],on="date",suffixes=("","_source"),how="inner")
            joined=joined[joined[col].notna()].copy()
            joined=joined.drop_duplicates("date")
            if joined.empty:continue
            source_mismatch=None
            if "y" in joined:
                old=pd.to_numeric(joined["y"],errors="coerce")
                source_mismatch=int(((old.notna())&(old.astype("Int64")!=joined[col].astype(int))).sum())
            elif "actual_y" in joined:
                old=pd.to_numeric(joined["actual_y"],errors="coerce")
                source_mismatch=int(((old.notna())&(old.astype("Int64")!=joined[col].astype(int))).sum())
            joined["actual_y"]=joined[col].astype(int)
            joined["p_for_score"]=joined[pred].astype(int)
            for year,gg in joined.groupby(joined.date.dt.year):
                s=score_df(gg,str(mname),year,"p_for_score",None,goal,
                     "09:00" if goal=="DAY" else "17:00","LEGACY_PREDICTION_TRANSFER_NOT_RETRAINED")
                s.update({"legacy_forecast_count":n0,"archived_label_source_mismatches":source_mismatch})
                metrics.append(s)
            inventory.append({"filename":name,"model":str(mname),"status":"LEGACY_PREDICTION_LABEL_TRANSFER_ONLY",
              "target":goal,"matched_source_dates":len(joined),
              "source_label_mismatches":source_mismatch,"reason":"Old archive prediction probabilities and old-source features unchanged; must NOT call retrained"})
            subcount+=1
        if subcount==0 and len(d):inventory.append({"filename":name,"status":"UNMATCHED","reason":"no scored binary common-source targets"})
    return metrics,inventory

def inventory_session(invent):
    for p in sorted(AX.glob("GOLD_SESSION_*_PREDICTIONS_*.csv")):
        invent.append({"filename":p.name,"status":"BLOCKED_DIFFERENT_TARGET",
          "reason":"WGC/Sobti ASIA/EU/US session target not 09:00-17:00 or 17:00-next09 execution label. Training on new target requires architecture-port, feature source/clock provenance and full PIT revalidation."})
    for name in ["PRAMV_V1","PSF_M4_SIG_FPCA_MACRO","RFR_MACRO_VETO",
                "GVZ_PIT_EVENT_RISK","HELIOS_SESSION_V1_V5","AURORA_SESSION","SENTRY_SESSION",
                "OPAL_SESSION","DART_SESSION","AIM_SESSION",
                "RTE_SESSION","ANFIS_SESSION"]:
        reason="2025 PIT FOMC/NFP/CPI ledger incomplete, macro at decision-hour not validated" if "MACRO" in name or name in ("PRAMV_V1","PSF_M4_SIG_FPCA_MACRO") else "Historical WGC/Sobti session target and/or 2020-25 input feature provenance not transportable to DAY/OVN without refitting exact architecture"
        invent.append({"filename":name,"model":name,"status":"ORIGINAL_SPEC_NOT_REFIT_YET",
          "reason":reason})
def main():
    start=time.time()
    q,t=source_load()
    r,models,predn=all_specs_retrain(q,t)
    old,inv=transport(t)
    inventory_session(inv)
    m=pd.DataFrame([x for x in r if x])
    m.to_csv(OM,index=False)
    pd.DataFrame(old).to_csv(OT,index=False)
    pd.DataFrame(inv).to_csv(OI,index=False)
    main_models=sorted(m.model.unique())
    summary={"status":"REPRODUCIBLE_SINGLE_MODELS_REPLAY_COMPLETE_WITH_EXPLICIT_BLOCKERS",
      "asof":"2026-10-08",
      "price_source":SOURCE,"quote_type":"BID_M15 for model features and target, ASK retained as uncertainty reference",
      "execution_origin":"Europe/Istanbul fixed 09:00, 17:00 (09:30 delayed challenger separately)",
      "historical_source_bars":len(q),"target_issue_dates":len(t),
      "training_role":"2020-2022 original 15m price features -> expanding prequential 2023/2024; train to 2024-12 and fix coefficients in 2025",
      "2025_caution":"Not untouched OOS: old forecast models and some variants were selected after inspecting 2025 elsewhere in project",
      "purged_matured_overnight_targets":True,"model_parameters": {"C":1.0,"solver":"original StandardScaler+L2 logistic","MIN_TRAIN":80},
      "frozen_pramv_v1_status":"NOT REFIT; macro PIT missing; legacy forecast transfer separately scored; frozen V1 not silently changed",
      "trained_model_architecture_count":len(models),
      "trained_binary_forecaster_count":len(main_models),
      "all_refit_prediction_records":predn,
      "transport_metric_rows":len(old),
      "session_models_retraining_status":"BLOCKED_DIFFERENT_TARGET until explicit original architecture feature-port with audited current origin",
      "files":{"actual_newsource_refit_metrics":OM.name,"legacy_forecast_source_transport_metrics":OT.name,
           "inventory":OI.name,"exact_new_source_preds":ROWS.name},
      "models":models,"elapsed_seconds":int(time.time()-start),"version":"V1_AUDITED"}
    OS.write_text(json.dumps(summary,indent=2)+"\n")
    print("REPLAY_TOTAL",json.dumps({k:summary[k] for k in ("trained_model_architecture_count","trained_binary_forecaster_count","all_refit_prediction_records","transport_metric_rows","elapsed_seconds")}),flush=True)
    print("LEADERBOARD")
    for (year,target),g in m[m.kind.eq("TRAINED_ON_NEW_SOURCE")].groupby(["year","target"]):
        w=g.sort_values("balanced_accuracy",ascending=False).head(4)
        print("TARGET_SCORES",year,target,w[["model","n","balanced_accuracy","down_recall","up_recall"]].to_json(orient="records"),flush=True)

if __name__=="__main__":main()
