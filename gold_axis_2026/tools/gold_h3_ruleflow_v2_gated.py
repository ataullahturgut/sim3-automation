from pathlib import Path
import json, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"
OUT=AX/"GOLD_H3_RULEFLOW_V2_GATED_RESULT_2026-10-04.md"
OUTJ=AX/"GOLD_H3_RULEFLOW_V2_GATED_SUMMARY_2026-10-04.json"

EVENTS_2025=[
("2025-03-05",3.99),("2025-03-07",3.99),("2025-03-11",3.94),("2025-03-12",4.01),("2025-03-19",3.99),
("2025-03-28",3.89),("2025-04-01",3.87),("2025-04-02",3.91),("2025-04-04",3.68),("2025-04-10",3.84),
("2025-04-29",3.65),("2025-04-30",3.60),("2025-05-02",3.83),("2025-05-07",3.78),("2025-05-13",4.02),
("2025-05-30",3.89),("2025-06-03",3.96),("2025-06-04",3.87),("2025-06-06",4.04),("2025-06-11",3.94),
("2025-06-18",3.94),("2025-06-27",3.73),("2025-07-01",3.78),("2025-07-02",3.78),("2025-07-03",3.88),
("2025-07-15",3.95),("2025-07-29",3.86),("2025-07-30",3.94),("2025-07-31",3.94),("2025-08-01",3.69),
("2025-08-12",3.72),("2025-08-29",3.59),("2025-09-03",3.61),("2025-09-04",3.59),("2025-09-05",3.51),
("2025-09-11",3.52),("2025-09-17",3.52),("2025-09-26",3.63),("2025-09-30",3.60)]
EVENTS_2026Q1=[
("2026-01-07",3.47),("2026-01-09",3.54),("2026-01-13",3.53),("2026-01-28",3.56),("2026-02-04",3.57),
("2026-02-05",3.47),("2026-02-11",3.52),("2026-02-13",3.40),("2026-02-20",3.48),("2026-03-04",3.54),
("2026-03-06",3.56),("2026-03-11",3.64),("2026-03-13",3.73),("2026-03-18",3.76),("2026-03-31",3.79)]

def corr(a,b):
    a=np.asarray(a,float); b=np.asarray(b,float)
    m=np.isfinite(a)&np.isfinite(b); a=a[m]; b=b[m]
    if len(a)<10: return np.nan
    return float(np.corrcoef(a,b)[0,1])

def erank(a,v):
    a=np.asarray(a,float); a=a[np.isfinite(a)]
    return (1+np.sum(a<=v))/(len(a)+1) if len(a) else np.nan

def load():
    v=pd.read_csv(V5,parse_dates=["feature_cutoff_date"])
    p=pd.read_csv(PANEL,parse_dates=["feature_cutoff_date"])
    d=pd.read_csv(DIV,parse_dates=["feature_cutoff_date"])
    z=v.merge(p,on="feature_cutoff_date",how="inner",suffixes=("","_p"))
    z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
    return z.sort_values("feature_cutoff_date").reset_index(drop=True),d.sort_values("feature_cutoff_date").reset_index(drop=True)

def score(events,z,d):
    rows=[]
    for i in range(3,len(events)):
        date,y2=events[i]
        q=z[z.feature_cutoff_date==pd.Timestamp(date)]
        if q.empty: continue
        r=q.iloc[-1]
        ss=[100*(events[j][1]-events[j-1][1]) for j in range(i-2,i+1)]
        gross=sum(abs(x) for x in ss); net=sum(ss)
        cr=(gross-abs(net))/gross if gross else 0
        dom=abs(ss[-1])/gross if gross else 0
        hotspot=(cr>0.359 and dom>0.294 and dom<=0.502)

        zi=z.index[z.feature_cutoff_date==pd.Timestamp(date)][0]
        hist=z.iloc[max(0,zi-120):zi]
        specs=[("trend_strength",-1),("session_against_trend",1),("trend_close_location",-1),("adverse_excursion",1)]
        ranks=[erank(s*hist[c].astype(float).to_numpy(),s*float(r[c])) for c,s in specs]
        sus=float(np.median(ranks))

        di=d.index[d.feature_cutoff_date==pd.Timestamp(date)]
        breadth=np.nan
        if len(di):
            j=int(di[0]); h=d.iloc[max(0,j-60):j]
            g=h.gold_daily_ret1.astype(float).to_numpy()
            cs=[corr(g,h[c].astype(float).to_numpy()) for c in ["usd_ret1","tnx_chg1","ndx_ret1","vix_ret1"]]
            cs=[abs(x) for x in cs if np.isfinite(x)]
            breadth=float(np.mean(cs)) if cs else np.nan

        gate=bool(sus>=0.60 or (np.isfinite(breadth) and breadth>=0.30))
        candidate=bool(hotspot and gate and int(r.v5_pred)==int(r.momentum_up))
        y=int(r.y_up); pred=int(r.v5_pred); mom=int(r.momentum_up)
        rescue=bool(candidate and pred!=y)
        broken=bool(candidate and pred==y)
        rows.append(dict(date=date,cr=cr,dom=dom,hotspot=hotspot,sus=sus,breadth=breadth,gate=gate,
                         candidate=candidate,rescue=rescue,broken=broken,reversal=(y!=mom),
                         v5_missed=(pred==mom and y!=mom)))
    return pd.DataFrame(rows)

def metrics(q):
    a=q[q.candidate]
    return dict(n=len(q),hotspots=int(q.hotspot.sum()),gated_hotspots=int((q.hotspot&q.gate).sum()),
                actions=int(q.candidate.sum()),rescue=int(q.rescue.sum()),broken=int(q.broken.sum()),
                net=int(q.rescue.sum()-q.broken.sum()),
                precision=float(q.rescue.sum()/max(int(q.candidate.sum()),1)),
                reversals=int(q.reversal.sum()),captured=int((q.candidate&q.reversal).sum()))

def main():
    z,d=load()
    q25=score(EVENTS_2025,z,d)
    q26=score(EVENTS_2026Q1,z,d)
    m25=metrics(q25); m26=metrics(q26)
    detail25=q25[q25.hotspot][["date","sus","breadth","gate","candidate","rescue","broken"]].to_dict("records")
    detail26=q26[q26.hotspot][["date","sus","breadth","gate","candidate","rescue","broken"]].to_dict("records")
    OUTJ.write_text(json.dumps({"rule":{"conflict_ratio_gt":0.359,"dominance_gt":0.294,"dominance_le":0.502,
                                      "susceptibility_ge":0.60,"macro_breadth_ge":0.30,"gate":"OR"},
                                "2025":m25,"2026Q1":m26,"detail_2025":detail25,"detail_2026Q1":detail26},indent=2,default=str)+"\n")
    lines=["# GOLD H3 — RULEFLOW V2 GATED RESULT","",
           "Rule: expectation hotspot AND (internal susceptibility >= 0.60 OR macro breadth >= 0.30), acting only when V5 follows momentum.","",
           "## 2025 discovery accounting","",
           f"- hotspots: **{m25['hotspots']}**",
           f"- gated hotspots: **{m25['gated_hotspots']}**",
           f"- actions: **{m25['actions']}**",
           f"- rescue / broken / net: **{m25['rescue']} / {m25['broken']} / {m25['net']:+d}**",
           f"- precision: **{100*m25['precision']:.1f}%**","",
           "## 2026 Q1 frozen stress","",
           f"- hotspots: **{m26['hotspots']}**",
           f"- gated hotspots: **{m26['gated_hotspots']}**",
           f"- actions: **{m26['actions']}**",
           f"- rescue / broken / net: **{m26['rescue']} / {m26['broken']} / {m26['net']:+d}**",
           f"- precision: **{100*m26['precision']:.1f}%**","",
           "## 2026 Q1 hotspot detail","",
           "| Date | Susceptibility | Macro breadth | Gate | Candidate | Rescue | Broken |",
           "|---|---:|---:|---|---|---|---|"]
    for r in detail26:
        lines.append(f"| {r['date']} | {r['sus']:.3f} | {r['breadth']:.3f} | {r['gate']} | {r['candidate']} | {r['rescue']} | {r['broken']} |")
    OUT.write_text("\n".join(lines)+"\n")
    print(OUT.read_text())

if __name__=="__main__":
    main()
