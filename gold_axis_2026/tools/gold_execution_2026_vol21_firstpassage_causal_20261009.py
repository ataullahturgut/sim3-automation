"""True ex-ante volatility-scaled barriers for overnight gold competing first hits.

Fixed alternative is historic ±.5% BID observed 15min closes. Adaptive only
uses strictly PREVIOUS 21 source-accepted matured overnight endpoint returns,
never future 2026 volatility or current session in its own threshold.
"""
from pathlib import Path
import sys,json,time
import numpy as np,pandas as pd
from scipy.spatial.distance import jensenshannon
AX=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(AX/"tools"))
import gold_execution_2026_firstpassage_barrier_diagnostic_20261008 as source
NAME="GOLD_EXECUTION_2026_VOL21_FIRSTPASSAGE_CAUSAL_20261009"
CLASSES=("NO_HIT","UP_FIRST","DOWN_FIRST")
LAM=1.0
def label_dynamic(fullq,t):
    # all target date rows fixed upstream, and all source-confirmed source gates
    rows=[];hist=[];last=None
    for row in t.sort_values("date").itertuples(index=False):
        d=pd.Timestamp(row.date)
        if last is not None and d<=last:raise RuntimeError("NONCHRONOLOGICAL_SOURCE_ORIGINS")
        last=d
        obs=source.per_night(fullq,row)
        if obs is None or not obs.get("accepted"):continue
        h=np.array([z[1] for z in hist[-21:]],float)
        if len(h)<21: # source-approved history from 2020 retained for later dates
            hist.append((d,float(row.ret_OVN)))
            continue
        if not np.isfinite(h).all():raise RuntimeError("STALE_OR_NAN_PRIOR_REALIZED_NIGHT")
        oldest=hist[-21][0]
        freshness=(d-oldest).days
        if freshness>65: # 21 eligible normal 16h observations should be reasonably near
            hist.append((d,float(row.ret_OVN)))
            continue
        sigma=float(np.sqrt(np.mean(h*h)))
        if not(0<sigma<.5):raise RuntimeError("EXANTE_SIGMA_ABNORMAL")
        origin=pd.Timestamp(d.date(),tz="UTC")+pd.Timedelta(hours=14)
        grid=pd.date_range(origin,periods=64,freq="15min")
        bars=fullq.reindex(grid)
        if pd.isna(bars.open.iloc[0]):raise RuntimeError("INVALID_17TR_PRICE_ANCHOR")
        entry=float(bars.open.iloc[0])
        observed=np.flatnonzero(bars.close.notna().to_numpy(bool))
        r=np.log(bars.close.to_numpy(float)[observed]/entry)
        up=np.flatnonzero(r>=LAM*sigma);down=np.flatnonzero(r<=-LAM*sigma)
        if len(up)==0 and len(down)==0: kind="NO_HIT"
        elif len(down)==0:kind="UP_FIRST"
        elif len(up)==0:kind="DOWN_FIRST"
        else:kind="UP_FIRST" if up[0]<down[0] else "DOWN_FIRST"
        if np.isnan(row.ret_OVN) or int(r[-1]>0)!=int(float(row.ret_OVN)>0):
            raise RuntimeError("CURRENT_LABEL_ALIGNMENT_MISMATCH")
        rows.append({"date":d.strftime("%Y-%m-%d"),"year":int(d.year),
          "fixed_event":obs["first_hit"],"scaled_event":kind,
          "preissue21_overnight_RMS":sigma,
          "scaled_barrier_log":float(sigma),"fixed_barrier_log":float(np.log(1.005)),
          "prior21_span_calendar_days":int(freshness),
          "endpoint_UP":int(r[-1]>0),
          "native_bar_closes":len(observed)})
        hist.append((d,float(row.ret_OVN)))
    p=pd.DataFrame(rows)
    if p.empty or p.date.duplicated().any():raise RuntimeError("BAD_EVENT_SET")
    return p

def online_probs(p):
    observations=[]
    for kind in ("fixed_event","scaled_event"):
        for row in p.itertuples(index=False):
            event=getattr(row,kind)
            sourceyear=int(row.year)
            seen=p[p.date<row.date]
            previous=seen[seen.year==sourceyear-1]
            if sourceyear<2023:continue
            for baseline in ("PREVIOUS_CALENDAR_YEAR","TRAILING63_DIRICHLET"):
                use=previous if baseline=="PREVIOUS_CALENDAR_YEAR" else seen.tail(63)
                if len(use)<60:continue
                freq=np.bincount([CLASSES.index(e) for e in use[kind]],minlength=3).astype(float)
                if baseline=="TRAILING63_DIRICHLET":freq+=1
                pr=freq/freq.sum()
                outcome=CLASSES.index(event)
                observations.append({"date":row.date,"year":sourceyear,
                    "label_type":kind,"model":baseline,"event":event,
                    "p_nohit":float(pr[0]),"p_upfirst":float(pr[1]),
                    "p_downfirst":float(pr[2]),"y":outcome,
                    "observed_n_prior":len(use),
                    "true_brier":float(np.square(pr-np.eye(3)[outcome]).sum())})
    a=pd.DataFrame(observations)
    return a

def describe(events,scores,name):
    rows=[];out=[]
    for (year),g in events.groupby("year"):
        if year<2023:continue
        r={"source_test":name,"year":int(year),"n":len(g),
           "median_exante_barrier_pct":float(g.scaled_barrier_log.median()*100),
           "exante_barrier_IQR_pct":float((g.scaled_barrier_log.quantile(.75)-g.scaled_barrier_log.quantile(.25))*100)}
        for typ in ("fixed_event","scaled_event"):
            freq=np.bincount([CLASSES.index(s) for s in g[typ]],minlength=3)
            r[typ+"_hit_fraction"]=float(1-freq[0]/len(g))
            for i,c in enumerate(CLASSES):
                r[typ+"_"+c+"_fraction"]=float(freq[i]/len(g))
            first_opposite=((g[typ].eq("UP_FIRST")&g.endpoint_UP.eq(0))|
                (g[typ].eq("DOWN_FIRST")&g.endpoint_UP.eq(1)))
            r[typ+"_first_opposite_final_n"]=int(first_opposite.sum())
        rows.append(r)
    year_df=pd.DataFrame(rows)
    for (year,kind,model),g in scores.groupby(["year","label_type","model"]):
        out.append({"source_test":name,"year":int(year),"label_type":kind,
           "baseline":model,"n":len(g),"multiclass_Brier":float(g.true_brier.mean()),
           "DOWN_FIRST_recall_if_maxprior":float(np.mean(
             g.loc[g.y==2,["p_nohit","p_upfirst","p_downfirst"]].to_numpy().argmax(axis=1)==2))
             if (g.y==2).any() else None})
    metric=pd.DataFrame(out)
    for typ in ("fixed_event","scaled_event"):
        if 2025 not in year_df.year.to_numpy() or 2026 not in year_df.year.to_numpy():continue
        q=year_df.set_index("year")
        a=np.array([q.loc[2025,typ+"_"+c+"_fraction"] for c in CLASSES],float)
        b=np.array([q.loc[2026,typ+"_"+c+"_fraction"] for c in CLASSES],float)
        dist=float(jensenshannon(a,b,base=2))
        print("JENSEN_SHANNON_2025_TO_2026",name,typ,dist,flush=True)
        year_df[typ+"_JSD_2025_TO_2026"]=dist
    return year_df,metric

def main():
    tic=time.time()
    q,t,sets=source.source_sets()
    summaries=[];model=[];preds=[]
    for name,moreq,moret in sets:
       combined=pd.concat([q,moreq]).sort_index()
       if combined.index.duplicated().any():raise RuntimeError("OVERLAP_QUOTE_ORIGIN")
       dates=pd.concat([t,moret],ignore_index=True).sort_values("date")
       if dates.date.duplicated().any():raise RuntimeError("OVERLAP_EVENT_ORIGIN")
       labels=label_dynamic(combined,dates)
       s=online_probs(labels)
       d,m=describe(labels,s,name)
       summaries.append(d);model.append(m)
       labels["source_test"]=name
       preds.append(labels)
       print("CAUSAL_VOL21_FIRSTPASSAGE",name,d.to_string(index=False),flush=True)
    root=str(AX/NAME)
    years=pd.concat(summaries,ignore_index=True)
    baselines=pd.concat(model,ignore_index=True)
    years.to_csv(root+"_YEAR_METRICS.csv",index=False)
    baselines.to_csv(root+"_BAYESIAN_BASELINE.csv",index=False)
    pd.concat(preds,ignore_index=True).to_csv(root+"_PRIVATE_DATED.csv",index=False)
    state={"status":"ACTUAL_EXANTE_21NIGHT_RMS_VOL_SCALED_COMPETING_PASSAGE_AUDIT",
       "first_barrier_definition":"observed bid close crossing log+/- 1x previous21 regular overnight RMS",
       "fixed_comparator":"exact same dates BID 15m-close +/-0.5% original barrier",
       "only_previous_matured_overnights":True,
       "prior_history_min":21,"max_lag21_span_days":65,
       "2026_stress_inspected":True,
       "no_intrabar_touch_or_bank_execution":True,
       "not_signed_direction_model_accuracy":True,
       "training_2026_futures_NOT_USED":True,
       "elapsed_sec":int(time.time()-tic)}
    Path(root+"_SUMMARY.json").write_text(json.dumps(state,indent=2)+"\n")
    print("CAUSAL_21BAR_VOLATILITY_BARRIER_BASELINES",baselines.to_string(index=False),flush=True)
    print("CAUSAL_21NIGHT_VOL_QC",json.dumps(state),flush=True)
if __name__=="__main__":
    try:main()
    except Exception as e:
        import traceback
        fr=traceback.extract_tb(e.__traceback__)[-1]
        obj={"status":"EXANTE_VOL_FIRSTPASSAGE_AUDIT_BLOCKED",
           "reason":str(e)[:160],"reason_type":type(e).__name__,
           "function":fr.name,"line":fr.lineno}
        (AX/(NAME+"_FAILURE_QC.json")).write_text(json.dumps(obj,indent=2)+"\n")
        print("CAUSAL_VOL21_FAIL",json.dumps(obj),flush=True)
