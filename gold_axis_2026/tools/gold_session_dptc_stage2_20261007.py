from __future__ import annotations

import importlib.util, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"SESSION_DPTC_STAGE2_OUT"; OUT.mkdir(exist_ok=True)

BOCPD=AX/"tools"/"gold_session_bocpd_v1_stage2_20261007.py"
PREREG=AX/"GOLD_SESSION_DPTC_STAGE1C_STAGE2_PREREG_2026-10-07.md"
CME=AX/"GOLD_H3_RTE_V1_CME_SOURCE_2026-10-03.csv"
DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"

QLEVELS=[0.80,0.85,0.90,0.95]
MIN_SELLR_TRAIN=80
SIGNS={
 "adverse_excursion":1.0,
 "trend_strength":-1.0,
 "trend_close_location":-1.0,
 "session_against_trend":1.0,
 "opposite_semivar_share":1.0,
 "signed_opt_pressure":1.0,
 "signed_d_opt_pressure":1.0,
 "core_confirmation":-1.0,
 "cross_dispersion":1.0,
 "topology_rotation":1.0,
 "trend_age":1.0,
}
FEATS=list(SIGNS)
BASEMAP={"GC":"v","SI":"v","NQ":"v","ZN":"n","CL":"c"}
STALE={"metal":5,"usd":7,"yield":7,"ndx":5,"vix":5,"cme":7}

def loadmod(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m
bocpd=loadmod("session_bocpd_stage2_for_dptc",BOCPD)

def num(s): return pd.to_numeric(s,errors="coerce")

def add_trend_age(p):
 out=[]
 for _,g0 in p.groupby(["partition","window"],sort=True):
  g=g0.sort_values("start_utc").copy();ages=[];prev=None;run=0
  for m in g.momentum_up.astype(int):
   if prev is None or m!=prev: run=1
   else: run+=1
   ages.append(run);prev=m
  g["trend_age"]=ages;out.append(g)
 return pd.concat(out,ignore_index=True)

def cme_features():
 q=pd.read_csv(CME)
 q["trade_date"]=pd.to_datetime(q.trade_date,errors="raise")
 q=q[q.status.eq("PASS")].drop_duplicates("trade_date",keep="last").sort_values("trade_date").copy()
 q["gc_total_volume"]=num(q.gc_total_volume);q["call_vol"]=num(q.call_vol);q["put_vol"]=num(q.put_vol)
 den=(q.call_vol+q.put_vol).replace(0,np.nan)
 q["opt_vol_imbalance"]=(q.call_vol-q.put_vol)/den
 q["d_opt_vol_imbalance_1"]=q.opt_vol_imbalance.diff()
 return q[["trade_date","opt_vol_imbalance","d_opt_vol_imbalance_1"]].dropna()

def zprior(s,window=60,minp=30):
 mu=s.shift(1).rolling(window,min_periods=minp).mean()
 sd=s.shift(1).rolling(window,min_periods=minp).std(ddof=0)
 return (s-mu)/sd.replace(0,np.nan)

def daily_sources():
 d=pd.read_csv(DIV)
 datecols=["feature_cutoff_date","metal_source_date","usd_source_date","yield_source_date","ndx_source_date","vix_source_date"]
 for c in datecols:d[c]=pd.to_datetime(d[c],errors="coerce")

 metal=d[["metal_source_date","silver_ret1","gold_daily_ret1"]].dropna().drop_duplicates("metal_source_date",keep="last").rename(columns={"metal_source_date":"date"}).sort_values("date")
 metal["z_silver"]=zprior(num(metal.silver_ret1))
 usd=d[["usd_source_date","usd_ret1"]].dropna().drop_duplicates("usd_source_date",keep="last").rename(columns={"usd_source_date":"date"}).sort_values("date")
 usd["z_usd"]=zprior(num(usd.usd_ret1))
 yld=d[["yield_source_date","tnx_chg1"]].dropna().drop_duplicates("yield_source_date",keep="last").rename(columns={"yield_source_date":"date"}).sort_values("date")
 yld["z_yield"]=zprior(num(yld.tnx_chg1))
 ndx=d[["ndx_source_date","ndx_ret1"]].dropna().drop_duplicates("ndx_source_date",keep="last").rename(columns={"ndx_source_date":"date"}).sort_values("date")
 ndx["z_ndx"]=zprior(num(ndx.ndx_ret1))
 vix=d[["vix_source_date","vix_ret1"]].dropna().drop_duplicates("vix_source_date",keep="last").rename(columns={"vix_source_date":"date"}).sort_values("date")
 vix["z_vix"]=zprior(num(vix.vix_ret1))
 return {"metal":metal,"usd":usd,"yield":yld,"ndx":ndx,"vix":vix},d.sort_values("feature_cutoff_date").reset_index(drop=True)

def latest_before(df,cutoff,max_stale):
 z=df[df.date<cutoff]
 if z.empty:return None
 r=z.iloc[-1];age=(cutoff-r.date).days
 return None if age>max_stale else r

def corr_info(a,b):
 a=np.asarray(a,float);b=np.asarray(b,float);m=np.isfinite(a)&np.isfinite(b);a=a[m];b=b[m]
 if len(a)<40 or np.std(a)<=1e-12 or np.std(b)<=1e-12:return np.nan,np.nan,len(a)
 r,p=pearsonr(a,b);return float(r),float(p),len(a)

def topology_table(div):
 rows=[]
 for i,r in div.iterrows():
  h=div.iloc[max(0,i-60):i]
  rn,pn,nn=corr_info(num(h.gold_daily_ret1),num(h.ndx_ret1))
  rv,pv,nv=corr_info(num(h.gold_daily_ret1),num(h.vix_ret1))
  strong=bool(np.isfinite(rn) and np.isfinite(rv) and np.isfinite(pn) and np.isfinite(pv) and rn>0 and rv<0 and min(pn,pv)<.05)
  rows.append({"date":r.feature_cutoff_date,"r_gn":rn,"p_gn":pn,"r_gv":rv,"p_gv":pv,"strong_pro_risk":strong,"n_gn":nn,"n_gv":nv})
 z=pd.DataFrame(rows).sort_values("date").reset_index(drop=True)
 run=[];cur=0
 for x in z.strong_pro_risk:
  cur=cur+1 if bool(x) else 0;run.append(cur)
 z["strong_run"]=run
 vals=z[["r_gn","r_gv"]].to_numpy(float);shift=np.full(len(z),np.nan)
 for i in range(len(z)):
  if i<100:continue
  ref=vals[max(0,i-125):i-5];rec=vals[max(0,i-4):i+1]
  ref=ref[np.isfinite(ref).all(axis=1)];rec=rec[np.isfinite(rec).all(axis=1)]
  if len(ref)<80 or len(rec)<3:continue
  med=np.median(ref,axis=0);mad=np.median(np.abs(ref-med),axis=0)*1.4826;std=np.std(ref,axis=0)
  scale=np.where((np.isfinite(mad))&(mad>1e-9),mad,np.where(std>1e-9,std,1.0))
  delta=(np.mean(rec,axis=0)-med)/scale;shift[i]=float(np.sqrt(np.sum(delta**2)))
 z["dep_shift"]=shift
 z["topology_rotation"]=np.sqrt(z.r_gn.diff()**2+z.r_gv.diff()**2)
 cal=z[z.date.dt.year<=2023].copy()
 q95_run=float(np.nanquantile(cal.strong_run,.95));q99_run=float(np.nanquantile(cal.strong_run,.99))
 q95_shift=float(np.nanquantile(cal.dep_shift.dropna(),.95))
 z["phase_q95"]=z.strong_pro_risk & ((z.strong_run>q95_run)|(z.dep_shift>=q95_shift))
 z["phase_q99"]=z.strong_pro_risk & ((z.strong_run>q99_run)|(z.dep_shift>=q95_shift))
 return z,{"q95_run":q95_run,"q99_run":q99_run,"q95_shift":q95_shift}

def attach_daily(p):
 src,div=daily_sources();topo,cal=topology_table(div);cme=cme_features()
 rows=[]
 for r in p.itertuples(index=False):
  T=pd.Timestamp(r.start_utc);cut=pd.Timestamp(T.tz_convert("America/New_York").date())
  mr=latest_before(src["metal"],cut,STALE["metal"]);ur=latest_before(src["usd"],cut,STALE["usd"])
  yr=latest_before(src["yield"],cut,STALE["yield"]);nr=latest_before(src["ndx"],cut,STALE["ndx"]);vr=latest_before(src["vix"],cut,STALE["vix"])
  oc=cme[cme.trade_date<cut]
  tr=topo[topo.date<cut]
  if any(x is None for x in [mr,ur,yr,nr,vr]) or oc.empty or tr.empty:continue
  oq=oc.iloc[-1]
  if (cut-oq.trade_date).days>STALE["cme"]:continue
  tq=tr.iloc[-1]
  vals=[float(mr.z_silver),float(ur.z_usd),float(yr.z_yield),float(nr.z_ndx),float(vr.z_vix)]
  if not np.all(np.isfinite(vals)) or not np.isfinite(tq.topology_rotation):continue
  s=1.0 if int(r.momentum_up)==1 else -1.0
  d=r._asdict()
  d.update({
   "signed_opt_pressure":float(-s*oq.opt_vol_imbalance),
   "signed_d_opt_pressure":float(-s*oq.d_opt_vol_imbalance_1),
   "core_confirmation":float(np.mean([s*vals[0],-s*vals[1],-s*vals[2]])),
   "cross_dispersion":float(np.std(vals,ddof=0)),
   "topology_rotation":float(tq.topology_rotation),
   "phase_q95":bool(tq.phase_q95),"phase_q99":bool(tq.phase_q99),
   "topology_date":tq.date,"cme_trade_date":oq.trade_date,
  })
  rows.append(d)
 return pd.DataFrame(rows),cal

def fit_sellr(train):
 spec={}
 y=train.reversal_target.astype(int).to_numpy()
 for c,sgn in SIGNS.items():
  x=num(train[c])*sgn;med=float(x.median());x=x.fillna(med)
  edges=np.unique(np.quantile(x,[0,.2,.4,.6,.8,1.0]))
  if len(edges)<3:
   lo=float(x.min());hi=float(x.max());edges=np.array([lo-1e-9,(lo+hi)/2,hi+1e-9])
  else:
   edges[0]-=1e-9;edges[-1]+=1e-9
  bins=np.clip(np.digitize(x,edges[1:-1],right=False),0,len(edges)-2);k=len(edges)-1;llr=[]
  for bi in range(k):
   nr=int(((bins==bi)&(y==1)).sum());nc=int(((bins==bi)&(y==0)).sum())
   pr=(nr+1)/(int((y==1).sum())+k);pc=(nc+1)/(int((y==0).sum())+k);llr.append(float(np.log(pr/pc)))
  spec[c]={"sign":sgn,"median":med,"edges":edges.tolist(),"llr":llr}
 return spec

def apply_sellr(df,spec):
 score=np.zeros(len(df),float)
 for c,s in spec.items():
  x=(num(df[c])*s["sign"]).fillna(s["median"]).to_numpy(float);edges=np.asarray(s["edges"],float)
  bins=np.clip(np.digitize(x,edges[1:-1],right=False),0,len(edges)-2);score+=np.asarray(s["llr"])[bins]
 return score

def metric(y,p):
 y=np.asarray(y,int);p=np.asarray(p,float);d=(p>=.5).astype(int)
 tp=int(((y==1)&(d==1)).sum());tn=int(((y==0)&(d==0)).sum());fp=int(((y==0)&(d==1)).sum());fn=int(((y==1)&(d==0)).sum())
 up=tp/max(tp+fn,1);dn=tn/max(tn+fp,1)
 return {"n":len(y),"accuracy":float((d==y).mean()),"balanced_accuracy":float((up+dn)/2),"up_recall":float(up),"down_recall":float(dn)}

def action_stats(q,mask):
 a=q[mask].copy();res=int((~a.baseline_correct).sum());br=int(a.baseline_correct.sum());monthly={}
 if len(a):
  a["net"]=np.where(a.baseline_correct,-1,1);a["month"]=a.start_utc.dt.to_period("M").astype(str);monthly=a.groupby("month").net.sum().to_dict()
 return {"actions":int(len(a)),"rescue":res,"broken":br,"net":res-br,"precision":res/max(len(a),1),"rate":len(a)/max(len(q),1),
         "worst_month":min(monthly.values()) if monthly else 0,"monthly":monthly}

def select_sellr(z):
 grids=[];sels=[]
 for (part,win),g0 in z.groupby(["partition","window"],sort=True):
  g=g0.sort_values("start_utc").copy();tr=g[g.start_utc.dt.year.eq(2023)].dropna(subset=FEATS+["reversal_target"])
  de=g[g.start_utc.dt.year.eq(2024)].copy()
  if len(tr)<MIN_SELLR_TRAIN or de.empty:continue
  spec=fit_sellr(tr);g["sellr_score"]=apply_sellr(g,spec)
  train_scores=g.loc[g.start_utc.dt.year.eq(2023),"sellr_score"].to_numpy(float)
  candidates=[]
  for ql in QLEVELS:
   th=float(np.quantile(train_scores,ql));m=(de.sellr_score>=th)&de.baseline_pred.eq(de.momentum_up.astype(int));st=action_stats(de,m)
   eligible=st["actions"]>=4 and st["precision"]>=.60 and st["net"]>0 and st["rate"]<=.15 and st["worst_month"]>=-1
   row={"partition":part,"window":win,"quantile":ql,"threshold":th,**{k:v for k,v in st.items() if k!="monthly"},"eligible":eligible,"monthly_json":json.dumps(st["monthly"],sort_keys=True)}
   grids.append(row)
   if eligible:candidates.append(row)
  if candidates:
   candidates=sorted(candidates,key=lambda r:(-r["net"],-r["precision"],r["actions"],-r["quantile"]))
   sel=candidates[0].copy();sel["spec_json"]=json.dumps(spec);sels.append(sel)
  z.loc[g.index,"sellr_score"]=g.sellr_score
 return z,pd.DataFrame(grids),pd.DataFrame(sels)

def simulate(g,phase_col,threshold):
 events=g[g.handoff_alarm].sort_values("start_utc").copy()
 trust=False;broken=0;pending=[];rows=[]
 for r in events.itertuples(index=False):
  now=pd.Timestamp(r.start_utc);m=[p for p in pending if p["maturity"]<=now];pending=[p for p in pending if p["maturity"]>now]
  for p in sorted(m,key=lambda x:(x["maturity"],x["origin"])):
   if p["acted"] and trust:
    if p["y"]==1:broken=0
    else:
     broken+=1
     if broken>=2:trust=False;broken=0
  catalyst=bool(float(r.sellr_score)>=threshold)
  if (not trust) and catalyst:trust=True;broken=0
  prephase=bool(getattr(r,phase_col)) if not trust else False
  acted=bool(trust or prephase);mode="TRUST" if trust else ("PHASE" if prephase else "KEEP")
  rows.append({"start_utc":now,"end_utc":r.end_utc,"acted":acted,"mode":mode,"catalyst":catalyst,"competence_y":int(r.competence_y),
               "baseline_pred":int(r.baseline_pred),"y_up":int(r.y_up)})
  pending.append({"origin":now,"maturity":pd.Timestamp(r.end_utc),"y":int(r.competence_y),"acted":acted})
 return pd.DataFrame(rows)

def main():
 if "PREREGISTERED BEFORE SESSION-SELLR / DPTC DEVELOPMENT RESULTS" not in PREREG.read_text():raise RuntimeError("PREREG_MISSING")

 path=add_trend_age(bocpd.build_path_panel())
 feat,topocal=attach_daily(path)
 base,_=bocpd.load_frozen_bases()
 z=base.merge(feat[["partition","window","start_utc","momentum_up","reversal_target"]+FEATS+["phase_q95","phase_q99","topology_date","cme_trade_date"]],
              on=["partition","window","start_utc"],how="inner",validate="one_to_one")
 z["baseline_pred"]=(z.p_up>=.5).astype(int);z["baseline_correct"]=z.baseline_pred.eq(z.y_up.astype(int))

 cov=[]
 for (part,win),g in z.groupby(["partition","window"]):
  cov.append({"partition":part,"window":win,"n":len(g),"n2023":int((g.start_utc.dt.year==2023).sum()),"n2024":int((g.start_utc.dt.year==2024).sum()),
              "first":g.start_utc.min(),"last":g.start_utc.max()})
 pd.DataFrame(cov).to_csv(OUT/"feature_coverage.csv",index=False)

 z,grid,selected=select_sellr(z)
 grid.to_csv(OUT/"sellr_grid.csv",index=False);selected.drop(columns=["spec_json"],errors="ignore").to_csv(OUT/"sellr_selected.csv",index=False)

 # Exact canonical Handoff state from BASE source mapping.
 archives=bocpd.load_archives()
 ifbc=bocpd.apply_ifbc_calibration(bocpd.build_ifbc_raw(path,archives,BASEMAP))
 llrs=bocpd.build_llrs(path,bocpd.sync_hourly(archives,BASEMAP))
 state=bocpd.build_handoff_state(ifbc,llrs)
 z=z.merge(state[["partition","window","start_utc","leadlag_score_premax","internal_now","internal_d1"]],
           on=["partition","window","start_utc"],how="inner",validate="one_to_one")
 z["handoff_alarm"]=(z.leadlag_score_premax>=.60)&(z.internal_now>=.60)&(z.internal_d1>=0)&z.baseline_pred.eq(z.momentum_up.astype(int))
 z["competence_y"]=(~z.baseline_correct).astype(int)

 metrics=[];actions=[];gates=[]
 for sel in selected.itertuples(index=False):
  g=z[(z.partition==sel.partition)&(z.window==sel.window)&(z.start_utc.dt.year==2024)].copy()
  if g.empty:continue
  for variant,pc in [("Q95","phase_q95"),("Q99","phase_q99")]:
   ev=simulate(g,pc,float(sel.threshold))
   acted=ev[ev.acted].copy()
   actkeys=set(acted.start_utc)
   g["p_assisted"]=g.p_up.astype(float)
   mact=g.start_utc.isin(actkeys);g.loc[mact,"p_assisted"]=1-g.loc[mact,"p_up"]
   mb=metric(g.y_up,g.p_up);ma=metric(g.y_up,g.p_assisted)
   res=int(acted.competence_y.sum()) if len(acted) else 0;br=int(len(acted)-res);monthly={}
   if len(acted):
    acted["net"]=np.where(acted.competence_y==1,1,-1);acted["month"]=acted.start_utc.dt.to_period("M").astype(str);monthly=acted.groupby("month").net.sum().to_dict()
    aa=acted.copy();aa["partition"]=sel.partition;aa["window"]=sel.window;aa["variant"]=variant;actions.append(aa)
   worst=min(monthly.values()) if monthly else 0;prec=res/max(len(acted),1)
   eligible=len(acted)>=4 and (res-br)>0 and prec>=.60 and ma["balanced_accuracy"]+1e-12>=mb["balanced_accuracy"] and ma["accuracy"]+1e-12>=mb["accuracy"] and worst>=-1
   row={"partition":sel.partition,"window":sel.window,"variant":variant,"sellr_quantile":sel.quantile,"sellr_threshold":sel.threshold,
        "eligible_n":len(g),"handoff_alarms":int(g.handoff_alarm.sum()),"actions":len(acted),"rescue":res,"broken":br,"net_rescue":res-br,
        "precision":prec,"phase_actions":int((acted["mode"]=="PHASE").sum()) if len(acted) else 0,
        "trust_actions":int((acted["mode"]=="TRUST").sum()) if len(acted) else 0,"worst_month_net":worst,
        "base_accuracy":mb["accuracy"],"assisted_accuracy":ma["accuracy"],"base_ba":mb["balanced_accuracy"],"assisted_ba":ma["balanced_accuracy"],
        "base_up":mb["up_recall"],"assisted_up":ma["up_recall"],"base_down":mb["down_recall"],"assisted_down":ma["down_recall"],
        "transport_eligible":eligible}
   metrics.append(row);gates.append({k:row[k] for k in ["partition","window","variant","actions","rescue","broken","net_rescue","precision","base_accuracy","assisted_accuracy","base_ba","assisted_ba","worst_month_net","transport_eligible"]})

 mdf=pd.DataFrame(metrics);gdf=pd.DataFrame(gates)
 mdf.to_csv(OUT/"dptc_metrics.csv",index=False);gdf.to_csv(OUT/"dptc_gate.csv",index=False)
 (pd.concat(actions,ignore_index=True) if actions else pd.DataFrame()).to_csv(OUT/"actions.csv",index=False)

 summary={"status":"SESSION_DPTC_STAGE2_COMPLETE","chronology":{"fit":2023,"development":2024,"2025":"CLOSED","2026":"UNREAD"},
          "topology_calibration":topocal,"sellr_selected":selected.drop(columns=["spec_json"],errors="ignore").to_dict("records"),
          "transport_eligible":gdf[gdf.transport_eligible].to_dict("records") if len(gdf) else [],
          "guardrails":["No historical H3 SELLR score/bin/threshold used.","2025 and 2026 outcomes not read.","SELLR fitted independently per partition/window on 2023 only.","DPTC state isolated per partition/window.","Only matured acted outcomes update TRUST hysteresis."]}
 (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

 lines=["# GOLD SESSION — DPTC STAGE-2 RESULT","","**Status:** SESSION_DPTC_STAGE2_COMPLETE","","2023 fits SESSION-SELLR; 2024 is development; 2025/2026 are not read.","",
        "## SESSION-SELLR selections","",
        "| Partition | Window | Q | Threshold | 2024 actions | Rescue | Broken | Net | Precision |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|"]
 if selected.empty:lines.append("| none | none | - | - | - | - | - | - | - |")
 else:
  for r in selected.itertuples(index=False):
   lines.append(f"| {r.partition} | {r.window} | {r.quantile:.2f} | {r.threshold:.4f} | {r.actions} | {r.rescue} | {r.broken} | {r.net:+d} | {100*r.precision:.1f}% |")
 lines += ["","## DPTC 2024 development","",
           "| Partition | Window | Variant | Handoff | Actions | R/B/Net | Precision | Base BA | Assisted BA | Base Acc | Assisted Acc | Gate |",
           "|---|---|---|---:|---:|---|---:|---:|---:|---:|---:|---|"]
 for r in mdf.itertuples(index=False):
  lines.append(f"| {r.partition} | {r.window} | {r.variant} | {r.handoff_alarms} | {r.actions} | {r.rescue}/{r.broken}/{r.net_rescue:+d} | {100*r.precision:.1f}% | {100*r.base_ba:.2f}% | {100*r.assisted_ba:.2f}% | {100*r.base_accuracy:.2f}% | {100*r.assisted_accuracy:.2f}% | {'PASS' if r.transport_eligible else 'FAIL'} |")
 lines += ["","## Frozen transport decision",""]
 elig=gdf[gdf.transport_eligible] if len(gdf) else pd.DataFrame()
 if elig.empty:lines.append("- **No DPTC session head is eligible to open 2025.**")
 else:
  for r in elig.itertuples(index=False):lines.append(f"- **{r.partition} / {r.window} / {r.variant}**")
 (OUT/"result.md").write_text("\n".join(lines)+"\n")
 print(json.dumps({"status":summary["status"],"transport_eligible":summary["transport_eligible"]},indent=2,default=str))

if __name__=="__main__":main()
