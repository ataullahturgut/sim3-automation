from __future__ import annotations

import json
import math
import os
import time
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg
import requests
from requests.adapters import HTTPAdapter
from scipy.special import gammaln, logsumexp
from urllib3.util.retry import Retry

IDENTITY = "BOCPD_HOURLY_VARIANCE_BMA_SUCCESSOR_V3_RESEARCH"
HOURLY_SERIES = "XAU_USD_TWELVE_1H_RESEARCH_V1"
DAILY_SERIES = "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1"
API_URL = "https://api.twelvedata.com/time_series"
SYMBOL = "XAU/USD"
NY_TZ = "America/New_York"
OUTPUTSIZE = 5000
EXPECTED_HOURS = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,19,20,21,22,23]
LAMBDA_DAYS = [10,20,40,60,120]
LAMBDA_OBS = [x*22 for x in LAMBDA_DAYS]
RECENT_K = [6,12,22]
THRESHOLDS = [0.5,0.7,0.85,0.95]
PERSISTENCE = [1,2,3]
HORIZONS = [48,72,120]
MAX_RUN = 5000
FROZEN_2025_EVENTS = [
    "2025-02-10","2025-02-14","2025-02-18","2025-03-13","2025-04-04",
    "2025-04-09","2025-04-10","2025-07-21","2025-08-01","2025-09-02",
    "2025-09-22","2025-09-29","2025-10-06","2025-10-13","2025-10-16",
    "2025-10-17","2025-10-21","2025-12-22","2025-12-29",
]


def secret(name: str) -> str:
    v=os.environ.get(name,"").strip()
    if not v: raise RuntimeError(f"{name}_MISSING")
    return v


def http_session() -> requests.Session:
    s=requests.Session()
    retry=Retry(total=5,connect=5,read=5,backoff_factor=2.0,
                status_forcelist=(408,425,429,500,502,503,504),
                allowed_methods=frozenset(["GET"]),respect_retry_after_header=True)
    s.mount("https://",HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent":"GoldControl-BOCPD-Variance-BMA-V3/1.0","Accept":"application/json"})
    return s


def fmt_utc(ts: pd.Timestamp)->str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%S")


def session_gate(frame: pd.DataFrame, label: str)->pd.DataFrame:
    out=frame.sort_values("bar_start_utc").drop_duplicates("bar_start_utc").copy()
    local=out["bar_start_utc"].dt.tz_convert(NY_TZ)
    dow=local.dt.dayofweek; hr=local.dt.hour
    allowed=((dow==6)&(hr>=18))|((dow>=0)&(dow<=3)&((hr<=16)|(hr>=18)))|((dow==4)&(hr<=16))
    kept=out.loc[allowed].copy().reset_index(drop=True)
    print(f"SESSION_GATE label={label} raw={len(out)} kept={len(kept)} excluded={len(out)-len(kept)}")
    return kept


def load_hourly_2022_2024()->pd.DataFrame:
    sql="""
      select observation_ts,value from canonical_latest
      where series_id=%s and observation_ts>=timestamptz '2022-01-01 00:00:00+00'
        and observation_ts<timestamptz '2025-01-01 00:00:00+00'
      order by observation_ts
    """
    with psycopg.connect(secret("NEON_DATABASE_URL")) as conn:
        with conn.cursor() as cur:
            cur.execute(sql,(HOURLY_SERIES,)); rows=cur.fetchall()
    f=pd.DataFrame(rows,columns=["bar_start_utc","value"])
    f["bar_start_utc"]=pd.to_datetime(f["bar_start_utc"],utc=True)
    f["value"]=pd.to_numeric(f["value"],errors="raise").astype(float)
    if f.empty or f["bar_start_utc"].duplicated().any() or (f["value"]<=0).any():
        raise RuntimeError("INVALID_STORED_HOURLY_SOURCE")
    years=set(f["bar_start_utc"].dt.year.unique().tolist())
    if years != {2022,2023,2024}: raise RuntimeError(f"STORED_YEAR_COVERAGE:{sorted(years)}")
    return session_gate(f,"stored_2022_2024")


def fetch_2025()->pd.DataFrame:
    key=secret("TWELVE_DATA_API_KEY"); s=http_session(); rows=[]
    starts=pd.date_range(pd.Timestamp("2025-01-01",tz="UTC"),pd.Timestamp("2026-01-01",tz="UTC"),freq="QS",inclusive="left")
    for i,st in enumerate(starts,1):
        en=min(st+pd.DateOffset(months=3),pd.Timestamp("2026-01-01",tz="UTC"))
        params={"symbol":SYMBOL,"interval":"1h","start_date":fmt_utc(st),
                "end_date":fmt_utc(en-pd.Timedelta(seconds=1)),"timezone":"UTC","order":"ASC",
                "outputsize":OUTPUTSIZE,"format":"JSON","apikey":key}
        r=s.get(API_URL,params=params,timeout=(10,60)); r.raise_for_status(); p=r.json()
        if isinstance(p,dict) and p.get("status")=="error": raise RuntimeError(f"TWELVE_API_ERROR:{p.get('code')}:{p.get('message')}")
        vals=p.get("values") if isinstance(p,dict) else None
        if not vals or len(vals)>=OUTPUTSIZE: raise RuntimeError(f"INVALID_2025_CHUNK:{st.date()}:{en.date()}")
        n=0
        for x in vals:
            ts=pd.to_datetime(x.get("datetime"),errors="coerce",utc=True); val=pd.to_numeric(x.get("close"),errors="coerce")
            if pd.isna(ts) or pd.isna(val): continue
            val=float(val)
            if math.isfinite(val) and val>0 and st<=ts<en:
                rows.append((pd.Timestamp(ts),val)); n+=1
        print(f"FETCH_2025_CHUNK={i} raw_valid={n} start={st.date()} end={en.date()}"); time.sleep(2)
    f=pd.DataFrame(rows,columns=["bar_start_utc","value"]).sort_values("bar_start_utc")
    dup=f.groupby("bar_start_utc")["value"].nunique()
    if (dup>1).any(): raise RuntimeError("2025_DUPLICATE_CONFLICT")
    f=f.drop_duplicates("bar_start_utc").reset_index(drop=True)
    f=session_gate(f,"challenge_2025")
    if not (5700<=len(f)<=6100): raise RuntimeError(f"2025_IMPLAUSIBLE_SESSION_ROWS:{len(f)}")
    return f


def load_daily()->pd.DataFrame:
    sql="""
      select observation_ts,value from canonical_latest
      where series_id=%s and observation_ts>=timestamptz '2022-01-01 00:00:00+00'
        and observation_ts<timestamptz '2026-01-01 00:00:00+00'
        and extract(isodow from observation_ts at time zone 'America/New_York') between 1 and 5
      order by observation_ts
    """
    with psycopg.connect(secret("NEON_DATABASE_URL")) as conn:
        with conn.cursor() as cur:
            cur.execute(sql,(DAILY_SERIES,)); rows=cur.fetchall()
    f=pd.DataFrame(rows,columns=["bar_start_utc","value"])
    f["bar_start_utc"]=pd.to_datetime(f["bar_start_utc"],utc=True); f["value"]=pd.to_numeric(f["value"],errors="raise").astype(float)
    f["bar_start_ny"]=f["bar_start_utc"].dt.tz_convert(NY_TZ); f["local_date"]=f["bar_start_ny"].dt.strftime("%Y-%m-%d")
    f["available_at_utc"]=f["bar_start_utc"]+pd.Timedelta(hours=1)
    return f.reset_index(drop=True)


def crosscheck_2025(hourly: pd.DataFrame,daily: pd.DataFrame)->dict:
    d=daily[daily["bar_start_ny"].dt.year==2025]
    h=dict(zip(hourly["bar_start_utc"],hourly["value"])); miss=mis=0; mad=0.0
    for r in d.itertuples(index=False):
        got=h.get(r.bar_start_utc)
        if got is None: miss+=1; continue
        diff=abs(float(got)-float(r.value)); mad=max(mad,diff); mis+=int(diff>1e-9)
    if len(d)!=255 or miss or mis: raise RuntimeError(f"2025_DAILY_CROSSCHECK_FAIL:n={len(d)} miss={miss} mismatch={mis}")
    return {"n":len(d),"exact_timestamp":len(d)-miss,"exact_value":len(d)-miss-mis,"max_abs_diff":mad}


def build_returns(prices: pd.DataFrame)->pd.DataFrame:
    f=prices.sort_values("bar_start_utc").drop_duplicates("bar_start_utc").reset_index(drop=True).copy()
    f["prev_ts"]=f["bar_start_utc"].shift(1); f["prev_value"]=f["value"].shift(1)
    f["elapsed"]=(f["bar_start_utc"]-f["prev_ts"]).dt.total_seconds()/3600.0
    f["raw_return"]=np.log(f["value"]/f["prev_value"])
    f=f[np.isclose(f["elapsed"],1.0,atol=1e-12)].copy()
    f["bar_start_ny"]=f["bar_start_utc"].dt.tz_convert(NY_TZ); f["hour"]=f["bar_start_ny"].dt.hour.astype(int)
    f["available_at_utc"]=f["bar_start_utc"]+pd.Timedelta(hours=1); f["local_date"]=f["bar_start_ny"].dt.strftime("%Y-%m-%d")
    hrs=sorted(f["hour"].unique().tolist())
    if hrs!=EXPECTED_HOURS: raise RuntimeError(f"ELIGIBLE_HOURS:{hrs}")
    return f[["bar_start_utc","bar_start_ny","available_at_utc","local_date","hour","raw_return"]].reset_index(drop=True)


def fit_2022_scale(ret: pd.DataFrame)->tuple[pd.DataFrame,float]:
    d=ret[ret["bar_start_ny"].dt.year==2022]
    stats=d.groupby("hour")["raw_return"].agg(["count","std"]).reset_index()
    if sorted(stats["hour"].tolist())!=EXPECTED_HOURS or int(stats["count"].min())<150 or (stats["std"]<=0).any():
        raise RuntimeError("2022_INTRADAY_SCALE_INVALID")
    tmp=d.merge(stats[["hour","std"]],on="hour",how="left"); z=tmp["raw_return"]/tmp["std"]
    v=float(z.var(ddof=1))
    if not math.isfinite(v) or v<=0: raise RuntimeError("2022_PRIOR_VARIANCE_INVALID")
    return stats,v


def standardize(ret: pd.DataFrame,stats: pd.DataFrame)->pd.DataFrame:
    o=ret.merge(stats[["hour","std"]],on="hour",how="left",validate="many_to_one")
    if o["std"].isna().any(): raise RuntimeError("UNSEEN_HOUR")
    o["x"]=o["raw_return"]/o["std"]
    if not np.isfinite(o["x"].to_numpy()).all(): raise RuntimeError("NONFINITE_STANDARDIZED_RETURN")
    return o


def student_t_zero_logpdf(x:float,alpha:np.ndarray,beta:np.ndarray)->np.ndarray:
    nu=2.0*alpha; scale2=beta/alpha
    z2=(x*x)/scale2
    return gammaln((nu+1)/2)-gammaln(nu/2)-0.5*(np.log(nu*np.pi)+np.log(scale2))-((nu+1)/2)*np.log1p(z2/nu)


@dataclass
class FilterState:
    lam_obs:int
    logw:float
    R:np.ndarray
    alpha:np.ndarray
    beta:np.ndarray


def run_bma(stream:pd.DataFrame,alpha0:float,beta0:float)->tuple[pd.DataFrame,dict]:
    states=[FilterState(l,-math.log(len(LAMBDA_OBS)),np.array([1.0]),np.array([alpha0]),np.array([beta0])) for l in LAMBDA_OBS]
    rows=[]; max_trunc=0.0
    for r in stream.itertuples(index=False):
        x=float(r.x); log_evs=[]; staged=[]
        for st in states:
            lp=student_t_zero_logpdf(x,st.alpha,st.beta)
            lj=np.log(np.maximum(st.R,1e-300))+lp
            le=float(logsumexp(lj)); log_evs.append(le)
            h=1.0/st.lam_obs
            new_log=np.empty(len(st.R)+1)
            new_log[0]=math.log(h)+le
            new_log[1:]=math.log1p(-h)+lj
            norm=float(logsumexp(new_log)); nr=np.exp(new_log-norm)
            na=np.empty(len(st.alpha)+1); nb=np.empty(len(st.beta)+1)
            na[0]=alpha0; nb[0]=beta0; na[1:]=st.alpha+0.5; nb[1:]=st.beta+0.5*x*x
            trunc=0.0
            if len(nr)>MAX_RUN+1:
                trunc=float(nr[MAX_RUN+1:].sum()); max_trunc=max(max_trunc,trunc)
                nr=nr[:MAX_RUN+1]; na=na[:MAX_RUN+1]; nb=nb[:MAX_RUN+1]; nr/=nr.sum()
            staged.append((nr,na,nb))
        lw=np.array([st.logw for st in states])+np.array(log_evs); lw=lw-logsumexp(lw)
        for j,st in enumerate(states):
            st.logw=float(lw[j]); st.R,st.alpha,st.beta=staged[j]
        weights=np.exp(lw)
        rec={}
        for k in RECENT_K:
            rec[k]=float(sum(weights[j]*states[j].R[:min(k+1,len(states[j].R))].sum() for j in range(len(states))))
        rows.append({"bar_start_utc":r.bar_start_utc,"bar_start_ny":r.bar_start_ny,"available_at_utc":r.available_at_utc,
                     "local_date":r.local_date,"x":x,**{f"recent_p_{k}":rec[k] for k in RECENT_K},
                     **{f"hazard_w_{LAMBDA_DAYS[j]}d":float(weights[j]) for j in range(len(states))}})
    return pd.DataFrame(rows),{"max_truncated_mass":max_trunc,"final_weights":{f"{LAMBDA_DAYS[j]}d":float(math.exp(states[j].logw)) for j in range(len(states))}}


def daily_events(daily:pd.DataFrame)->pd.DataFrame:
    d=daily.copy().sort_values("bar_start_utc").reset_index(drop=True)
    d["ret_pct"]=100*np.log(d["value"]/d["value"].shift(1))
    d["sigma20"]=d["ret_pct"].shift(1).rolling(20).std(ddof=1)
    d["z"]=d["ret_pct"]/d["sigma20"]
    d["event"]=d["z"].abs()>=2.0
    d["prev_daily_available_at_utc"]=d["available_at_utc"].shift(1)
    ev=d[d["event"]].copy()
    actual=ev[ev["bar_start_ny"].dt.year==2025]["local_date"].tolist()
    if actual!=FROZEN_2025_EVENTS: raise RuntimeError(f"FROZEN_2025_EVENT_MISMATCH:{actual}")
    return ev


def episode_onsets(frame:pd.DataFrame,k:int,threshold:float,p:int)->pd.DataFrame:
    s=frame[f"recent_p_{k}"].to_numpy(); active=False; above=below=0; idx=[]
    for i,v in enumerate(s):
        if not active:
            above=above+1 if v>=threshold else 0
            if above>=p:
                onset=i-p+1; idx.append(onset); active=True; above=0; below=0
        else:
            below=below+1 if v<threshold else 0
            if below>=p:
                active=False; below=0; above=0
    if not idx: return frame.iloc[0:0].copy()
    o=frame.iloc[idx].copy(); o["score_k"]=k; o["score_threshold"]=threshold; o["persistence"]=p
    return o


def evaluate(onsets:pd.DataFrame,events:pd.DataFrame,year:int,horizon:int)->dict:
    o=onsets[onsets["bar_start_ny"].dt.year==year].copy(); e=events[events["bar_start_ny"].dt.year==year].copy()
    ot=pd.DatetimeIndex(pd.to_datetime(o["available_at_utc"],utc=True)).sort_values()
    hit_signal=0; leads=[]
    for t in ot:
        fut=e[e["available_at_utc"]>t]
        if fut.empty: continue
        er=fut.iloc[0]; lead=(er["available_at_utc"]-t).total_seconds()/3600
        if lead<=horizon and t<er["prev_daily_available_at_utc"]:
            hit_signal+=1; leads.append(float(lead))
    hit_events=0; event_leads=[]
    for er in e.itertuples(index=False):
        lo=er.available_at_utc-pd.Timedelta(hours=horizon); hi=er.prev_daily_available_at_utc
        eligible=ot[(ot>=lo)&(ot<hi)]
        if len(eligible):
            hit_events+=1; event_leads.append(float((er.available_at_utc-eligible[-1]).total_seconds()/3600))
    precision=hit_signal/len(o) if len(o) else 0.0; recall=hit_events/len(e) if len(e) else 0.0
    f1=2*precision*recall/(precision+recall) if precision+recall else 0.0
    return {"year":year,"horizon":horizon,"episodes":int(len(o)),"events":int(len(e)),"signal_hits":int(hit_signal),"event_hits":int(hit_events),
            "precision":precision,"recall":recall,"f1":f1,"median_lead_hours":float(np.median(event_leads)) if event_leads else None}


def select_2023(scores:pd.DataFrame,events:pd.DataFrame)->tuple[dict,pd.DataFrame]:
    rows=[]
    f=scores[scores["bar_start_ny"].dt.year==2023]
    for k in RECENT_K:
        for th in THRESHOLDS:
            for p in PERSISTENCE:
                on=episode_onsets(f,k,th,p)
                for h in HORIZONS:
                    m=evaluate(on,events,2023,h); m.update({"k":k,"threshold":th,"persistence":p}); rows.append(m)
    tab=pd.DataFrame(rows)
    tab=tab.sort_values(["f1","precision","episodes","horizon","threshold","persistence"],ascending=[False,False,True,True,False,False]).reset_index(drop=True)
    best=tab.iloc[0].to_dict()
    print("SELECTED_2023="+json.dumps(best,sort_keys=True,default=str))
    return best,tab


def main()->None:
    out=Path(os.environ.get("OUTPUT_DIR","bocpd_v3_output")); out.mkdir(parents=True,exist_ok=True)
    stored=load_hourly_2022_2024(); ch=fetch_2025(); daily=load_daily(); check=crosscheck_2025(ch,daily)
    prices=pd.concat([stored,ch],ignore_index=True).sort_values("bar_start_utc").drop_duplicates("bar_start_utc").reset_index(drop=True)
    ret=build_returns(prices); stats,prior_var=fit_2022_scale(ret); z=standardize(ret,stats)
    stream=z[z["bar_start_ny"].dt.year>=2023].copy().reset_index(drop=True)
    scores,bma_meta=run_bma(stream,2.0,prior_var)
    events=daily_events(daily)
    best,grid=select_2023(scores,events)
    k=int(best["k"]); th=float(best["threshold"]); p=int(best["persistence"]); h=int(best["horizon"])
    all_onsets=episode_onsets(scores,k,th,p)
    m2023=evaluate(all_onsets,events,2023,h); m2024=evaluate(all_onsets,events,2024,h); m2025=evaluate(all_onsets,events,2025,h)
    print("VALIDATION_2024="+json.dumps(m2024,sort_keys=True)); print("DIAGNOSTIC_2025="+json.dumps(m2025,sort_keys=True))

    # 2025 descriptive event overlay, keeping strict vs intraday distinction.
    on25=all_onsets[all_onsets["bar_start_ny"].dt.year==2025].copy()
    ot=pd.DatetimeIndex(pd.to_datetime(on25["available_at_utc"],utc=True)).sort_values(); overlay=[]
    e25=events[events["bar_start_ny"].dt.year==2025]
    for er in e25.itertuples(index=False):
        prior=ot[ot<er.available_at_utc]; latest=prior[-1] if len(prior) else pd.NaT
        lead=None if pd.isna(latest) else float((er.available_at_utc-latest).total_seconds()/3600)
        if pd.isna(latest): cat="NO_PRIOR_ALERT"
        elif latest<er.prev_daily_available_at_utc: cat="STRICT_PRE_EVENT_WINDOW"
        else: cat="INTRADAY_PRE_EVENT_CLOSE"
        overlay.append({"event_date":er.local_date,"latest_prior_alert":latest,"lead_hours":lead,"category":cat,
                        "clean_hit_within_selected_horizon":bool(pd.notna(latest) and latest<er.prev_daily_available_at_utc and lead<=h)})
    overlay=pd.DataFrame(overlay)

    stats.to_csv(out/"v3_2022_hour_scale.csv",index=False); scores.to_csv(out/"v3_full_scores_2023_2025.csv",index=False)
    grid.to_csv(out/"v3_2023_selection_grid.csv",index=False); all_onsets.to_csv(out/"v3_all_alert_onsets.csv",index=False); overlay.to_csv(out/"v3_2025_event_overlay.csv",index=False)
    summary={
      "identity":IDENTITY,"source_crosscheck_2025":check,
      "eligible_returns":{str(y):int((z["bar_start_ny"].dt.year==y).sum()) for y in [2022,2023,2024,2025]},
      "2022_hour_support_min":int(stats["count"].min()),"2022_hour_support_max":int(stats["count"].max()),"prior_variance":prior_var,
      "hazard_model_average":bma_meta,"selected_2023_rule":best,
      "metrics":{"2023_development":m2023,"2024_locked_validation":m2024,"2025_reused_diagnostic":m2025},
      "event_counts":{str(y):int((events["bar_start_ny"].dt.year==y).sum()) for y in [2023,2024,2025]},
      "alert_onset_counts":{str(y):int((all_onsets["bar_start_ny"].dt.year==y).sum()) for y in [2023,2024,2025]},
      "2025_overlay_categories":overlay["category"].value_counts().to_dict(),
      "2025_clean_hits_selected_horizon":int(overlay["clean_hit_within_selected_horizon"].sum()),
      "evidence_2025":"HISTORICAL_REPLAY_REUSED_CHALLENGE_DIAGNOSTIC","direction_vote":False,"runtime_promotion":"NOT_AUTHORIZED"
    }
    (out/"v3_summary.json").write_text(json.dumps(summary,indent=2,sort_keys=True,default=str),encoding="utf-8")
    print("V3_SUMMARY="+json.dumps(summary,sort_keys=True,default=str))
    print("V3_2025_OVERLAY_BEGIN")
    for r in overlay.itertuples(index=False): print(f"EVENT date={r.event_date} category={r.category} lead_hours={r.lead_hours} clean={r.clean_hit_within_selected_horizon}")
    print("V3_2025_OVERLAY_END")
    print("DATABASE_MODEL_OUTPUT_WRITES=NONE")
    print("BOCPD_V3_COMPLETE")

if __name__=="__main__": main()
