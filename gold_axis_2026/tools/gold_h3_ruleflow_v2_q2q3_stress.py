from pathlib import Path
import io, json, re
import numpy as np
import pandas as pd
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"

OUT=AX/"GOLD_H3_RULEFLOW_V2_Q2Q3_STRESS_RESULT_2026-10-04.md"
OUTCSV=AX/"GOLD_H3_RULEFLOW_V2_Q2Q3_STRESS_EVENTS_2026-10-04.csv"
OUTJ=AX/"GOLD_H3_RULEFLOW_V2_Q2Q3_STRESS_SUMMARY_2026-10-04.json"

EVENTS=[
("2026-03-13","PCE"),("2026-03-18","FOMC"),("2026-03-31","JOLTS"),
("2026-04-01","ADP"),("2026-04-03","NFP"),("2026-04-09","PCE"),("2026-04-10","CPI"),("2026-04-29","FOMC"),("2026-04-30","PCE"),
("2026-05-05","JOLTS"),("2026-05-06","ADP"),("2026-05-08","NFP"),("2026-05-12","CPI"),("2026-05-28","PCE"),
("2026-06-02","JOLTS"),("2026-06-03","ADP"),("2026-06-05","NFP"),("2026-06-10","CPI"),("2026-06-17","FOMC"),("2026-06-25","PCE"),("2026-06-30","JOLTS"),
("2026-07-01","ADP"),("2026-07-02","NFP"),("2026-07-14","CPI"),("2026-07-29","FOMC"),("2026-07-30","PCE"),
("2026-08-04","JOLTS"),("2026-08-05","ADP"),("2026-08-07","NFP"),("2026-08-12","CPI"),("2026-08-26","PCE"),
("2026-09-01","JOLTS"),("2026-09-02","ADP"),("2026-09-04","NFP"),("2026-09-11","CPI"),("2026-09-16","FOMC"),("2026-09-29","JOLTS"),("2026-09-30","PCE")
]

def load_treasury_2y():
    url="https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve&field_tdr_date_value=2026"
    html=requests.get(url,timeout=60,headers={"User-Agent":"Mozilla/5.0 academic research"}).text
    tabs=pd.read_html(io.StringIO(html))
    best=None
    for t in tabs:
        cols=[str(c).strip().lower() for c in t.columns]
        if any("date"==c or c.startswith("date") for c in cols) and any(("2-year" in c) or ("2 yr" in c) or ("2-year"==c) for c in cols):
            best=t.copy(); break
    if best is None:
        # fallback: choose widest table containing a date-like first column and a "2" tenor column
        for t in tabs:
            if t.shape[1]>=8 and any("date" in str(c).lower() for c in t.columns):
                best=t.copy(); break
    if best is None:
        raise RuntimeError("Treasury table not found")
    cmap={str(c).strip().lower():c for c in best.columns}
    date_col=next(c for c in best.columns if "date" in str(c).lower())
    two_candidates=[c for c in best.columns if re.search(r"(^|\b)2\s*(yr|year)",str(c).lower())]
    if not two_candidates:
        raise RuntimeError(f"2-year column not found: {list(best.columns)}")
    two=two_candidates[0]
    x=best[[date_col,two]].copy()
    x.columns=["date","two_y"]
    x["date"]=pd.to_datetime(x["date"],errors="coerce")
    x["two_y"]=pd.to_numeric(x["two_y"],errors="coerce")
    x=x.dropna().drop_duplicates("date").sort_values("date")
    return x

def corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    m=np.isfinite(a)&np.isfinite(b); a=a[m]; b=b[m]
    if len(a)<10: return np.nan
    va=np.std(a); vb=np.std(b)
    if va<=1e-12 or vb<=1e-12: return np.nan
    return float(np.corrcoef(a,b)[0,1])

def erank(a,v):
    a=np.asarray(a,float); a=a[np.isfinite(a)]
    return float((1+np.sum(a<=v))/(len(a)+1)) if len(a) else np.nan

def load_model():
    v=pd.read_csv(V5,parse_dates=["feature_cutoff_date"])
    p=pd.read_csv(PANEL,parse_dates=["feature_cutoff_date"])
    d=pd.read_csv(DIV,parse_dates=["feature_cutoff_date"])
    z=v.merge(p,on="feature_cutoff_date",how="inner",suffixes=("","_p"))
    z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
    return z.sort_values("feature_cutoff_date").reset_index(drop=True),d.sort_values("feature_cutoff_date").reset_index(drop=True)

def build():
    tsy=load_treasury_2y()
    levels={r.date.strftime("%Y-%m-%d"):float(r.two_y) for r in tsy.itertuples()}
    z,d=load_model()
    rows=[]
    enriched=[]
    for date,event in EVENTS:
        if date not in levels:
            enriched.append((date,event,np.nan))
        else:
            enriched.append((date,event,levels[date]))
    for i,(date,event,y2) in enumerate(enriched):
        if i<3 or not np.isfinite(y2): continue
        # require previous 3 event levels
        prev3=enriched[i-3:i]
        if any(not np.isfinite(x[2]) for x in prev3): continue
        steps=[100*(enriched[j][2]-enriched[j-1][2]) for j in range(i-2,i+1)]
        gross=float(sum(abs(x) for x in steps)); net=float(sum(steps))
        cr=(gross-abs(net))/gross if gross>0 else 0.0
        dom=abs(steps[-1])/gross if gross>0 else 0.0
        hotspot=bool(cr>0.359 and dom>0.294 and dom<=0.502)

        dt=pd.Timestamp(date)
        q=z[z.feature_cutoff_date==dt]
        if q.empty:
            rows.append(dict(date=date,event=event,two_y=y2,available=False,reason="no_h3_origin",
                             conflict_ratio=cr,current_dominance=dom,hotspot=hotspot))
            continue
        r=q.iloc[-1]
        zi=int(q.index[-1])
        hist=z.iloc[max(0,zi-120):zi]
        specs=[("trend_strength",-1),("session_against_trend",1),("trend_close_location",-1),("adverse_excursion",1)]
        ranks=[erank(s*hist[c].astype(float).to_numpy(),s*float(r[c])) for c,s in specs]
        sus=float(np.median(ranks)) if np.isfinite(ranks).all() else np.nan

        di=d.index[d.feature_cutoff_date==dt]
        breadth=np.nan
        if len(di):
            j=int(di[0]); h=d.iloc[max(0,j-60):j]
            g=h.gold_daily_ret1.astype(float).to_numpy()
            cs=[corr(g,h[c].astype(float).to_numpy()) for c in ["usd_ret1","tnx_chg1","ndx_ret1","vix_ret1"]]
            cs=[abs(x) for x in cs if np.isfinite(x)]
            breadth=float(np.mean(cs)) if cs else np.nan

        gate=bool((np.isfinite(sus) and sus>=0.60) or (np.isfinite(breadth) and breadth>=0.30))
        mom=int(r.momentum_up); pred=int(r.v5_pred); y=int(r.y_up)
        candidate=bool(hotspot and gate and pred==mom)
        rescue=bool(candidate and pred!=y)
        broken=bool(candidate and pred==y)
        rows.append(dict(date=date,event=event,two_y=y2,available=True,
                         step_bp=steps[-1],gross3=gross,conflict_ratio=cr,current_dominance=dom,
                         hotspot=hotspot,susceptibility=sus,macro_breadth=breadth,gate=gate,
                         momentum_up=mom,y_up=y,v5_pred=pred,
                         reversal=bool(y!=mom),v5_follows=bool(pred==mom),
                         candidate=candidate,rescue=rescue,broken=broken,
                         h3_return=float(r.target_r3)))
    return pd.DataFrame(rows)

def summarize(q,label):
    a=q[q.available==True].copy()
    cand=a[a.candidate==True]
    hot=a[a.hotspot==True]
    gh=a[(a.hotspot==True)&(a.gate==True)]
    non=a[~((a.hotspot==True)&(a.gate==True))]
    return {
        "period":label,"n":len(a),"hotspots":len(hot),"gated_hotspots":len(gh),
        "actions":len(cand),"rescue":int(cand.rescue.sum()),"broken":int(cand.broken.sum()),
        "net":int(cand.rescue.sum()-cand.broken.sum()),
        "precision":float(cand.rescue.mean()) if len(cand) else np.nan,
        "gated_reversal_rate":float(gh.reversal.mean()) if len(gh) else np.nan,
        "nongated_reversal_rate":float(non.reversal.mean()) if len(non) else np.nan,
    }

def main():
    q=build()
    q.to_csv(OUTCSV,index=False)
    qa=q[(q.date>="2026-04-01")&(q.date<="2026-09-30")].copy()
    q2=qa[(qa.date<="2026-06-30")]
    q3=qa[(qa.date>="2026-07-01")]
    s_all=summarize(qa,"Q2-Q3")
    s2=summarize(q2,"Q2")
    s3=summarize(q3,"Q3")
    summary={"rule":{"conflict_gt":0.359,"dominance_gt":0.294,"dominance_le":0.502,
                     "susceptibility_ge":0.60,"macro_breadth_ge":0.30,"gate":"OR"},
             "Q2":s2,"Q3":s3,"Q2Q3":s_all,
             "unavailable":qa[qa.available==False][["date","event","reason"]].to_dict("records"),
             "actions":qa[qa.candidate==True][["date","event","conflict_ratio","current_dominance","susceptibility","macro_breadth","rescue","broken","h3_return"]].to_dict("records")}
    OUTJ.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD H3 — RULEFLOW V2 2026 Q2-Q3 STRESS RESULT","",
           "**Rule was frozen before this run. No threshold changes.**","",
           "## Summary","",
           "| Period | N | Hotspots | Gated hotspots | Actions | Rescue | Broken | Net | Precision | Gated reversal | Other reversal |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for s in [s2,s3,s_all]:
        pr="—" if not np.isfinite(s["precision"]) else f"{100*s['precision']:.1f}%"
        gr="—" if not np.isfinite(s["gated_reversal_rate"]) else f"{100*s['gated_reversal_rate']:.1f}%"
        nr="—" if not np.isfinite(s["nongated_reversal_rate"]) else f"{100*s['nongated_reversal_rate']:.1f}%"
        lines.append(f"| {s['period']} | {s['n']} | {s['hotspots']} | {s['gated_hotspots']} | {s['actions']} | {s['rescue']} | {s['broken']} | {s['net']:+d} | {pr} | {gr} | {nr} |")
    lines += ["","## Actions","",
              "| Date | Event | Conflict | Dominance | Susceptibility | Macro breadth | Rescue | Broken | H3 return |",
              "|---|---|---:|---:|---:|---:|---|---|---:|"]
    for r in summary["actions"]:
        lines.append(f"| {r['date']} | {r['event']} | {r['conflict_ratio']:.3f} | {r['current_dominance']:.3f} | {r['susceptibility']:.3f} | {r['macro_breadth']:.3f} | {r['rescue']} | {r['broken']} | {100*r['h3_return']:+.2f}% |")
    if summary["unavailable"]:
        lines += ["","## Unavailable event origins",""]
        for r in summary["unavailable"]:
            lines.append(f"- {r['date']} {r['event']}: {r['reason']}")
    OUT.write_text("\n".join(lines)+"\n")
    print(OUT.read_text())

if __name__=="__main__":
    main()
