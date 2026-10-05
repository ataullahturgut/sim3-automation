from pathlib import Path
import json, math, io, subprocess
import numpy as np
import pandas as pd
import requests
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

H3=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
IFBC_FROZEN=AX/"GOLD_H3_SAGE_V1_IFBC_SNAPSHOT_2026-10-04.csv"
LLRS_FROZEN=AX/"GOLD_H3_SAGE_V1_LLRS_SNAPSHOT_2026-10-04.csv"
SAGE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"
RF=AX/"GOLD_H3_RULEFLOW_V3_TOPOLOGY_DIAGNOSTIC_2026-10-04.csv"
PHASE=AX/"GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_PANEL_2026-10-05.csv"
SELLR=AX/"GOLD_H3_COMPETENCE_TRANSITION_V1_SELLR_SCORES_SOURCE_2026-10-05.csv"

OUT_IFBC=AX/"GOLD_H3_2025_BACKFILL_IFBC_EXTENDED_2026-10-05.csv"
OUT_LLRS=AX/"GOLD_H3_2025_BACKFILL_LLRS_EXTENDED_2026-10-05.csv"
OUT_STATE=AX/"GOLD_H3_2025_BACKFILL_HANDOFF_STATE_2026-10-05.csv"
OUT_ACT=AX/"GOLD_H3_2025_BACKFILL_DPTC_ACTIONS_2026-10-05.csv"
OUT_JSON=AX/"GOLD_H3_2025_BACKFILL_DPTC_SUMMARY_2026-10-05.json"
OUT_MD=AX/"GOLD_H3_2025_BACKFILL_DPTC_RESULT_2026-10-05.md"

START=pd.Timestamp("2024-10-10",tz="UTC")
END=pd.Timestamp("2026-10-04",tz="UTC")
SYMS={"GC":"GC=F","SI":"SI=F","ZN":"ZN=F","NQ":"NQ=F","CL":"CL=F"}
SELLR_THR=2.3677413378977423
Q99_RUN=4.0
CAL_N=120
MIN_CAL=60
WINDOW_DAYS=60
MIN_TRAIN=500
ALPHA=10.0

EXT_FEATURES=["ZN_r1","ZN_r3","ZN_r6","NQ_r1","NQ_r3","NQ_r6","SI_r1","SI_r3","SI_r6","CL_r1","CL_r3","CL_r6"]
GC_FEATURES=["GC_r1","GC_r3","GC_r6"]

S=requests.Session()
S.headers.update({"User-Agent":"Mozilla/5.0 academic research"})

def B(v):
    if isinstance(v,(bool,np.bool_)): return bool(v)
    if pd.isna(v): return False
    return str(v).strip().lower() in {"true","1","yes"}

def fetch(sym,label,need_volume=False):
    p1=int(START.timestamp());p2=int(END.timestamp());last=None
    for host in ["query1.finance.yahoo.com","query2.finance.yahoo.com"]:
        url=f"https://{host}/v8/finance/chart/{requests.utils.quote(sym,safe='')}"
        params={"period1":p1,"period2":p2,"interval":"1h","events":"history","includeAdjustedClose":"true"}
        try:
            r=S.get(url,params=params,timeout=60)
            if r.status_code!=200:
                last=f"{host} HTTP {r.status_code}: {r.text[:300]}";continue
            j=r.json()["chart"]
            if j.get("error") or not j.get("result"):
                last=f"{host} chart_error={j.get('error')}";continue
            z=j["result"][0];q=z["indicators"]["quote"][0]
            rows=[]
            for i,t in enumerate(z.get("timestamp",[])):
                c=q.get("close",[])[i]
                if c is None: continue
                cv=float(c)
                if not np.isfinite(cv) or cv<=0: continue
                if need_volume:
                    vv=q.get("volume",[])[i] if i<len(q.get("volume",[])) else None
                    vv=0.0 if vv is None or not np.isfinite(float(vv)) else max(0.0,float(vv))
                    rows.append((pd.to_datetime(t,unit="s",utc=True),cv,vv))
                else:
                    rows.append((pd.to_datetime(t,unit="s",utc=True),cv))
            cols=["ts",f"{label}_close",f"{label}_volume"] if need_volume else ["ts",label]
            d=pd.DataFrame(rows,columns=cols).drop_duplicates("ts").sort_values("ts")
            if len(d)<3000: last=f"{host} too few rows={len(d)}";continue
            return d
        except Exception as e:
            last=f"{host}: {type(e).__name__}: {e}"
    raise RuntimeError(f"FETCH_FAIL {sym}: {last}")

def same_hour_volume_z(df,label):
    q=df.copy()
    q["et_hour"]=q.ts.dt.tz_convert("America/New_York").dt.hour
    q[f"{label}_logvol"]=np.log1p(q[f"{label}_volume"].astype(float))
    z=pd.Series(np.nan,index=q.index,dtype=float)
    for _,idx in q.groupby("et_hour").groups.items():
        ids=list(idx);s=q.loc[ids,f"{label}_logvol"];prior=s.shift(1)
        mu=prior.rolling(40,min_periods=15).mean()
        sd=prior.rolling(40,min_periods=15).std(ddof=0).replace(0,np.nan)
        z.loc[ids]=(s-mu)/sd
    q[f"{label}_volume_z"]=z
    return q.drop(columns=["et_hour",f"{label}_logvol"])

def cutoff_ts(d):
    return (pd.Timestamp(d.date()).tz_localize("America/New_York")+pd.Timedelta(hours=16)).tz_convert("UTC")

def efficiency(ret):
    den=float(np.abs(ret).sum())
    return 0.0 if den<=1e-12 else float(abs(ret.sum())/den)

def vol_flow(ret,vol,s):
    den=float(vol.sum())
    return 0.0 if den<=0 else float(s*np.sum(ret*vol)/den)

def opp_share(ret,vol,s):
    den=float(vol.sum())
    if den<=0:return 0.0
    return float(vol[(s*ret)<0].sum()/den)

def build_vast_raw(h3):
    gc=same_hour_volume_z(fetch("GC=F","GC",True),"GC")
    si=same_hour_volume_z(fetch("SI=F","SI",True),"SI")
    x=gc.merge(si,on="ts",how="inner").sort_values("ts").reset_index(drop=True)
    x["GC_ret1"]=np.log(x.GC_close).diff();x["SI_ret1"]=np.log(x.SI_close).diff()
    hh=h3[h3.eligible_v5_continuation.map(B)].copy()
    hh=hh[hh.forecast_issue_date>=pd.Timestamp("2024-10-15")].sort_values("forecast_issue_date")
    rows=[]
    for r in hh.itertuples():
        co=cutoff_ts(r.feature_cutoff_date)
        w=x[(x.ts<=co)&(x.ts>=co-pd.Timedelta(hours=18))].tail(12).copy()
        if len(w)<12:continue
        if (co-w.ts.iloc[-1]).total_seconds()/3600>3:continue
        if (w.ts.iloc[-1]-w.ts.iloc[0]).total_seconds()/3600>18:continue
        if w[["GC_ret1","SI_ret1"]].isna().any(axis=None):continue
        s=1.0 if int(r.momentum_up)==1 else -1.0
        d=r._asdict()
        for h in [3,6,12]:
            z=w.tail(h)
            d[f"gc_flow_{h}"]=vol_flow(z.GC_ret1.to_numpy(),z.GC_volume.to_numpy(),s)
            d[f"gc_opp_vol_share_{h}"]=opp_share(z.GC_ret1.to_numpy(),z.GC_volume.to_numpy(),s)
        for h in [6,12]:
            z=w.tail(h);d[f"gc_efficiency_{h}"]=efficiency(z.GC_ret1.to_numpy())
        for h in [6,12]:
            z=w.tail(h)
            d[f"si_flow_{h}"]=vol_flow(z.SI_ret1.to_numpy(),z.SI_volume.to_numpy(),s)
            d[f"si_opp_vol_share_{h}"]=opp_share(z.SI_ret1.to_numpy(),z.SI_volume.to_numpy(),s)
        d["gc_si_flow_gap12"]=float(d["gc_flow_12"]-d["si_flow_12"])
        d["joint_opposition_share12"]=float((d["gc_opp_vol_share_12"]+d["si_opp_vol_share_12"])/2)
        d["hourly_last_ts"]=w.ts.iloc[-1]
        rows.append(d)
    return pd.DataFrame(rows).sort_values("feature_cutoff_date").reset_index(drop=True)

def rank_val(hist,v,min_n=MIN_CAL):
    a=np.asarray(hist,float);a=a[np.isfinite(a)]
    if len(a)<min_n or not np.isfinite(v):return np.nan
    return float((1+np.sum(a<=v))/(len(a)+1))

def build_ifbc_scores(vast):
    z=vast.copy().sort_values("feature_cutoff_date").reset_index(drop=True)
    z["x1"]=z.gc_opp_vol_share_12
    z["x2"]=-z.gc_flow_12
    z["x3"]=-z.si_flow_12
    z["x4"]=z.joint_opposition_share12
    z["x5"]=z.gc_si_flow_gap12
    z["x6"]=1-z.gc_efficiency_12
    rows=[]
    for i,r in z.iterrows():
        hist=z[z.feature_cutoff_date<r.feature_cutoff_date].tail(CAL_N)
        ranks=[rank_val(hist[f"x{k}"],r[f"x{k}"]) for k in range(1,7)]
        if any(not np.isfinite(v) for v in ranks):continue
        d=r.to_dict()
        for k,v in enumerate(ranks,1):d[f"rank_{k}"]=v
        d["ifbc_score"]=float(np.median(ranks));d["ifbc_count60"]=int(sum(v>=.60 for v in ranks))
        rows.append(d)
    return pd.DataFrame(rows).sort_values("feature_cutoff_date").reset_index(drop=True)

def ridge():
    return Pipeline([("scale",StandardScaler()),("ridge",Ridge(alpha=ALPHA))])

def llrs_prepare_hourly(raw):
    x=raw[["ts","GC","ZN","NQ","SI","CL"]].copy().sort_values("ts").drop_duplicates("ts",keep="last").reset_index(drop=True)
    for name in SYMS:
        lv=np.log(pd.to_numeric(x[name],errors="coerce"))
        for h in [1,3,6]:
            x[f"{name}_r{h}"]=lv-lv.shift(h)
    x["target_ts_6h"]=x.ts.shift(-6)
    x["GC_fwd6"]=np.log(x.GC.shift(-6))-np.log(x.GC)
    wall=(x.target_ts_6h-x.ts).dt.total_seconds()/3600
    x.loc[(wall<5)|(wall>8.5),"GC_fwd6"]=np.nan
    return x

def llrs_origin_scores(hourly,h3,min_issue):
    hh=h3[h3.eligible_v5_continuation.map(B)].copy()
    hh=hh[hh.forecast_issue_date>=pd.Timestamp(min_issue)].sort_values("forecast_issue_date")
    ready=hourly.dropna(subset=EXT_FEATURES+GC_FEATURES+["GC_fwd6","target_ts_6h"]).copy()
    rows=[]
    for r in hh.itertuples():
        co=cutoff_ts(r.feature_cutoff_date)
        hist=ready[(ready.ts>=co-pd.Timedelta(days=WINDOW_DAYS))&(ready.target_ts_6h<co)].copy()
        if len(hist)<MIN_TRAIN:continue
        cur=hourly[hourly.ts<=co].tail(1).copy()
        if cur.empty or cur[EXT_FEATURES+GC_FEATURES].isna().any(axis=None):continue
        stale=(co-cur.ts.iloc[0]).total_seconds()/3600
        if stale<0 or stale>3:continue
        me,mg=ridge(),ridge();y=hist.GC_fwd6.to_numpy(float)
        me.fit(hist[EXT_FEATURES].to_numpy(float),y);mg.fit(hist[GC_FEATURES].to_numpy(float),y)
        pe=float(me.predict(cur[EXT_FEATURES].to_numpy(float))[0])
        pg=float(mg.predict(cur[GC_FEATURES].to_numpy(float))[0])
        sigma=float(np.std(y-me.predict(hist[EXT_FEATURES].to_numpy(float)),ddof=1))
        if not np.isfinite(sigma) or sigma<=1e-9:continue
        s=1.0 if int(r.momentum_up)==1 else -1.0
        rows.append({
          "feature_cutoff_date":r.feature_cutoff_date,"forecast_issue_date":r.forecast_issue_date,
          "target_end_date_h3":r.target_end_date_h3,"y_up":int(r.y_up),"momentum_up":int(r.momentum_up),
          "v5_pred":int(r.v5_pred),"rescue_target":int(r.rescue_target),
          "llrs_pressure":float(-s*pe/sigma),"llrs_incremental":float(-s*(pe-pg)/sigma),
          "llrs_external_opposes":bool(s*pe<0),"hourly_source_ts":cur.ts.iloc[0],
          "hourly_train_n":int(len(hist))
        })
    if not rows:
        return pd.DataFrame(columns=["feature_cutoff_date","forecast_issue_date","target_end_date_h3","y_up","momentum_up","v5_pred","rescue_target","llrs_pressure","llrs_incremental","llrs_external_opposes","hourly_source_ts","hourly_train_n"])
    return pd.DataFrame(rows).sort_values("feature_cutoff_date").reset_index(drop=True)

def load_frozen_llrs_hourly():
    spec="origin/gold-h3-llrs-v1-20261004:gold_axis_2026/GOLD_H3_LLRS_V1_HOURLY_PANEL_2026-10-04.csv"
    raw=subprocess.check_output(["git","show",spec],text=True)
    q=pd.read_csv(io.StringIO(raw))
    q["ts"]=pd.to_datetime(q["ts"],utc=True)
    return q

def build_llrs(h3):
    # Reconstruct missing pre-2025 history from the same Yahoo identities, but
    # preserve the original frozen 2025 hourly panel byte-for-source instead of
    # trusting today's mutable continuous-futures history.
    current=None
    for name,sym in SYMS.items():
        d=fetch(sym,name,False)
        current=d if current is None else current.merge(d,on="ts",how="inner")
    current=current.sort_values("ts").reset_index(drop=True)

    frozen_raw=load_frozen_llrs_hourly()
    first_frozen=frozen_raw.ts.min()

    # QA path: reproduce the original LLRS scores from the original frozen raw panel.
    qa_hourly=llrs_prepare_hourly(frozen_raw)
    qa_scores=llrs_origin_scores(qa_hourly,h3,"2025-01-01")

    # Extension path: only pre-frozen timestamps come from today's same-source fetch;
    # all timestamps from the original first frozen bar onward use the archived raw panel.
    pre=current[current.ts<first_frozen][["ts","GC","ZN","NQ","SI","CL"]].copy()
    core=frozen_raw[["ts","GC","ZN","NQ","SI","CL"]].copy()
    hybrid_raw=pd.concat([pre,core],ignore_index=True).sort_values("ts").drop_duplicates("ts",keep="last")
    hybrid_hourly=llrs_prepare_hourly(hybrid_raw)
    ext_scores=llrs_origin_scores(hybrid_hourly,h3,"2024-12-01")
    return ext_scores,qa_scores,{
        "first_frozen_hourly":str(first_frozen),
        "pre_extension_rows":int(len(pre)),
        "frozen_hourly_rows":int(len(core)),
        "hybrid_hourly_rows":int(len(hybrid_hourly)),
    }

def rolling_rank(df,col,sign=1.0,window=120):
    x=pd.to_numeric(df[col],errors="coerce").to_numpy(float)*sign
    out=np.full(len(df),np.nan)
    for i in range(len(df)):
        h=x[max(0,i-window):i];a=h[np.isfinite(h)]
        if len(a)<20 or not np.isfinite(x[i]):continue
        out[i]=float((1+np.sum(a<=x[i]))/(len(a)+1))
    return out

def med(df,cols):
    return np.nanmedian(df[cols].to_numpy(float),axis=1)

def build_handoff_scores(ifbc,llrs):
    i=ifbc.sort_values("feature_cutoff_date").reset_index(drop=True).copy()
    mom=np.where(i.momentum_up.astype(int).to_numpy()==1,1.0,-1.0)
    i["gc_flow_against_mom"]=-mom*pd.to_numeric(i.gc_flow_12,errors="coerce").to_numpy(float)
    i["si_flow_against_mom"]=-mom*pd.to_numeric(i.si_flow_12,errors="coerce").to_numpy(float)
    specs={
      "r_frag_trend":("trend_strength",-1.0),"r_frag_session":("session_against_trend",1.0),
      "r_frag_close":("trend_close_location",-1.0),"r_frag_adverse":("adverse_excursion",1.0),
      "r_flow_gc_oppvol":("gc_opp_vol_share_12",1.0),"r_flow_si_oppvol":("si_opp_vol_share_12",1.0),
      "r_flow_joint":("joint_opposition_share12",1.0),"r_flow_gc_against":("gc_flow_against_mom",1.0),
      "r_flow_si_against":("si_flow_against_mom",1.0),"r_flow_ineff":("gc_efficiency_12",-1.0)}
    for out,(col,sgn) in specs.items():i[out]=rolling_rank(i,col,sgn)
    i["fragility_score"]=med(i,["r_frag_trend","r_frag_session","r_frag_close","r_frag_adverse"])
    i["flow_score"]=med(i,["r_flow_gc_oppvol","r_flow_si_oppvol","r_flow_joint","r_flow_gc_against","r_flow_si_against","r_flow_ineff"])

    l=llrs.sort_values("feature_cutoff_date").reset_index(drop=True).copy()
    l["r_llrs_pressure"]=rolling_rank(l,"llrs_pressure",1)
    l["r_llrs_incremental"]=rolling_rank(l,"llrs_incremental",1)
    l["llrs_strict"]=l.llrs_external_opposes.map(B)&(pd.to_numeric(l.llrs_pressure,errors="coerce")>0)&(pd.to_numeric(l.llrs_incremental,errors="coerce")>0)
    l["leadlag_score"]=med(l,["r_llrs_pressure","r_llrs_incremental"])
    l.loc[~l.llrs_strict,"leadlag_score"]=0.0

    z=i[["feature_cutoff_date","fragility_score","flow_score"]].merge(
      l[["feature_cutoff_date","leadlag_score"]],on="feature_cutoff_date",how="inner")
    z=z.sort_values("feature_cutoff_date").reset_index(drop=True)
    for c in ["fragility_score","flow_score","leadlag_score"]:
        z[f"{c}_lag1"]=z[c].shift(1);z[f"{c}_lag2"]=z[c].shift(2)
    z["leadlag_score_premax"]=z[["leadlag_score_lag1","leadlag_score_lag2"]].max(axis=1)
    z["internal_now"]=z[["fragility_score","flow_score"]].max(axis=1)
    z["internal_lag1"]=z[["fragility_score_lag1","flow_score_lag1"]].max(axis=1)
    z["internal_d1"]=z.internal_now-z.internal_lag1
    return z

def confusion(y,p):
    y=np.asarray(y,int);p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum());tn=int(((y==0)&(p==0)).sum())
    fp=int(((y==0)&(p==1)).sum());fn=int(((y==1)&(p==0)).sum())
    up=tp/max(tp+fn,1);dn=tn/max(tn+fp,1)
    return {"n":len(y),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),
            "tp":tp,"tn":tn,"fp":fp,"fn":fn,"balanced_accuracy":float((up+dn)/2)}

def simulate_dptc(alarms,phase_col):
    trust=False;broken_streak=0;pending=[];rows=[];entry=None
    for _,r in alarms.sort_values("feature_cutoff_date").iterrows():
        now=r.feature_cutoff_date
        matured=[p for p in pending if p["maturity"]<=now]
        pending=[p for p in pending if p["maturity"]>now]
        for p in sorted(matured,key=lambda x:(x["maturity"],x["origin"])):
            if p["acted"] and trust:
                if p["y"]==1:broken_streak=0
                else:
                    broken_streak+=1
                    if broken_streak>=2:trust=False;broken_streak=0
        catalyst=bool(r.sellr_fire)
        if (not trust) and catalyst:
            trust=True;broken_streak=0
            if entry is None:entry=now
        pretrust=bool(r[phase_col]) if not trust else False
        acted=bool(trust or pretrust)
        mode="TRUST" if trust else ("PHASE" if pretrust else "KEEP")
        rows.append({**r.to_dict(),"acted":acted,"mode":mode})
        pending.append({"origin":now,"maturity":r.target_end_date_h3,"y":int(r.competence_y),"acted":acted})
    q=pd.DataFrame(rows);a=q[q.acted].copy()
    rescue=int(a.competence_y.sum()) if len(a) else 0;broken=int(len(a)-rescue)
    return q,a,entry,rescue,broken

def maxdiff(a,b,cols):
    j=a[["feature_cutoff_date"]+cols].merge(b[["feature_cutoff_date"]+cols],on="feature_cutoff_date",suffixes=("_new","_old"))
    out={}
    for c in cols:
        d=np.abs(pd.to_numeric(j[f"{c}_new"],errors="coerce")-pd.to_numeric(j[f"{c}_old"],errors="coerce"))
        out[c]=None if d.dropna().empty else float(d.max())
    return len(j),out

def main():
    h3=pd.read_csv(H3)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:h3[c]=pd.to_datetime(h3[c])
    for c in ["eligible_v5_continuation","opal_override_check"]:
        if c in h3.columns:h3[c]=h3[c].map(B)

    vast=build_vast_raw(h3)
    ifbc_new=build_ifbc_scores(vast)
    llrs_new,llrs_qa,llrs_bridge=build_llrs(h3)

    oldi=pd.read_csv(IFBC_FROZEN);oldl=pd.read_csv(LLRS_FROZEN)
    for q in [oldi,oldl]:
        for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
            if c in q.columns:q[c]=pd.to_datetime(q[c])

    rawcols=["gc_flow_12","gc_opp_vol_share_12","gc_efficiency_12","si_flow_12","si_opp_vol_share_12","gc_si_flow_gap12","joint_opposition_share12"]
    ni,di=maxdiff(ifbc_new,oldi,rawcols)
    nl,dl=maxdiff(llrs_qa,oldl,["llrs_pressure","llrs_incremental"])

    first_i=oldi.feature_cutoff_date.min();first_l=oldl.feature_cutoff_date.min()
    iext=pd.concat([ifbc_new[ifbc_new.feature_cutoff_date<first_i],oldi],ignore_index=True,sort=False).sort_values("feature_cutoff_date").drop_duplicates("feature_cutoff_date",keep="last")
    lext=pd.concat([llrs_new[llrs_new.feature_cutoff_date<first_l],oldl],ignore_index=True,sort=False).sort_values("feature_cutoff_date").drop_duplicates("feature_cutoff_date",keep="last")
    iext.to_csv(OUT_IFBC,index=False);lext.to_csv(OUT_LLRS,index=False)

    state=build_handoff_scores(iext,lext)
    z=h3[h3.feature_cutoff_date.dt.year==2025].copy().sort_values("feature_cutoff_date")
    z["v5_pred"]=(pd.to_numeric(z.p_helios_v5_dce,errors="coerce")>=.5).astype(int)

    sg=pd.read_csv(SAGE,parse_dates=["feature_cutoff_date"])
    sdates=set(sg[(sg.feature_cutoff_date.dt.year==2025)&sg.ocs_candidate.map(B)].feature_cutoff_date)
    rf=pd.read_csv(RF,parse_dates=["date"])
    rdates=set(rf[(rf.period.astype(str)=="2025")&rf.v3_candidate.map(B)].date)
    flips=sdates|rdates
    z["baseline_pred"]=np.where(z.feature_cutoff_date.isin(flips),1-z.v5_pred,z.v5_pred).astype(int)
    z["baseline_correct"]=z.baseline_pred==z.y_up.astype(int)
    z=z.merge(state,on="feature_cutoff_date",how="left")

    ph=pd.read_csv(PHASE,parse_dates=["feature_cutoff_date"])
    z=z.merge(ph[["feature_cutoff_date","strong_pro_risk","strong_run","dep_shift95","dependence_phase"]],on="feature_cutoff_date",how="left")
    z["phase_q95"]=z.dependence_phase.map(B)
    z["phase_q99"]=z.strong_pro_risk.map(B)&((pd.to_numeric(z.strong_run,errors="coerce")>Q99_RUN)|z.dep_shift95.map(B))

    sc=pd.read_csv(SELLR,parse_dates=["feature_cutoff_date"])
    sc=sc[["feature_cutoff_date","sellr_score","baseline_pred","momentum_up"]].rename(columns={"baseline_pred":"sellr_baseline_pred","momentum_up":"sellr_momentum_up"})
    z=z.merge(sc,on="feature_cutoff_date",how="left")
    z["sellr_fire"]=(pd.to_numeric(z.sellr_score,errors="coerce")>=SELLR_THR)&(pd.to_numeric(z.sellr_baseline_pred,errors="coerce")==pd.to_numeric(z.sellr_momentum_up,errors="coerce"))
    z["handoff_alarm"]=(pd.to_numeric(z.leadlag_score_premax,errors="coerce")>=.60)&(pd.to_numeric(z.internal_now,errors="coerce")>=.60)&(pd.to_numeric(z.internal_d1,errors="coerce")>=0)&(z.baseline_pred.astype(int)==z.momentum_up.astype(int))
    z["competence_y"]=(~z.baseline_correct).astype(int)
    z.to_csv(OUT_STATE,index=False)

    alarms=z[z.handoff_alarm].copy()
    results={};acts=[]
    base=confusion(z.y_up,z.baseline_pred)
    for name,col in [("Q95","phase_q95"),("Q99","phase_q99")]:
        _,a,e,r,b=simulate_dptc(alarms,col)
        pred=z.baseline_pred.to_numpy(int).copy()
        ad=set(a.feature_cutoff_date)
        mask=z.feature_cutoff_date.isin(ad).to_numpy()
        pred[mask]=1-pred[mask]
        m=confusion(z.y_up,pred)
        results[name]={"actions":len(a),"rescue":r,"broken":b,"net":r-b,
                       "entry":None if e is None else e.date().isoformat(),
                       "precision":float(r/max(len(a),1)),"metrics":m,
                       "phase_actions":int((a["mode"]=="PHASE").sum()) if len(a) else 0,
                       "trust_actions":int((a["mode"]=="TRUST").sum()) if len(a) else 0,
                       "action_dates":[{"date":d.feature_cutoff_date.date().isoformat(),"mode":d.mode,"outcome":"RESCUE" if d.competence_y==1 else "BROKEN","sellr_fire":bool(d.sellr_fire)} for d in a.itertuples()]}
        if len(a):
            aa=a.copy();aa["variant"]=name;acts.append(aa)
    if acts:pd.concat(acts,ignore_index=True).to_csv(OUT_ACT,index=False)
    else:pd.DataFrame().to_csv(OUT_ACT,index=False)

    raw_pass=all(v is not None and v<1e-8 for v in di.values()) and all(v is not None and v<1e-8 for v in dl.values())
    summary={
      "schema":"GOLD_H3_2025_SOURCE_BACKFILL_DPTC_REPLAY_V1",
      "status":"SOURCE_REPRO_PASS" if raw_pass else "SOURCE_REPRO_MISMATCH_REVIEW_REQUIRED",
      "source_window":{"start":str(START),"end":str(END),"yahoo_limit":"730_days"},
      "qa":{"ifbc_overlap_n":ni,"ifbc_raw_max_abs_diff":di,"llrs_overlap_n":nl,"llrs_max_abs_diff":dl,"llrs_bridge":llrs_bridge,"raw_source_reproduction_pass":raw_pass},
      "coverage":{"reconstructed_vast_first":str(vast.feature_cutoff_date.min().date()),"reconstructed_ifbc_score_first":str(ifbc_new.feature_cutoff_date.min().date()),"extended_ifbc_first":str(iext.feature_cutoff_date.min().date()),"reconstructed_llrs_first":str(llrs_new.feature_cutoff_date.min().date()),"extended_llrs_first":str(lext.feature_cutoff_date.min().date()),"handoff_state_first_complete":None if state.dropna(subset=["leadlag_score_premax","internal_now","internal_d1"]).empty else str(state.dropna(subset=["leadlag_score_premax","internal_now","internal_d1"]).feature_cutoff_date.min().date())},
      "2025":{"origins":len(z),"baseline":base,"handoff_alarms":len(alarms),"handoff_rescue":int(alarms.competence_y.sum()),"handoff_broken":int(len(alarms)-alarms.competence_y.sum()),"variants":results},
      "frozen_overlay":{"sage_dates":sorted(d.date().isoformat() for d in sdates),"ruleflow_dates":sorted(d.date().isoformat() for d in rdates)}
    }
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 — 2025 Source Backfill + DPTC Replay V1","",
           f"**Status:** {summary['status']}","",
           "## Source reconstruction QA","",
           f"- IFBC raw overlap rows: **{ni}**",
           f"- LLRS overlap rows: **{nl}**",
           f"- raw-source reproduction pass (<1e-8): **{raw_pass}**",
           f"- reconstructed VAST first origin: **{summary['coverage']['reconstructed_vast_first']}**",
           f"- reconstructed IFBC score first origin: **{summary['coverage']['reconstructed_ifbc_score_first']}**",
           f"- reconstructed LLRS first origin: **{summary['coverage']['reconstructed_llrs_first']}**",
           f"- first complete extended Handoff state: **{summary['coverage']['handoff_state_first_complete']}**","",
           "## 2025 full-year replay","",
           f"- origins: **{len(z)}**",
           f"- combined V5+frozen SAGE+RuleFlow baseline: **{base['correct']}/{base['n']} = {100*base['accuracy']:.2f}%**, BA **{100*base['balanced_accuracy']:.2f}%**",
           f"- reconstructed canonical Handoff alarms: **{len(alarms)}**, rescue/broken **{int(alarms.competence_y.sum())}/{int(len(alarms)-alarms.competence_y.sum())}**","",
           "| Variant | Actions | Rescue | Broken | Net | Precision | Entry | Correct/N | Accuracy | BA |",
           "|---|---:|---:|---:|---:|---:|---|---:|---:|---:|"]
    for name in ["Q95","Q99"]:
        s=results[name];m=s["metrics"]
        lines.append(f"| {name} | {s['actions']} | {s['rescue']} | {s['broken']} | {s['net']:+d} | {100*s['precision']:.1f}% | {s['entry'] or 'none'} | {m['correct']}/{m['n']} | {100*m['accuracy']:.2f}% | {100*m['balanced_accuracy']:.2f}% |")
    lines+=["","## Action chronology",""]
    for name in ["Q95","Q99"]:
        lines.append(f"### {name}")
        if not results[name]["action_dates"]:lines.append("- no actions")
        for a in results[name]["action_dates"]:lines.append(f"- {a['date']} — {a['mode']} — {a['outcome']} — SELLR={a['sellr_fire']}")
        lines.append("")
    lines+=["## Interpretation discipline","",
            "- Missing 2025 hourly source history is reconstructed from the same Yahoo futures identities and the same original VAST/IFBC/LLRS equations.",
            "- Frozen post-start IFBC and LLRS snapshots are retained; reconstructed rows are used only before their original first dates.",
            "- Handoff ranks are recomputed over the extended history, because the purpose of this audit is explicitly to test the model after filling the missing historical state.",
            "- SAGE is not back-activated into 2025 H1; its original maturity boundary is preserved.",
            "- This is a historical reconstruction/backfill replay, not prospective validation."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: backfill-after-workflow-installed
