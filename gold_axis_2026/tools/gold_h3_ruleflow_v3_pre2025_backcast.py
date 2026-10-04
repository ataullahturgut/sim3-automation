from pathlib import Path
import json
import urllib.request
import numpy as np
import pandas as pd
from scipy.stats import pearsonr

ROOT = Path(__file__).resolve().parents[2]
AX = ROOT / "gold_axis_2026"

V5 = AX / "GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PANEL = AX / "GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
DIV = AX / "GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"

OUT_CSV = AX / "GOLD_H3_RULEFLOW_V3_PRE2025_BACKCAST_EVENTS_2026-10-04.csv"
OUT_SUM = AX / "GOLD_H3_RULEFLOW_V3_PRE2025_BACKCAST_SUMMARY_2026-10-04.json"
OUT_MD = AX / "GOLD_H3_RULEFLOW_V3_PRE2025_BACKCAST_RESULT_2026-10-04.md"
OUT_DGS2 = AX / "GOLD_H3_RULEFLOW_V3_PRE2025_DGS2_SOURCE_2026-10-04.csv"

ALPHA = 0.05

EVENTS = {
    2023: {
        "ADP": ["2023-01-05","2023-02-01","2023-03-08","2023-04-05","2023-05-03","2023-06-01","2023-07-06","2023-08-02","2023-08-30","2023-10-04","2023-11-01","2023-12-06"],
        "NFP": ["2023-01-06","2023-02-03","2023-03-10","2023-04-07","2023-05-05","2023-06-02","2023-07-07","2023-08-04","2023-09-01","2023-10-06","2023-11-03","2023-12-08"],
        "JOLTS": ["2023-01-04","2023-02-01","2023-03-08","2023-04-04","2023-05-02","2023-05-31","2023-07-06","2023-08-01","2023-08-29","2023-10-03","2023-11-01","2023-12-05"],
        "CPI": ["2023-01-12","2023-02-14","2023-03-14","2023-04-12","2023-05-10","2023-06-13","2023-07-12","2023-08-10","2023-09-13","2023-10-12","2023-11-14","2023-12-12"],
        "PCE": ["2023-01-27","2023-02-24","2023-03-31","2023-04-28","2023-05-26","2023-06-30","2023-07-28","2023-08-31","2023-09-29","2023-10-27","2023-11-30","2023-12-22"],
        "FOMC": ["2023-02-01","2023-03-22","2023-05-03","2023-06-14","2023-07-26","2023-09-20","2023-11-01","2023-12-13"],
    },
    2024: {
        "ADP": ["2024-01-04","2024-01-31","2024-03-06","2024-04-03","2024-05-01","2024-06-05","2024-07-03","2024-07-31","2024-09-05","2024-10-02","2024-10-30","2024-12-04"],
        "NFP": ["2024-01-05","2024-02-02","2024-03-08","2024-04-05","2024-05-03","2024-06-07","2024-07-05","2024-08-02","2024-09-06","2024-10-04","2024-11-01","2024-12-06"],
        "JOLTS": ["2024-01-03","2024-01-30","2024-03-06","2024-04-02","2024-05-01","2024-06-04","2024-07-02","2024-07-30","2024-09-04","2024-10-01","2024-10-29","2024-12-03"],
        "CPI": ["2024-01-11","2024-02-13","2024-03-12","2024-04-10","2024-05-15","2024-06-12","2024-07-11","2024-08-14","2024-09-11","2024-10-10","2024-11-13","2024-12-11"],
        "PCE": ["2024-01-26","2024-02-29","2024-03-29","2024-04-26","2024-05-31","2024-06-28","2024-07-26","2024-08-30","2024-09-27","2024-10-31","2024-11-27","2024-12-20"],
        "FOMC": ["2024-01-31","2024-03-20","2024-05-01","2024-06-12","2024-07-31","2024-09-18","2024-11-07","2024-12-18"],
    }
}

EVENTS[2025] = {"QA": [
"2025-03-05","2025-03-07","2025-03-11","2025-03-12","2025-03-19","2025-03-28",
"2025-04-01","2025-04-02","2025-04-04","2025-04-10","2025-04-29","2025-04-30",
"2025-05-02","2025-05-07","2025-05-13","2025-05-30","2025-06-03","2025-06-04",
"2025-06-06","2025-06-11","2025-06-18","2025-06-27","2025-07-01","2025-07-02",
"2025-07-03","2025-07-15","2025-07-29","2025-07-30","2025-07-31","2025-08-01",
"2025-08-12","2025-08-29","2025-09-03","2025-09-04","2025-09-05","2025-09-11",
"2025-09-17","2025-09-26","2025-09-30"
]}
EXPECTED_2025_Y2 = {
"2025-03-05":3.99,"2025-03-07":3.99,"2025-03-11":3.94,"2025-03-12":4.01,"2025-03-19":3.99,"2025-03-28":3.89,
"2025-04-01":3.87,"2025-04-02":3.91,"2025-04-04":3.68,"2025-04-10":3.84,"2025-04-29":3.65,"2025-04-30":3.60,
"2025-05-02":3.83,"2025-05-07":3.78,"2025-05-13":4.02,"2025-05-30":3.89,"2025-06-03":3.96,"2025-06-04":3.87,
"2025-06-06":4.04,"2025-06-11":3.94,"2025-06-18":3.94,"2025-06-27":3.73,"2025-07-01":3.78,"2025-07-02":3.78,
"2025-07-03":3.88,"2025-07-15":3.95,"2025-07-29":3.86,"2025-07-30":3.94,"2025-07-31":3.94,"2025-08-01":3.69,
"2025-08-12":3.72,"2025-08-29":3.59,"2025-09-03":3.61,"2025-09-04":3.59,"2025-09-05":3.51,"2025-09-11":3.52,
"2025-09-17":3.52,"2025-09-26":3.63,"2025-09-30":3.60
}

def corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    m=np.isfinite(a)&np.isfinite(b); a=a[m]; b=b[m]
    if len(a)<10 or np.std(a)<=1e-12 or np.std(b)<=1e-12:
        return np.nan
    return float(np.corrcoef(a,b)[0,1])

def corr_info(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    m=np.isfinite(a)&np.isfinite(b); a=a[m]; b=b[m]
    if len(a)<10 or np.std(a)<=1e-12 or np.std(b)<=1e-12:
        return np.nan,np.nan,int(len(a))
    r,p=pearsonr(a,b)
    return float(r),float(p),int(len(a))

def erank(a,v):
    a=np.asarray(a,float); a=a[np.isfinite(a)]
    return (1+np.sum(a<=v))/(len(a)+1) if len(a) else np.nan

def build_event_table():
    rows=[]
    for year,fams in EVENTS.items():
        by_date={}
        for fam,dates in fams.items():
            for d in dates:
                by_date.setdefault(d,[]).append(fam)
        for d in sorted(by_date):
            rows.append({"year":year,"date":pd.Timestamp(d),"event":"+".join(sorted(by_date[d]))})
    ev=pd.DataFrame(rows).sort_values("date").reset_index(drop=True)

    url="https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2&cosd=2022-12-20&coed=2025-09-30"
    with urllib.request.urlopen(url, timeout=30) as resp:
        raw=resp.read()
    tmp=AX/"_tmp_dgs2_pre2025.csv"
    tmp.write_bytes(raw)
    d=pd.read_csv(tmp)
    tmp.unlink(missing_ok=True)
    d.columns=["date","DGS2"]
    d["date"]=pd.to_datetime(d["date"])
    d["DGS2"]=pd.to_numeric(d["DGS2"],errors="coerce")
    d=d.dropna(subset=["DGS2"]).sort_values("date").reset_index(drop=True)
    d.to_csv(OUT_DGS2,index=False)

    vals=[]; carried=[]
    for dt in ev.date:
        q=d[d.date<=dt].tail(1)
        if q.empty:
            vals.append(np.nan); carried.append(True)
        else:
            vals.append(float(q.DGS2.iloc[0]))
            carried.append(bool(q.date.iloc[0]!=dt))
    ev["two_y"]=vals
    ev["dgs2_carried_forward"]=carried
    return ev

def load():
    v=pd.read_csv(V5,parse_dates=["feature_cutoff_date"])
    p=pd.read_csv(PANEL,parse_dates=["feature_cutoff_date"])
    d=pd.read_csv(DIV,parse_dates=["feature_cutoff_date"])
    z=v.merge(p,on="feature_cutoff_date",how="inner",suffixes=("","_p"))
    z["v5_pred"]=(pd.to_numeric(z.p_helios_v5_dce,errors="coerce")>=.5).astype(int)
    return z.sort_values("feature_cutoff_date").reset_index(drop=True),d.sort_values("feature_cutoff_date").reset_index(drop=True)

def score_year(ev,z,d,year):
    e=ev[ev.year==year].sort_values("date").reset_index(drop=True)
    rows=[]
    for i in range(3,len(e)):
        rr=e.iloc[i]
        dt=rr.date
        q=z[z.feature_cutoff_date==dt]
        if q.empty:
            continue
        r=q.iloc[-1]

        ys=e.two_y.astype(float).to_numpy()
        ss=[100*(ys[j]-ys[j-1]) for j in range(i-2,i+1)]
        if not np.isfinite(ss).all():
            continue
        gross=float(sum(abs(x) for x in ss)); net=float(sum(ss))
        cr=float((gross-abs(net))/gross) if gross else 0.0
        dom=float(abs(ss[-1])/gross) if gross else 0.0
        hotspot=bool(cr>0.359 and dom>0.294 and dom<=0.502)

        zi=z.index[z.feature_cutoff_date==dt]
        if len(zi)!=1:
            continue
        zi=int(zi[0])
        hist=z.iloc[max(0,zi-120):zi]
        specs=[("trend_strength",-1),("session_against_trend",1),("trend_close_location",-1),("adverse_excursion",1)]
        ranks=[erank(s*pd.to_numeric(hist[c],errors="coerce").to_numpy(float),s*float(r[c])) for c,s in specs]
        sus=float(np.median(ranks)) if np.isfinite(ranks).all() else np.nan

        di=d.index[d.feature_cutoff_date==dt]
        breadth=np.nan
        ndx_r60=ndx_p60=vix_r60=vix_p60=np.nan
        ndx_n60=vix_n60=0
        if len(di)==1:
            j=int(di[0]); h=d.iloc[max(0,j-60):j]
            g=pd.to_numeric(h.gold_daily_ret1,errors="coerce").to_numpy(float)
            cs=[]
            for c in ["usd_ret1","tnx_chg1","ndx_ret1","vix_ret1"]:
                cc=corr(g,pd.to_numeric(h[c],errors="coerce").to_numpy(float))
                if np.isfinite(cc): cs.append(abs(cc))
            breadth=float(np.mean(cs)) if cs else np.nan
            ndx_r60,ndx_p60,ndx_n60=corr_info(g,pd.to_numeric(h.ndx_ret1,errors="coerce").to_numpy(float))
            vix_r60,vix_p60,vix_n60=corr_info(g,pd.to_numeric(h.vix_ret1,errors="coerce").to_numpy(float))

        gate=bool(sus>=0.60 or (np.isfinite(breadth) and breadth>=0.30))
        pred=int(r.v5_pred); mom=int(r.momentum_up); y=int(r.y_up)
        v2_candidate=bool(hotspot and gate and pred==mom)
        strong_pro=bool(
            np.isfinite(ndx_r60) and np.isfinite(vix_r60) and np.isfinite(ndx_p60) and np.isfinite(vix_p60)
            and ndx_r60>0 and vix_r60<0 and min(ndx_p60,vix_p60)<ALPHA
        )
        v3_candidate=bool(v2_candidate and not strong_pro)
        v2_rescue=bool(v2_candidate and pred!=y)
        v2_broken=bool(v2_candidate and pred==y)
        v3_rescue=bool(v3_candidate and pred!=y)
        v3_broken=bool(v3_candidate and pred==y)

        rows.append({
            "year":year,"date":dt.date().isoformat(),"event":rr.event,"two_y":float(rr.two_y),
            "dgs2_carried_forward":bool(rr.dgs2_carried_forward),
            "conflict_ratio":cr,"current_dominance":dom,"hotspot":hotspot,
            "susceptibility":sus,"macro_breadth":breadth,"gate":gate,
            "v5_pred":pred,"momentum_up":mom,"y_up":y,
            "v2_candidate":v2_candidate,"v2_rescue":v2_rescue,"v2_broken":v2_broken,
            "ndx_r60":ndx_r60,"ndx_p60":ndx_p60,"ndx_n60":ndx_n60,
            "vix_r60":vix_r60,"vix_p60":vix_p60,"vix_n60":vix_n60,
            "strong_pro_risk":strong_pro,
            "v3_candidate":v3_candidate,"v3_rescue":v3_rescue,"v3_broken":v3_broken,
        })
    return pd.DataFrame(rows)

def confusion(y,p):
    y=np.asarray(y,int); p=np.asarray(p,int)
    tp=int(((y==1)&(p==1)).sum()); tn=int(((y==0)&(p==0)).sum())
    fp=int(((y==0)&(p==1)).sum()); fn=int(((y==1)&(p==0)).sum())
    up=tp/max(tp+fn,1); down=tn/max(tn+fp,1)
    return {"n":int(len(y)),"correct":int((y==p).sum()),"accuracy":float((y==p).mean()),
            "tp":tp,"tn":tn,"fp":fp,"fn":fn,"up_recall":float(up),"down_recall":float(down),
            "balanced_accuracy":float((up+down)/2)}

def action_metrics(q,prefix):
    c=q[f"{prefix}_candidate"].astype(bool)
    r=q[f"{prefix}_rescue"].astype(bool)
    b=q[f"{prefix}_broken"].astype(bool)
    return {"event_rows":int(len(q)),"hotspots":int(q.hotspot.sum()),"gated_hotspots":int((q.hotspot&q.gate).sum()),
            "actions":int(c.sum()),"rescue":int(r.sum()),"broken":int(b.sum()),
            "net":int(r.sum()-b.sum()),"precision":float(r.sum()/max(int(c.sum()),1))}

def year_full_metrics(v, q, year):
    g=v[v.feature_cutoff_date.dt.year==year].copy()
    y=g.y_up.astype(int).to_numpy()
    base=(pd.to_numeric(g.p_helios_v5_dce,errors="coerce")>=.5).astype(int).to_numpy()
    mp=dict(zip(g.feature_cutoff_date.dt.strftime("%Y-%m-%d"),range(len(g))))
    assisted=base.copy()
    dates=[]
    for r in q[q.v3_candidate].itertuples():
        if r.date in mp:
            k=mp[r.date]
            assisted[k]=1-assisted[k]
            dates.append(r.date)
    return confusion(y,base),confusion(y,assisted),dates

def main():
    ev=build_event_table()
    z,d=load()
    allq=[]
    summary={"schema":"RULEFLOW_V3_TG_PRE2025_BACKCAST","status":"FIXED_RULE_HISTORICAL_BACKCAST","years":{}}
    for year in [2023,2024]:
        q=score_year(ev,z,d,year)
        allq.append(q)
        v2m=action_metrics(q,"v2"); v3m=action_metrics(q,"v3")
        b,a,dates=year_full_metrics(pd.read_csv(V5,parse_dates=["feature_cutoff_date"]),q,year)
        summary["years"][str(year)]={"v2":v2m,"v3":v3m,"v5_baseline":b,"v5_plus_v3":a,"v3_action_dates":dates}
    q=pd.concat(allq,ignore_index=True)
    q.to_csv(OUT_CSV,index=False)

    v2all=action_metrics(q,"v2"); v3all=action_metrics(q,"v3")
    summary["combined_actions"]={"v2":v2all,"v3":v3all}
    q25=score_year(ev,z,d,2025)
    qa25_v2=action_metrics(q25,"v2")
    qa25_v3=action_metrics(q25,"v3")
    e25=ev[ev.year==2025].copy()
    diffs=[]
    for rr in e25.itertuples():
        ex=EXPECTED_2025_Y2.get(rr.date.strftime("%Y-%m-%d"))
        if ex is not None and np.isfinite(rr.two_y):
            diffs.append(abs(float(rr.two_y)-float(ex)))
    maxdiff=float(max(diffs)) if diffs else np.nan
    qa_pass=bool(qa25_v2["actions"]==5 and qa25_v2["rescue"]==5 and qa25_v2["broken"]==0 and maxdiff<=0.011)
    summary["reconstruction_qa_2025"]={"v2":qa25_v2,"v3":qa25_v3,"max_abs_dgs2_diff_vs_frozen_y2":maxdiff,"pass":qa_pass}
    summary["dgs2_carried_forward_event_dates"]=ev.loc[ev.dgs2_carried_forward,"date"].dt.strftime("%Y-%m-%d").tolist()
    OUT_SUM.write_text(json.dumps(summary,indent=2)+"\n")

    lines=[
        "# GOLD H3 — RULEFLOW V3-TG PRE-2025 BACKCAST RESULT","",
        "**Status:** FIXED-RULE HISTORICAL BACKCAST — not prospective validation.","",
        "No RuleFlow threshold, topology sign, p-value threshold, or action rule was changed after the preregistration commit.","",
    ]
    for year in [2023,2024]:
        s=summary["years"][str(year)]
        lines += [
            f"## {year}","",
            f"- event rows scored: **{s['v3']['event_rows']}**",
            f"- V2 hotspots / gated hotspots: **{s['v2']['hotspots']} / {s['v2']['gated_hotspots']}**",
            f"- V2 actions: **{s['v2']['actions']}**, rescue/broken/net = **{s['v2']['rescue']} / {s['v2']['broken']} / {s['v2']['net']:+d}**",
            f"- V3-TG actions: **{s['v3']['actions']}**, rescue/broken/net = **{s['v3']['rescue']} / {s['v3']['broken']} / {s['v3']['net']:+d}**",
            f"- V3-TG action precision: **{100*s['v3']['precision']:.2f}%**",
            f"- V5 baseline: **{s['v5_baseline']['correct']}/{s['v5_baseline']['n']} = {100*s['v5_baseline']['accuracy']:.2f}%**, BA **{100*s['v5_baseline']['balanced_accuracy']:.2f}%**",
            f"- V5 + V3-TG: **{s['v5_plus_v3']['correct']}/{s['v5_plus_v3']['n']} = {100*s['v5_plus_v3']['accuracy']:.2f}%**, BA **{100*s['v5_plus_v3']['balanced_accuracy']:.2f}%**",
            f"- V3 action dates: **{', '.join(s['v3_action_dates']) if s['v3_action_dates'] else 'none'}**",""
        ]
    lines += [
        "## Reconstruction QA on known 2025 evidence","",
        f"- V2 actions/rescue/broken: **{summary['reconstruction_qa_2025']['v2']['actions']} / {summary['reconstruction_qa_2025']['v2']['rescue']} / {summary['reconstruction_qa_2025']['v2']['broken']}**",
        f"- V3 actions/rescue/broken: **{summary['reconstruction_qa_2025']['v3']['actions']} / {summary['reconstruction_qa_2025']['v3']['rescue']} / {summary['reconstruction_qa_2025']['v3']['broken']}**",
        f"- max absolute DGS2 difference vs frozen 2025 y2 values: **{summary['reconstruction_qa_2025']['max_abs_dgs2_diff_vs_frozen_y2']:.4f} pp**",
        f"- reconstruction QA pass: **{summary['reconstruction_qa_2025']['pass']}**","",
        "## Combined 2023-2024 event accounting","",
        f"- V2 actions: **{v2all['actions']}**, rescue/broken/net = **{v2all['rescue']} / {v2all['broken']} / {v2all['net']:+d}**",
        f"- V3-TG actions: **{v3all['actions']}**, rescue/broken/net = **{v3all['rescue']} / {v3all['broken']} / {v3all['net']:+d}**",
        f"- V3-TG precision: **{100*v3all['precision']:.2f}%**","",
        "## V3 action detail","",
        "| Date | Event | V5 | Momentum | Actual | Rescue | Broken | NDX r60 | VIX r60 | Strong pro-risk |",
        "|---|---|---:|---:|---:|---|---|---:|---:|---|"
    ]
    for r in q[q.v3_candidate].itertuples():
        lines.append(f"| {r.date} | {r.event} | {r.v5_pred} | {r.momentum_up} | {r.y_up} | {r.v3_rescue} | {r.v3_broken} | {r.ndx_r60:.3f} | {r.vix_r60:.3f} | {r.strong_pro_risk} |")
    lines += ["","## V2 calls vetoed by topology","",
              "| Date | Event | V2 rescue | V2 broken | NDX r60 | VIX r60 |",
              "|---|---|---|---|---:|---:|"]
    for r in q[q.v2_candidate & ~q.v3_candidate].itertuples():
        lines.append(f"| {r.date} | {r.event} | {r.v2_rescue} | {r.v2_broken} | {r.ndx_r60:.3f} | {r.vix_r60:.3f} |")
    lines += ["","## Data note","",
              f"- DGS2 carry-forward was required on **{len(summary['dgs2_carried_forward_event_dates'])}** event dates: {', '.join(summary['dgs2_carried_forward_event_dates']) if summary['dgs2_carried_forward_event_dates'] else 'none'}.",
              "- SAGE V2 cannot be backcast to 2023-2024 with the frozen source contract because IFBC begins 2025-05-09 and LLRS begins 2025-02-07. No synthetic SAGE result is reported.",
              "- This backcast is historically earlier than the topology discovery period, but it remains retrospective evidence rather than prospective OOS validation."
    ]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()

# trigger: pre2025-backcast-run
