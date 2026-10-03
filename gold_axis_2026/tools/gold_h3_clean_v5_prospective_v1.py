from __future__ import annotations
import json, math, os, tempfile
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import balanced_accuracy_score, log_loss, recall_score
import gold_h3_aurora_prospective_v1 as apro
import gold_h3_iris_v1 as iris
import gold_h3_rift_v1 as rift
import gold_h3_turn_v1 as turn
import gold_h3_vega_v1 as vega
import gold_h3_opal_v1 as opal
import gold_h3_helios_v1 as h1
import gold_h3_helios_v2 as h2
import gold_h3_helios_v3_gt as h3
import gold_h3_helios_v4_rge as h4
import gold_h3_helios_v5_dce as h5

ROOT=Path(__file__).resolve().parents[2]
OUT=Path(os.environ.get("OUT_DIR","gold_h3_clean_prospective_v1_out")); OUT.mkdir(parents=True,exist_ok=True)
FIRST_FEATURE=pd.Timestamp("2026-10-05"); FREEZE_TS=pd.Timestamp("2026-10-03T11:33:49Z")
HIST_AURORA=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_AURORA_PREDICTIONS_2026-10-03.csv"
HIST_V5=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
FROZEN_RIFT_PANEL=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
FROZEN_VEGA_PANEL=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_VEGA_PANEL.csv"
FROZEN_OPAL_PANEL=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv"
AURORA_LEDGER=OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_AURORA_LEDGER.csv"
V5_LEDGER=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_V5_LEDGER.csv"
V5_MISSES=ROOT/"gold_axis_2026"/"GOLD_H3_CLEAN_PROSPECTIVE_V1_V5_MISSES.csv"
V5_COLS=["feature_cutoff_date","issued_at_utc","planned_forecast_issue_date","p_clean_aurora","aurora_direction","p_clean_v5","v5_direction","changed_from_aurora","active_expert","prob_path_superior","gate_active","candidate_reversal","opal_override","p_opal_reversal","cot_report_date","cot_available_date","gt_flip_share","v4_route","rge_active","dce_exception","settlement_status","target_end_date_h3","target_r3","y_up","aurora_correct","v5_correct","v5_brier_row","v5_logloss_row","settled_at_utc"]
MISS_COLS=["feature_cutoff_date","planned_forecast_issue_date","deadline_utc","recorded_at_utc","reason"]

def now_utc():
    x=os.environ.get("CLEAN_H3_NOW_UTC","").strip()
    return pd.Timestamp(x).tz_convert("UTC") if x else pd.Timestamp.now(tz="UTC")

def read_dates(path):
    x=pd.read_csv(path)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3","planned_forecast_issue_date"]:
        if c in x.columns: x[c]=pd.to_datetime(x[c],errors="coerce")
    return x

def synthetic_aurora(a):
    h=read_dates(HIST_AURORA); rows=[]
    for r in a.itertuples(index=False):
        d=pd.Timestamp(r.feature_cutoff_date); settled=str(r.settlement_status)=="SETTLED"
        issue=pd.Timestamp(r.planned_forecast_issue_date)
        rows.append({"feature_cutoff_date":d,"forecast_issue_date":issue,"target_end_date_h3":pd.Timestamp(r.target_end_date_h3) if settled and pd.notna(r.target_end_date_h3) else d+pd.Timedelta(days=3650),"year":int(issue.year),"month":str(issue.to_period("M")),"y_up":int(r.y_up) if settled and pd.notna(r.y_up) else 0,"target_r3":float(r.target_r3) if settled and pd.notna(r.target_r3) else 0.0,"p_structural":float(r.p_structural),"p_path_global":float(r.p_path_global),"p_sentry":float(r.p_structural),"p_dart":float(r.p_aurora),"p_aurora":float(r.p_aurora),"active_expert":str(r.active_expert),"matured_pair_n":int(r.matured_pair_n),"net_rescue_63":int(r.net_rescue_63),"matured_disagreements":int(r.matured_disagreements),"q_path":float(r.q_path),"prob_path_superior":float(r.prob_path_superior)})
    if rows: h=pd.concat([h,pd.DataFrame(rows)],ignore_index=True,sort=False)
    return h.sort_values("forecast_issue_date").drop_duplicates("forecast_issue_date",keep="last").reset_index(drop=True)

def cache_hourly():
    hist=iris.load_neon_hourly(); succ,n=iris.fetch_extension(); _,br=iris.bridge_metrics(hist,succ)
    if not br["pass"]: raise RuntimeError(f"CLEAN_V5_HOURLY_BRIDGE_FAIL {br}")
    iris.load_neon_hourly=lambda:hist.copy(); iris.fetch_extension=lambda:(succ.copy(),n)

def extend(fpath,g,last):
    f=read_dates(fpath); g=g[g.forecast_issue_date>last].copy()
    if "month_key" not in f.columns:f["month_key"]=f.forecast_issue_date.dt.to_period("M").astype(str)
    if "month_key" not in g.columns:g["month_key"]=g.forecast_issue_date.dt.to_period("M").astype(str)
    cols=sorted(set(f.columns)|set(g.columns))
    for c in cols:
        if c not in f.columns:f[c]=np.nan
        if c not in g.columns:g[c]=np.nan
    return pd.concat([f[cols],g[cols]],ignore_index=True).sort_values("forecast_issue_date").reset_index(drop=True)

def temp(df,td,name):
    p=Path(td)/name; df.to_csv(p,index=False); return p

def chain(a):
    syn=synthetic_aurora(a); last=pd.to_datetime(pd.read_csv(HIST_AURORA,usecols=["forecast_issue_date"]).forecast_issue_date).max()
    with tempfile.TemporaryDirectory() as td:
        af=temp(syn,td,"a.csv"); cache_hourly()
        rift.AURORA=af; rp,_,_=rift.load_panel(); rf=temp(rift.run_rift(extend(FROZEN_RIFT_PANEL,rp,last)),td,"r.csv")
        turn.AURORA=af; tp,_,_=turn.apply_turn(); tf=temp(tp,td,"t.csv")
        vega.AURORA=af; vp,_,_,_=vega.load_panel(); vf=temp(vega.run_vega(extend(FROZEN_VEGA_PANEL,vp,last)),td,"v.csv")
        opal.AURORA=af; op,_,_,_,_=opal.load_panel(); of=temp(opal.run_opal(extend(FROZEN_OPAL_PANEL,op,last)),td,"o.csv")
        h1.AURORA=af;h1.RIFT=rf;h1.TURN=tf;h1.VEGA=vf;h1.OPAL=of
        g1,_=h1.build_ledger(); f1=temp(g1,td,"h1.csv"); h2.V1=f1
        g2=h2.build_v2(); f2=temp(g2,td,"h2.csv")
        h3.H1=f1;h3.H2=f2;h3.OPAL=of; b3=h3.load_base(); g3=h3.simulate_market(b3); f3=temp(g3,td,"h3.csv")
        h4.V3=f3; b4=h4.attach_v3(b3); g4,_=h4.simulate_rge(b4); g5=h5.apply_dce(g4)
    ref=read_dates(HIST_V5); chk=g5[g5.forecast_issue_date<=last].merge(ref[["forecast_issue_date","p_helios_v5_dce"]],on="forecast_issue_date",suffixes=("_new","_ref"),validate="one_to_one")
    if len(chk)!=len(ref):raise RuntimeError(f"CLEAN_V5_HISTORY_MATCH_FAIL {len(chk)} {len(ref)}")
    md=float(np.max(np.abs(chk.p_helios_v5_dce_new-chk.p_helios_v5_dce_ref)))
    if md>1e-10:raise RuntimeError(f"CLEAN_V5_HISTORY_REPRO_DIFF {md}")
    return g5,md

def read_v5():
    if not V5_LEDGER.exists():return pd.DataFrame(columns=V5_COLS)
    return read_dates(V5_LEDGER)

def read_miss():
    if not V5_MISSES.exists():return pd.DataFrame(columns=MISS_COLS)
    return read_dates(V5_MISSES)

def settle(v,a,ts):
    amap={pd.Timestamp(r.feature_cutoff_date):r for r in a.itertuples(index=False)}; n=0
    for i,r in v.iterrows():
        if str(r.get("settlement_status",""))=="SETTLED":continue
        ar=amap.get(pd.Timestamp(r.feature_cutoff_date))
        if ar is None or str(ar.settlement_status)!="SETTLED":continue
        y=int(ar.y_up);p=float(r.p_clean_v5);pa=float(r.p_clean_aurora);pc=float(np.clip(p,1e-6,1-1e-6))
        v.loc[i,["settlement_status","target_end_date_h3","target_r3","y_up","aurora_correct","v5_correct","v5_brier_row","v5_logloss_row","settled_at_utc"]]=["SETTLED",ar.target_end_date_h3,float(ar.target_r3),y,int((pa>=.5)==bool(y)),int((p>=.5)==bool(y)),(p-y)**2,-(y*math.log(pc)+(1-y)*math.log(1-pc)),ts.isoformat()];n+=1
    return v,n

def met(v,col):
    z=v[v.settlement_status=="SETTLED"]
    if z.empty:return {"n":0}
    y=z.y_up.astype(int).to_numpy();p=z[col].astype(float).to_numpy();d=(p>=.5).astype(int)
    return {"n":len(z),"accuracy":float(np.mean(d==y)),"balanced_accuracy":float(balanced_accuracy_score(y,d)) if len(np.unique(y))==2 else None,"brier":float(np.mean((p-y)**2)),"logloss":float(log_loss(y,np.clip(p,1e-6,1-1e-6),labels=[0,1])),"up_recall":float(recall_score(y,d,pos_label=1,zero_division=0)),"down_recall":float(recall_score(y,d,pos_label=0,zero_division=0))}

def main():
    ts=now_utc(); a=read_dates(AURORA_LEDGER); v=read_v5(); miss=read_miss(); v,settled=settle(v,a,ts)\n    if a.empty:\n        g=pd.DataFrame(); md=0.0\n    else:\n        g,md=chain(a)
    existing=set(pd.to_datetime(v.feature_cutoff_date,errors="coerce").dropna().dt.normalize()) if len(v) else set(); missed=set(pd.to_datetime(miss.feature_cutoff_date,errors="coerce").dropna().dt.normalize()) if len(miss) else set(); issued=0
    for ar in a.sort_values("feature_cutoff_date").itertuples(index=False):
        d=pd.Timestamp(ar.feature_cutoff_date).normalize()
        if d<FIRST_FEATURE or d in existing or d in missed:continue
        deadline,issue=apro.deadline_utc(d)
        if ts>deadline or str(ar.settlement_status)=="SETTLED":
            miss=pd.concat([miss,pd.DataFrame([{"feature_cutoff_date":d,"planned_forecast_issue_date":issue,"deadline_utc":deadline.isoformat(),"recorded_at_utc":ts.isoformat(),"reason":"CLEAN_V5_NOT_ISSUED_BEFORE_DEADLINE_NO_BACKFILL"}])],ignore_index=True);missed.add(d);continue
        q=g[g.feature_cutoff_date==d]
        if len(q)!=1:raise RuntimeError(f"CLEAN_V5_CURRENT_ROW_FAIL {d} {len(q)}")
        r=q.iloc[0];p=float(r.p_helios_v5_dce);pa=float(ar.p_aurora)
        v=pd.concat([v,pd.DataFrame([{"feature_cutoff_date":d,"issued_at_utc":ts.isoformat(),"planned_forecast_issue_date":issue,"p_clean_aurora":pa,"aurora_direction":"UP" if pa>=.5 else "DOWN","p_clean_v5":p,"v5_direction":"UP" if p>=.5 else "DOWN","changed_from_aurora":bool((pa>=.5)!=(p>=.5)),"active_expert":str(r.active_expert),"prob_path_superior":float(r.prob_path_superior),"gate_active":bool(r.gate_active),"candidate_reversal":bool(r.candidate_reversal),"opal_override":bool(r.opal_override),"p_opal_reversal":float(r.p_opal_reversal),"cot_report_date":r.cot_report_date,"cot_available_date":r.cot_available_date,"gt_flip_share":float(r.gt_flip_share),"v4_route":bool(r.v4_route),"rge_active":bool(r.rge_active),"dce_exception":bool(r.dce_exception),"settlement_status":"PENDING","target_end_date_h3":np.nan,"target_r3":np.nan,"y_up":np.nan,"aurora_correct":np.nan,"v5_correct":np.nan,"v5_brier_row":np.nan,"v5_logloss_row":np.nan,"settled_at_utc":""}])],ignore_index=True);existing.add(d);issued+=1
    if len(v):v["feature_cutoff_date"]=pd.to_datetime(v.feature_cutoff_date);v=v.sort_values("feature_cutoff_date").drop_duplicates("feature_cutoff_date",keep="first")
    if len(miss):miss["feature_cutoff_date"]=pd.to_datetime(miss.feature_cutoff_date);miss=miss.sort_values("feature_cutoff_date").drop_duplicates("feature_cutoff_date",keep="first")
    v.to_csv(OUT/V5_LEDGER.name,index=False,columns=V5_COLS);miss.to_csv(OUT/V5_MISSES.name,index=False,columns=MISS_COLS)
    ma,mv=met(v,"p_clean_aurora"),met(v,"p_clean_v5");z=v[v.settlement_status=="SETTLED"];resc=brok=0
    if len(z):
        ch=(z.p_clean_aurora>=.5)!=(z.p_clean_v5>=.5);y=z.y_up.astype(int);resc=int((ch&((z.p_clean_aurora>=.5).astype(int)!=y)&((z.p_clean_v5>=.5).astype(int)==y)).sum());brok=int((ch&((z.p_clean_aurora>=.5).astype(int)==y)&((z.p_clean_v5>=.5).astype(int)!=y)).sum())
    s={"identity":"CLEAN_V5_DCE_H3_V1_PROSPECTIVE_SHADOW","umbrella_identity":"CLEAN_H3_PROSPECTIVE_V1","freeze_timestamp_utc":str(FREEZE_TS),"first_eligible_feature_cutoff":str(FIRST_FEATURE.date()),"historical_reproduction_max_abs_diff":md,"forecast_rows":len(v),"settled_rows":int((v.settlement_status=="SETTLED").sum()) if len(v) else 0,"pending_rows":int((v.settlement_status!="SETTLED").sum()) if len(v) else 0,"missed_origins":len(miss),"new_forecasts":issued,"new_settlements":settled,"aurora_metrics":ma,"v5_metrics":mv,"rescued":resc,"broken":brok,"net_rescue":resc-brok}
    (OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_V5_STATUS.json").write_text(json.dumps(s,indent=2,sort_keys=True,default=str)+"\n")
    (OUT/"GOLD_H3_CLEAN_PROSPECTIVE_V1_V5_STATUS.md").write_text("# CLEAN V5-DCE H3 V1 — PROSPECTIVE SHADOW STATUS\n\n"+json.dumps(s,indent=2,default=str)+"\n")
    print(json.dumps(s,default=str))
if __name__=="__main__":main()
