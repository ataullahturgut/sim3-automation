from __future__ import annotations
from pathlib import Path
import json
import numpy as np
import pandas as pd

from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"

DIV=AX/"GOLD_H3_DIVERGE_PROXY_V1_PANEL_2026-10-03.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
SAGE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"

OUT_SCORE=AX/"GOLD_H3_ERB_V1_SCORES_2026-10-04.csv"
OUT_GRID=AX/"GOLD_H3_ERB_V1_DEV_GRID_2026-10-04.csv"
OUT_JSON=AX/"GOLD_H3_ERB_V1_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_ERB_V1_RESULT_2026-10-04.md"

XCOLS=["usd_ret1","tnx_chg1","ndx_ret1","vix_ret1","silver_ret1"]
RANK_SIGNS={
    "trend_strength":-1.0,
    "session_against_trend":1.0,
    "trend_close_location":-1.0,
    "adverse_excursion":1.0,
}
QS=[0.60,0.70,0.80]
QB=[0.60,0.70,0.80]
RULES=["A_RESPONSE","B_SHIFT","C_CONCURRENCE"]

def bools(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def ridge():
    return Pipeline([
        ("sc",StandardScaler()),
        ("rg",Ridge(alpha=10.0)),
    ])

def erank(hist, value):
    a=np.asarray(hist,float)
    a=a[np.isfinite(a)]
    if len(a)==0 or not np.isfinite(value):
        return np.nan
    return float((1.0 + np.sum(a<=value))/(len(a)+1.0))

def load():
    d=pd.read_csv(DIV,parse_dates=[
        "feature_cutoff_date","forecast_issue_date","target_end_date_h3",
        "metal_source_date","usd_source_date","yield_source_date","ndx_source_date","vix_source_date"
    ])
    v=pd.read_csv(V5,usecols=[
        "feature_cutoff_date","p_helios_v5_dce"
    ],parse_dates=["feature_cutoff_date"])
    z=d.merge(v,on="feature_cutoff_date",how="inner",validate="one_to_one")
    z["v5_pred"]=(z.p_helios_v5_dce>=.5).astype(int)
    z["eligible"]=z.v5_pred.eq(z.momentum_up.astype(int))
    z["rescue_target"]=z.eligible & z.v5_pred.ne(z.y_up.astype(int))

    try:
        s=pd.read_csv(SAGE,usecols=["feature_cutoff_date","ocs_candidate"],parse_dates=["feature_cutoff_date"])
        s["ocs_candidate"]=bools(s.ocs_candidate)
        z=z.merge(s,on="feature_cutoff_date",how="left",validate="one_to_one")
    except Exception:
        z["ocs_candidate"]=False
    z["ocs_candidate"]=z.ocs_candidate.fillna(False).astype(bool)
    return z.sort_values("feature_cutoff_date").reset_index(drop=True)

def build_scores(z):
    e=z[z.eligible].copy().reset_index(drop=True)
    rows=[]
    for i,r in e.iterrows():
        hist=e.iloc[:i].copy()
        if len(hist)<80:
            continue
        hist=hist.dropna(subset=XCOLS+["gold_daily_ret1"]).tail(120)
        if len(hist)<80:
            continue
        short=hist.tail(30)
        if len(short)<20:
            continue

        ml=ridge(); ms=ridge()
        Xl=hist[XCOLS].to_numpy(float)
        yl=hist.gold_daily_ret1.to_numpy(float)
        Xs=short[XCOLS].to_numpy(float)
        ys=short.gold_daily_ret1.to_numpy(float)
        ml.fit(Xl,yl); ms.fit(Xs,ys)

        cur=r[XCOLS].to_numpy(float).reshape(1,-1)
        if not np.isfinite(cur).all() or not np.isfinite(r.gold_daily_ret1):
            continue
        pl=float(ml.predict(cur)[0])
        ps=float(ms.predict(cur)[0])
        resid=yl-ml.predict(Xl)
        sig=float(np.std(resid,ddof=1))
        if not np.isfinite(sig) or sig<=1e-9:
            continue

        prior=e.iloc[max(0,i-120):i]
        if len(prior)<60:
            continue
        rr=[]
        for c,sgn in RANK_SIGNS.items():
            ph=sgn*prior[c].astype(float).to_numpy()
            cv=sgn*float(r[c])
            rr.append(erank(ph,cv))
        if not np.isfinite(rr).all():
            continue
        susceptibility=float(np.median(rr))

        mom=1.0 if int(r.momentum_up)==1 else -1.0
        response_break=float(-mom*(float(r.gold_daily_ret1)-pl)/sig)
        relation_shift=float(-mom*(ps-pl)/sig)
        external_opp=float(-mom*ps/sig)

        rows.append({
            "feature_cutoff_date":r.feature_cutoff_date,
            "forecast_issue_date":r.forecast_issue_date,
            "target_end_date_h3":r.target_end_date_h3,
            "year":int(r.year),
            "month":str(r.month),
            "y_up":int(r.y_up),
            "target_r3":float(r.target_r3),
            "momentum_up":int(r.momentum_up),
            "v5_pred":int(r.v5_pred),
            "p_v5":float(r.p_helios_v5_dce),
            "rescue_target":int(r.rescue_target),
            "ocs_candidate":bool(r.ocs_candidate),
            "susceptibility":susceptibility,
            "response_break":response_break,
            "relation_shift":relation_shift,
            "external_opp":external_opp,
            "pred_long":pl,
            "pred_short":ps,
            "rel_sigma":sig,
            "rank_weak_trend":rr[0],
            "rank_session_opp":rr[1],
            "rank_failed_close":rr[2],
            "rank_adverse":rr[3],
        })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)

def candidate(q,rule,ts,tb):
    if rule=="A_RESPONSE":
        return (q.susceptibility>=ts)&(q.response_break>=tb)
    if rule=="B_SHIFT":
        return (q.susceptibility>=ts)&(q.relation_shift>=tb)&(q.external_opp>0)
    if rule=="C_CONCURRENCE":
        mx=np.maximum(q.response_break,q.relation_shift)
        return (q.susceptibility>=ts)&(mx>=tb)&(q.external_opp>0)
    raise ValueError(rule)

def stat(q,c):
    y=q.rescue_target.astype(bool)
    n=int(c.sum()); r=int((c&y).sum()); b=int((c&~y).sum())
    return {
        "actions":n,"rescue":r,"broken":b,"net":r-b,
        "precision":r/max(n,1),
        "action_rate":float(c.mean()) if len(c) else 0.0,
    }

def eval_period(scores,rule,ts,tb,year):
    q=scores[scores.year==year].copy()
    q["erb_candidate"]=candidate(q,rule,ts,tb)
    q["sage_pred"]=np.where(q.ocs_candidate,1-q.v5_pred,q.v5_pred).astype(int)
    q["incremental_action"]=q.erb_candidate & (~q.ocs_candidate)
    q["assisted_pred"]=np.where(q.incremental_action,1-q.v5_pred,q.sage_pred).astype(int)
    q["rescue"]=q.incremental_action & q.sage_pred.ne(q.y_up) & q.assisted_pred.eq(q.y_up)
    q["broken"]=q.incremental_action & q.sage_pred.eq(q.y_up) & q.assisted_pred.ne(q.y_up)
    a=int(q.incremental_action.sum()); r=int(q.rescue.sum()); b=int(q.broken.sum())
    half={}
    for h,mask in [("H1",q.forecast_issue_date.dt.month<=6),("H2",q.forecast_issue_date.dt.month>=7)]:
        z=q[mask]
        rr=int(z.rescue.sum()); bb=int(z.broken.sum())
        half[h]={"actions":int(z.incremental_action.sum()),"rescue":rr,"broken":bb,"net":rr-bb}
    return {
        "covered_n":len(q),
        "candidates":int(q.erb_candidate.sum()),
        "ocs_overlap":int((q.erb_candidate&q.ocs_candidate).sum()),
        "actions":a,"rescue":r,"broken":b,"net":r-b,
        "precision":r/max(a,1),
        "sage_correct":int((q.sage_pred==q.y_up).sum()),
        "assisted_correct":int((q.assisted_pred==q.y_up).sum()),
        "sage_accuracy":float((q.sage_pred==q.y_up).mean()) if len(q) else np.nan,
        "assisted_accuracy":float((q.assisted_pred==q.y_up).mean()) if len(q) else np.nan,
        "half":half,
    }

def main():
    z=load()
    s=build_scores(z)
    s.to_csv(OUT_SCORE,index=False)

    dev=s[s.year.isin([2023,2024])].copy()
    grid=[]
    if len(dev):
        for qs in QS:
            ts=float(dev.susceptibility.quantile(qs))
            for qb in QB:
                for bcol in ["response_break","relation_shift"]:
                    pass
                # one shared break scale: quantile of max positive directional break
                base=np.maximum(dev.response_break,dev.relation_shift)
                tb=float(pd.Series(base).quantile(qb))
                for rule in RULES:
                    c=candidate(dev,rule,ts,tb)
                    st=stat(dev,c)
                    elig=bool(st["actions"]>=8 and st["action_rate"]<=.20 and st["precision"]>=.55 and st["net"]>=2)
                    grid.append({"rule":rule,"q_s":qs,"q_b":qb,"sus_threshold":ts,"break_threshold":tb,**st,"eligible":elig})
    g=pd.DataFrame(grid)
    g.to_csv(OUT_GRID,index=False)

    selected=None; ev25=None; ev26=None; status="ERB_DEV_FAIL"
    elig=g[g.eligible].copy() if len(g) else pd.DataFrame()
    if len(elig):
        rank={"C_CONCURRENCE":0,"B_SHIFT":1,"A_RESPONSE":2}
        elig["rule_rank"]=elig.rule.map(rank)
        elig=elig.sort_values(
            ["net","precision","rescue","action_rate","q_s","q_b","rule_rank"],
            ascending=[False,False,False,True,False,False,True]
        )
        r=elig.iloc[0]
        selected={
            "rule":r.rule,"q_s":float(r.q_s),"q_b":float(r.q_b),
            "sus_threshold":float(r.sus_threshold),"break_threshold":float(r.break_threshold)
        }
        ev25=eval_period(s,r.rule,float(r.sus_threshold),float(r.break_threshold),2025)
        pass25=bool(
            ev25["actions"]>=4 and ev25["rescue"]>=3 and ev25["net"]>0
            and ev25["precision"]>=.55
            and ev25["assisted_accuracy"]>=ev25["sage_accuracy"]
            and ev25["half"]["H1"]["net"]>=-1
            and ev25["half"]["H2"]["net"]>=-1
        )
        status="ERB_2025_CONFIRM_PASS" if pass25 else "ERB_2025_CONFIRM_FAIL"
        if pass25:
            ev26=eval_period(s,r.rule,float(r.sus_threshold),float(r.break_threshold),2026)
            status="ERB_2026_STRESS_OPENED"

    summary={
        "schema":"ERB_H3_V1",
        "status":status,
        "score_rows":len(s),
        "dev_rows":len(dev),
        "selected":selected,
        "confirmation_2025":ev25,
        "stress_2026":ev26,
        "dev_grid":g.to_dict("records"),
    }
    OUT_JSON.write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# ERB-H3 V1 — EXPECTATION REGIME BREAK RESULT","",
        f"**Status:** **{status}**","",
        f"- scored origins: **{len(s)}**",
        f"- DEV 2023-2024 origins: **{len(dev)}**","",
        "## DEV grid","",
        "| Rule | qS | qB | Actions | Rescue | Broken | Net | Precision | Rate | Eligible |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    for r in g.itertuples():
        lines.append(f"| {r.rule} | {r.q_s:.2f} | {r.q_b:.2f} | {r.actions} | {r.rescue} | {r.broken} | {r.net:+d} | {100*r.precision:.2f}% | {100*r.action_rate:.2f}% | {r.eligible} |")
    if selected:
        lines += ["","## Selected frozen DEV rule","",
                  f"- rule: **{selected['rule']}**",
                  f"- susceptibility threshold: **{selected['sus_threshold']:.4f}**",
                  f"- break threshold: **{selected['break_threshold']:.4f}**"]
    if ev25:
        lines += ["","## 2025 untouched confirmation","",
                  f"- covered: **{ev25['covered_n']}**",
                  f"- candidates / OCS overlap / incremental actions: **{ev25['candidates']} / {ev25['ocs_overlap']} / {ev25['actions']}**",
                  f"- rescue / broken / net: **{ev25['rescue']} / {ev25['broken']} / {ev25['net']:+d}**",
                  f"- precision: **{100*ev25['precision']:.2f}%**",
                  f"- SAGE -> SAGE+ERB accuracy: **{100*ev25['sage_accuracy']:.2f}% -> {100*ev25['assisted_accuracy']:.2f}%**",
                  f"- H1 net: **{ev25['half']['H1']['net']:+d}**, H2 net: **{ev25['half']['H2']['net']:+d}**"]
    if ev26:
        lines += ["","## 2026 stress test","",
                  f"- covered: **{ev26['covered_n']}**",
                  f"- candidates / OCS overlap / incremental actions: **{ev26['candidates']} / {ev26['ocs_overlap']} / {ev26['actions']}**",
                  f"- rescue / broken / net: **{ev26['rescue']} / {ev26['broken']} / {ev26['net']:+d}**",
                  f"- precision: **{100*ev26['precision']:.2f}%**",
                  f"- SAGE -> SAGE+ERB accuracy: **{100*ev26['sage_accuracy']:.2f}% -> {100*ev26['assisted_accuracy']:.2f}%**",
                  f"- H1 net: **{ev26['half']['H1']['net']:+d}**, H2 net: **{ev26['half']['H2']['net']:+d}**"]
    lines += ["","## Governance","",
              "2023-2024 selected the rule. 2025 was untouched confirmation. 2026 was opened only after a 2025 pass. Historical 2026 remains stress/development evidence, not a pristine holdout."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__":
    main()
