from pathlib import Path
import json, math
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
PANEL=AX/"GOLD_H3_RTE_V1_FEATURE_PANEL_2026-10-03.csv"
MACRO=AX/"GOLD_H3_MACRO_EVENT_CATALYST_RAW_2026-10-04.csv"

OUT_PANEL=AX/"GOLD_H3_EVENT_HAZARD_PANEL_2026-10-04.csv"
OUT_SUM=AX/"GOLD_H3_EVENT_HAZARD_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_EVENT_HAZARD_RESULT_2026-10-04.md"

def robust_z_expanding(x):
    out=[]
    hist=[]
    for v in x:
        if len(hist)<12:
            out.append(np.nan)
        else:
            a=np.asarray(hist,float)
            med=np.nanmedian(a)
            mad=np.nanmedian(np.abs(a-med))
            scale=1.4826*mad
            if not np.isfinite(scale) or scale<1e-9:
                scale=np.nanstd(a)
            out.append((v-med)/scale if np.isfinite(scale) and scale>1e-9 else 0.0)
        hist.append(v)
    return np.asarray(out,float)

def macro_events():
    m=pd.read_csv(MACRO)
    m["observation_ts"]=pd.to_datetime(m.observation_ts,utc=True)
    m["event_date"]=m.observation_ts.dt.tz_convert("America/New_York").dt.date
    m["available_as_of"]=pd.to_datetime(m.available_as_of,utc=True,errors="coerce")

    emp=m[m.event_type=="EMPLOYMENT"].copy().sort_values("observation_ts")
    emp=emp.dropna(subset=["nfp_actual","nfp_consensus","unemp_actual","unemp_consensus","ahe_actual","ahe_consensus"])
    emp["nfp_surprise"]=emp.nfp_actual-emp.nfp_consensus
    emp["unemp_surprise"]=emp.unemp_actual-emp.unemp_consensus
    emp["ahe_surprise"]=emp.ahe_actual-emp.ahe_consensus
    emp["z_nfp"]=robust_z_expanding(emp.nfp_surprise.to_numpy(float))
    emp["z_unemp"]=robust_z_expanding(emp.unemp_surprise.to_numpy(float))
    emp["z_ahe"]=robust_z_expanding(emp.ahe_surprise.to_numpy(float))
    # Positive score = gold-bullish labor surprise: weaker jobs/higher unemployment/weaker earnings.
    emp["gold_emp_score"]=(-emp.z_nfp + emp.z_unemp - emp.z_ahe)/3.0

    inf=m[m.event_type=="INFLATION"].copy().sort_values("observation_ts")
    fomc=m[m.event_type=="FOMC"].copy().sort_values("observation_ts")
    return emp,inf,fomc

def in_window(events,start,end):
    d=events.event_date
    return bool(((d>start)&(d<=end)).any())

def last_emp(emp,cutoff):
    q=emp[emp.event_date<=cutoff].copy()
    if q.empty: return None
    return q.iloc[-1]

def summarize_group(df,mask,name):
    q=df[mask].copy()
    n=len(q)
    rev=int(q.rescue_target.sum()) if n else 0
    rate=rev/max(n,1)
    return {"group":name,"n":n,"v5_missed_reversal_n":rev,"v5_error_rate":rate}

def flip_diag(df,mask,name):
    q=df[mask].copy()
    n=len(q)
    rescue=int(q.rescue_target.sum())
    broken=n-rescue
    return {"rule":name,"candidate_n":n,"rescued":rescue,"broken":broken,"net":rescue-broken,
            "precision":rescue/max(n,1)}

def main():
    emp,inf,fomc=macro_events()

    p=pd.read_csv(PANEL)
    for c in ["feature_cutoff_date","forecast_issue_date","target_end_date_h3"]:
        p[c]=pd.to_datetime(p[c])
    p=p[p.eligible_v5_continuation.astype(bool)].copy().sort_values("forecast_issue_date")
    p["cutoff_date"]=p.feature_cutoff_date.dt.date
    p["end_date"]=p.target_end_date_h3.dt.date

    rows=[]
    for r in p.itertuples():
        future_emp=in_window(emp,r.cutoff_date,r.end_date)
        future_inf=in_window(inf,r.cutoff_date,r.end_date)
        future_fomc=in_window(fomc,r.cutoff_date,r.end_date)
        le=last_emp(emp,r.cutoff_date)
        if le is None or not np.isfinite(le.gold_emp_score):
            emp_days=np.nan; emp_score=np.nan
        else:
            emp_days=(r.cutoff_date-le.event_date).days
            emp_score=float(le.gold_emp_score)
        sign=1.0 if int(r.momentum_up)==1 else -1.0
        shock_against=-sign*emp_score if np.isfinite(emp_score) else np.nan
        d=r._asdict()
        d.update({
            "future_emp_event":future_emp,
            "future_inflation_event":future_inf,
            "future_fomc_event":future_fomc,
            "future_any_major_event":future_emp or future_inf or future_fomc,
            "days_since_emp":emp_days,
            "last_emp_gold_score":emp_score,
            "emp_shock_against_momentum":shock_against,
            "recent_emp_1d":bool(np.isfinite(emp_days) and emp_days<=1),
            "recent_emp_3d":bool(np.isfinite(emp_days) and emp_days<=3),
        })
        rows.append(d)

    z=pd.DataFrame(rows)
    z.to_csv(OUT_PANEL,index=False)

    groups=[]
    for col in ["future_any_major_event","future_emp_event","future_inflation_event","future_fomc_event","recent_emp_1d","recent_emp_3d"]:
        groups.append(summarize_group(z,z[col].astype(bool),col+"=1"))
        groups.append(summarize_group(z,~z[col].astype(bool),col+"=0"))

    flips=[]
    flips.append(flip_diag(z,z.future_any_major_event.astype(bool),"FLIP_ON_ANY_FUTURE_MAJOR_EVENT"))
    flips.append(flip_diag(z,z.future_emp_event.astype(bool),"FLIP_ON_FUTURE_EMPLOYMENT"))
    flips.append(flip_diag(z,z.future_inflation_event.astype(bool),"FLIP_ON_FUTURE_INFLATION"))
    flips.append(flip_diag(z,z.future_fomc_event.astype(bool),"FLIP_ON_FUTURE_FOMC"))

    for days in [1,3]:
        recent=z.days_since_emp.notna()&(z.days_since_emp<=days)
        for th in [0.0,.5,1.0]:
            mask=recent&(z.emp_shock_against_momentum>=th)
            flips.append(flip_diag(z,mask,f"FLIP_RECENT_EMP_{days}D_AGAINST_GE_{th:.1f}"))

    # 2026 diagnosed missed reversal / OPAL-no-candidate slice.
    opal= z.opal_override_check.astype(str).str.lower().isin(["true","1","yes"])
    miss26=(z.year==2026)&(z.rescue_target==1)&(~opal)
    missstats={
        "n":int(miss26.sum()),
        "future_any":int((miss26&z.future_any_major_event).sum()),
        "future_emp":int((miss26&z.future_emp_event).sum()),
        "future_inflation":int((miss26&z.future_inflation_event).sum()),
        "future_fomc":int((miss26&z.future_fomc_event).sum()),
        "recent_emp_3d":int((miss26&z.recent_emp_3d).sum()),
    }

    # Per-year event hazard.
    yearly=[]
    for y,g in z.groupby("year"):
        for event_flag in [False,True]:
            q=g[g.future_any_major_event==event_flag]
            yearly.append({
                "year":int(y),"future_event":event_flag,"n":len(q),
                "error_n":int(q.rescue_target.sum()),
                "error_rate":float(q.rescue_target.mean()) if len(q) else np.nan
            })

    out={"groups":groups,"flip_diagnostics":flips,"missed_2026_opal_no_candidate":missstats,"yearly":yearly,
         "employment_events_complete":len(emp),"inflation_schedule_events":len(inf),"fomc_schedule_events":len(fomc)}
    OUT_SUM.write_text(json.dumps(out,indent=2,default=str)+"\n")

    lines=["# GOLD H3 — MACRO EVENT HAZARD / CATALYST DIAGNOSTIC","",
           "**Status:** retrospective mechanism diagnostic; not a new clean holdout.","",
           "Academic mechanism: gold futures react materially and asymmetrically to macroeconomic surprises, especially employment/inflation and FOMC-related shocks. This experiment tests whether the H3 reversal error is concentrated around such events.","",
           "## V5 error-rate anatomy","",
           "| Group | n | Missed reversals | Error rate |",
           "|---|---:|---:|---:|"]
    for x in groups:
        lines.append(f"| {x['group']} | {x['n']} | {x['v5_missed_reversal_n']} | {100*x['v5_error_rate']:.2f}% |")

    lines += ["","## Simple intervention diagnostics","",
              "| Rule | Candidates | Rescue | Broken | Net | Precision |",
              "|---|---:|---:|---:|---:|---:|"]
    for x in flips:
        lines.append(f"| {x['rule']} | {x['candidate_n']} | {x['rescued']} | {x['broken']} | {x['net']:+d} | {100*x['precision']:.2f}% |")

    lines += ["","## 2026 V5-missed / OPAL-no-candidate reversal slice","",
              f"- total: **{missstats['n']}**",
              f"- H3 window contains any major event: **{missstats['future_any']}**",
              f"- employment: **{missstats['future_emp']}**",
              f"- inflation: **{missstats['future_inflation']}**",
              f"- FOMC: **{missstats['future_fomc']}**",
              f"- employment release occurred within prior 3 calendar days: **{missstats['recent_emp_3d']}**",
              "",
              "## Year-by-year any-event hazard","",
              "| Year | Future major event | n | V5 errors | Error rate |",
              "|---:|---|---:|---:|---:|"]
    for x in yearly:
        lines.append(f"| {x['year']} | {x['future_event']} | {x['n']} | {x['error_n']} | {100*x['error_rate']:.2f}% |")

    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
