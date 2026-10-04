from pathlib import Path
import json, numpy as np, pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
SRC=AX/"GOLD_H3_OPA_V1_SOURCE_2026-10-04.csv"
PANEL=AX/"GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv"
V5=AX/"GOLD_H3_CLEAN_HELIOS_V5_DCE_PREDICTIONS_2026-10-03.csv"
SAGE=AX/"GOLD_H3_SAGE_SELECTIVE_V1_PREDICTIONS_2026-10-04.csv"

OUT_GRID=AX/"GOLD_H3_OPA_V2_DEV_GRID_2026-10-04.csv"
OUT_JSON=AX/"GOLD_H3_OPA_V2_SUMMARY_2026-10-04.json"
OUT_MD=AX/"GOLD_H3_OPA_V2_RESULT_2026-10-04.md"
OUT_PRED=AX/"GOLD_H3_OPA_V2_PREDICTIONS_2026-10-04.csv"

QUANTS=[.70,.80,.85,.90,.95]
RULES=["D_DUAL","B_VOL","C_LEVEL","A_OI"]

def as_bool(s):
    if s.dtype==bool: return s
    return s.astype(str).str.lower().isin(["true","1","yes"])

def make_source():
    x=pd.read_csv(SRC,parse_dates=["trade_date"])
    x=x[x.parse_status=="PASS"].copy().sort_values("trade_date").drop_duplicates("trade_date",keep="last")
    for c in ["og_call_volume","og_call_oi","og_put_volume","og_put_oi"]: x[c]=pd.to_numeric(x[c],errors="coerce")
    eps=1e-12
    x["oi_lr"]=np.log((x.og_call_oi+eps)/(x.og_put_oi+eps))
    x["vol_lr"]=np.log((x.og_call_volume+eps)/(x.og_put_volume+eps))
    x["d_oi_lr"]=x.oi_lr.diff()
    x["d_vol_lr"]=x.vol_lr.diff()
    return x.dropna(subset=["oi_lr","vol_lr","d_oi_lr","d_vol_lr"]).copy()

def build_panel():
    p=pd.read_csv(PANEL,parse_dates=["feature_cutoff_date","forecast_issue_date","target_end_date_h3"])
    v=pd.read_csv(V5,usecols=["feature_cutoff_date","p_helios_v5_dce"],parse_dates=["feature_cutoff_date"])
    sg=pd.read_csv(SAGE,usecols=["feature_cutoff_date","ocs_candidate"],parse_dates=["feature_cutoff_date"])
    sg["ocs_candidate"]=as_bool(sg.ocs_candidate)
    p=p.merge(v,on="feature_cutoff_date",how="inner",validate="one_to_one")
    p=p.merge(sg,on="feature_cutoff_date",how="left",validate="one_to_one")
    p["ocs_candidate"]=p.ocs_candidate.fillna(False).astype(bool)
    p["v5_pred"]=(p.p_helios_v5_dce>=.5).astype(int)
    p["eligible"]=p.v5_pred.eq(p.momentum_up.astype(int))
    p["rescue_target"]=p.v5_pred.ne(p.y_up.astype(int)).astype(int)

    s=make_source()
    rows=[]
    for r in p[p.eligible].itertuples():
        z=s[s.trade_date<r.feature_cutoff_date]
        if z.empty: continue
        q=z.iloc[-1]
        stale=(r.feature_cutoff_date-q.trade_date).days
        if stale>7: continue
        m=1.0 if int(r.momentum_up)==1 else -1.0
        rows.append({
            "feature_cutoff_date":r.feature_cutoff_date,"forecast_issue_date":r.forecast_issue_date,
            "target_end_date_h3":r.target_end_date_h3,"year":int(r.year),"month":str(r.month),
            "y_up":int(r.y_up),"momentum_up":int(r.momentum_up),"v5_pred":int(r.v5_pred),
            "p_v5":float(r.p_helios_v5_dce),"rescue_target":int(r.rescue_target),
            "ocs_candidate":bool(r.ocs_candidate),"source_trade_date":q.trade_date,
            "oi_opp":float(-m*q.d_oi_lr),"vol_opp":float(-m*q.d_vol_lr),"level_opp":float(-m*q.oi_lr),
        })
    return pd.DataFrame(rows).sort_values("forecast_issue_date").reset_index(drop=True)

def mask_rule(z,rule,thr):
    a=z.oi_opp>=thr
    if rule=="A_OI": return a
    if rule=="B_VOL": return a & (z.vol_opp>0)
    if rule=="C_LEVEL": return a & (z.level_opp>0)
    if rule=="D_DUAL": return a & (z.vol_opp>0) & (z.level_opp>0)
    raise ValueError(rule)

def stats(z,mask):
    y=z.rescue_target.astype(bool); c=mask.astype(bool)
    r=int((c&y).sum()); b=int((c&~y).sum()); n=int(c.sum())
    return {
        "actions":n,"rescue":r,"broken":b,"net":r-b,
        "precision":r/max(n,1),"action_rate":float(c.mean()) if len(c) else 0.0
    }

def period_eval(p,rule,thr,year):
    q=p[p.year==year].copy()
    q["opa_candidate"]=mask_rule(q,rule,thr)
    q["incremental_action"]=q.opa_candidate & (~q.ocs_candidate)
    q["sage_pred"]=np.where(q.ocs_candidate,1-q.v5_pred,q.v5_pred).astype(int)
    q["assisted_pred"]=np.where(q.incremental_action,1-q.v5_pred,q.sage_pred).astype(int)
    q["rescue"]=q.incremental_action & q.sage_pred.ne(q.y_up) & q.assisted_pred.eq(q.y_up)
    q["broken"]=q.incremental_action & q.sage_pred.eq(q.y_up) & q.assisted_pred.ne(q.y_up)
    a=int(q.incremental_action.sum()); r=int(q.rescue.sum()); b=int(q.broken.sum())
    return {
        "year":year,"covered_n":len(q),"opa_candidates":int(q.opa_candidate.sum()),
        "ocs_overlap":int((q.opa_candidate&q.ocs_candidate).sum()),
        "incremental_actions":a,"rescue":r,"broken":b,"net":r-b,
        "precision":r/max(a,1),"sage_correct":int((q.sage_pred==q.y_up).sum()),
        "assisted_correct":int((q.assisted_pred==q.y_up).sum()),
        "sage_accuracy":float((q.sage_pred==q.y_up).mean()) if len(q) else np.nan,
        "assisted_accuracy":float((q.assisted_pred==q.y_up).mean()) if len(q) else np.nan
    },q

def main():
    p=build_panel()
    dev=p[p.year.isin([2023,2024])].copy()
    rows=[]
    for qv in QUANTS:
        thr=float(dev.oi_opp.quantile(qv))
        for rule in RULES:
            st=stats(dev,mask_rule(dev,rule,thr))
            eligible=bool(st["actions"]>=8 and st["action_rate"]<=.20 and st["precision"]>=.55 and st["net"]>=2)
            rows.append({"quantile":qv,"oi_opp_threshold":thr,"rule":rule,**st,"eligible":eligible})
    grid=pd.DataFrame(rows)
    grid.to_csv(OUT_GRID,index=False)
    elig=grid[grid.eligible].copy()

    selected=None; ev25=None; ev26=None; pred_out=pd.DataFrame()
    status="OPA_V2_DEV_FAIL"
    if not elig.empty:
        rank={"D_DUAL":0,"B_VOL":1,"C_LEVEL":2,"A_OI":3}
        elig["rule_rank"]=elig.rule.map(rank)
        elig=elig.sort_values(["net","precision","rescue","action_rate","quantile","rule_rank"],
                              ascending=[False,False,False,True,False,True])
        s=elig.iloc[0]
        selected={"rule":s.rule,"quantile":float(s.quantile),"oi_opp_threshold":float(s.oi_opp_threshold)}
        ev25,q25=period_eval(p,s.rule,float(s.oi_opp_threshold),2025)
        confirm=bool(ev25["rescue"]>=2 and ev25["net"]>0 and ev25["precision"]>=.50 and ev25["assisted_accuracy"]>=ev25["sage_accuracy"])
        status="OPA_V2_2025_CONFIRM_PASS" if confirm else "OPA_V2_2025_CONFIRM_FAIL"
        q25["eval_period"]="2025"; pred_out=q25
        if confirm:
            ev26,q26=period_eval(p,s.rule,float(s.oi_opp_threshold),2026)
            q26["eval_period"]="2026"; pred_out=pd.concat([q25,q26],ignore_index=True)
            status="OPA_V2_2026_PARTIAL_HOLDOUT_OPENED"

    if not pred_out.empty: pred_out.to_csv(OUT_PRED,index=False)

    summ={
        "schema":"OPA_H3_V2_TRANSITION","status":status,"panel_rows":len(p),"dev_rows":len(dev),
        "dev_grid":grid.to_dict("records"),"selected":selected,
        "confirmation_2025":ev25,"holdout_2026_partial":ev26
    }
    OUT_JSON.write_text(json.dumps(summ,indent=2,default=str)+"\n")

    lines=["# OPA-H3 V2 — MOMENTUM-OPPOSED POSITIONING TRANSITION RESULT","",f"**Status:** **{status}**","",
           "## DEV 2023-2024","",
           "| Rule | q | Actions | Rescue | Broken | Net | Precision | Rate | Eligible |",
           "|---|---:|---:|---:|---:|---:|---:|---:|---|"]
    for r in grid.sort_values(["quantile","rule"]).itertuples():
        lines.append(f"| {r.rule} | {r.quantile:.2f} | {r.actions} | {r.rescue} | {r.broken} | {r.net:+d} | {100*r.precision:.2f}% | {100*r.action_rate:.2f}% | {r.eligible} |")
    if selected:
        lines += ["","## Selected DEV rule","",
                  f"- rule: **{selected['rule']}**",
                  f"- oi_opp quantile: **{selected['quantile']:.2f}**",
                  f"- frozen numeric threshold: **{selected['oi_opp_threshold']:.8f}**"]
    if ev25:
        lines += ["","## 2025 untouched confirmation","",
                  f"- covered: **{ev25['covered_n']}**",
                  f"- candidates / OCS overlap / incremental: **{ev25['opa_candidates']} / {ev25['ocs_overlap']} / {ev25['incremental_actions']}**",
                  f"- rescue / broken / net: **{ev25['rescue']} / {ev25['broken']} / {ev25['net']:+d}**",
                  f"- precision: **{100*ev25['precision']:.2f}%**",
                  f"- SAGE -> assisted accuracy: **{100*ev25['sage_accuracy']:.2f}% -> {100*ev25['assisted_accuracy']:.2f}%**"]
    if ev26:
        lines += ["","## 2026 covered partial holdout","",
                  f"- covered: **{ev26['covered_n']}**",
                  f"- candidates / OCS overlap / incremental: **{ev26['opa_candidates']} / {ev26['ocs_overlap']} / {ev26['incremental_actions']}**",
                  f"- rescue / broken / net: **{ev26['rescue']} / {ev26['broken']} / {ev26['net']:+d}**",
                  f"- precision: **{100*ev26['precision']:.2f}%**",
                  f"- SAGE -> assisted accuracy: **{100*ev26['sage_accuracy']:.2f}% -> {100*ev26['assisted_accuracy']:.2f}%**",
                  "- note: official preliminary-OI source coverage ends 2026-03-19; this is not a full-year claim."]
    lines += ["","## Governance","",
              "V2 was designed after the V1 DEV failure using only the prespecified 2023-2024 DEV universe. 2025 was untouched confirmation; 2026 was opened only after a 2025 pass."]
    OUT_MD.write_text("\n".join(lines)+"\n")
    print(OUT_MD.read_text())

if __name__=="__main__": main()
