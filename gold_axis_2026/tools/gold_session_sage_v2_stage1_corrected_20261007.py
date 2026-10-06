from __future__ import annotations

import importlib.util,json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
V1_PATH=AX/"tools"/"gold_session_sage_v1_stage1_20261007.py"
OUT=AX/"SESSION_SAGE_V2_STAGE1_CORRECTED_OUT";OUT.mkdir(exist_ok=True)

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m
v1=loadmod("sagev1",V1_PATH)

def replay_a1_corrected(pa):
    rows=[]
    models={
      "S17_A1_SESSION":["a1_logit"]+v1.SESSION_ALL,
      "S18_A1_PATH_MATCHED":["a1_logit"]+v1.res1h.feature_names("g1h"),
      "S18_A1_PATH_SESSION":["a1_logit"]+v1.res1h.feature_names("g1h")+v1.SESSION_ALL,
    }
    for (part,win),g0 in pa.groupby(["partition","window"],sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        test=g[g.start_utc.dt.year.isin([2023,2024])].copy().reset_index(drop=True)
        for bs in range(0,len(test),v1.BLOCK):
            te=test.iloc[bs:bs+v1.BLOCK].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
            if len(tr)<v1.MIN_A1 or tr.y_up.nunique()<2:continue

            # Binding fresh A1 direct comparator: no downstream refit.
            for r in te.itertuples(index=False):
                rows.append({
                  "stage_role":"S1.7-8","model":"S17_A1_DIRECT_MATCHED",
                  "partition":part,"window":win,"label_date":r.label_date,
                  "start_utc":r.start_utc,"end_utc":r.end_utc,"year":int(r.start_utc.year),
                  "y_up":int(r.y_up),"p_up":float(r.p_A1_arcr),"train_n":len(tr),
                  "sage_local_date":r.sage_local_date,"sage_ready_utc":r.sage_ready_utc,
                  "sage_age_hours":float(r.sage_age_hours),
                })
            for tag,features in models.items():
                p=v1.fit_predict(tr,te,features)
                for r,pp in zip(te.itertuples(index=False),p):
                    rows.append({
                      "stage_role":"S1.7-8","model":tag,"partition":part,"window":win,
                      "label_date":r.label_date,"start_utc":r.start_utc,"end_utc":r.end_utc,
                      "year":int(r.start_utc.year),"y_up":int(r.y_up),"p_up":float(pp),
                      "train_n":len(tr),"sage_local_date":r.sage_local_date,
                      "sage_ready_utc":r.sage_ready_utc,"sage_age_hours":float(r.sage_age_hours),
                    })
    return pd.DataFrame(rows)

def standalone_gate_correct(mdf):
    rows=[]
    q=mdf[(mdf.stage_role=="S1.5-6")&(mdf.model=="S15_SESSION_ONLY")].copy()
    for (part,win),g in q.groupby(["partition","window"],sort=True):
        comb=g[g.period=="2023-2024_SCORED"]
        if comb.empty:continue
        c=comb.iloc[0]
        year_ok=True
        for r in g[g.period.isin(["2023","2024"])].itertuples(index=False):
            if r.n>=40 and r.balanced_accuracy<.50:year_ok=False
        eligible=bool(c.n>=80 and min(c.up_recall,c.down_recall)>=.30 and c.balanced_accuracy>=.52 and year_ok)
        reasons=[]
        if c.n<80:reasons.append("N_LT_80")
        if min(c.up_recall,c.down_recall)<.30:reasons.append("RECALL_FLOOR")
        if c.balanced_accuracy<.52:reasons.append("BA_LT_52")
        if not year_ok:reasons.append("YEAR_BA_LT_50")
        rows.append({"stage_role":"S1.5","partition":part,"window":win,"candidate":"S15_SESSION_ONLY",
                     "comparator":"NONE","combined_n":int(c.n),"eligible":eligible,
                     "reason":"PASS" if eligible else "|".join(reasons)})
    return rows

def main():
    if "PREREGISTERED BEFORE SESSION-SAGE RESULTS" not in v1.PREREG.read_text():
        raise RuntimeError("SAGE_PREREG_MISSING")

    panel,_=v1.s14.build_panel()
    panel=panel.reset_index(drop=True);panel["row_id"]=np.arange(len(panel))
    cycles=v1.build_sage_cycles(v1.load_raw_ohlc())
    panel=v1.attach_sage(panel,cycles)

    raw15=v1.s14.combined_raw15();raw1h=v1.s14.xau1h_from_15m(raw15)
    panel=v1.res1h.attach(panel,raw1h,"g1h","1h")
    f1h=v1.res1h.feature_names("g1h")

    p_direct=panel.dropna(subset=v1.SESSION_ALL+f1h+["direction"]).copy()
    if not (p_direct.sage_ready_utc<p_direct.start_utc).all():raise RuntimeError("SAGE_TIME_LEAK_DIRECT")
    direct_models={
      "S15_SESSION_ONLY":v1.SESSION_ALL,
      "S16_PATH_GLOBAL_MATCHED":f1h,
      "S16_PATH_SESSION":f1h+v1.SESSION_ALL,
    }
    d=v1.replay(p_direct,direct_models,v1.MIN_DIRECT,"S1.5-6")

    fa1=v1.s14.fresh_a1_with_warmup(panel)
    pa=panel.merge(fa1,on=["partition","window","start_utc"],how="inner",validate="one_to_one")
    pa=pa.dropna(subset=["a1_logit"]+v1.SESSION_ALL+f1h+["direction"]).copy()
    if not (pa.sage_ready_utc<pa.start_utc).all():raise RuntimeError("SAGE_TIME_LEAK_A1")
    a=replay_a1_corrected(pa)

    pred=pd.concat([d,a],ignore_index=True)
    mdf=v1.metrics_frame(pred)
    p16=v1.paired(pred,"S1.5-6","S16_PATH_SESSION","S16_PATH_GLOBAL_MATCHED")
    p17=v1.paired(pred,"S1.7-8","S17_A1_SESSION","S17_A1_DIRECT_MATCHED")
    p18=v1.paired(pred,"S1.7-8","S18_A1_PATH_SESSION","S18_A1_PATH_MATCHED")
    pdf=pd.concat([p16,p17,p18],ignore_index=True)

    gates=standalone_gate_correct(mdf)+v1.pair_gate(pdf)
    gdf=pd.DataFrame(gates)

    samples=[]
    for (part,win),g in panel.dropna(subset=v1.SESSION_ALL).groupby(["partition","window"],sort=True):
        z=pd.concat([g.sort_values("start_utc").head(2),g.sort_values("start_utc").tail(2)]).drop_duplicates("start_utc")
        for r in z.itertuples(index=False):
            samples.append({"partition":part,"window":win,"label_date":r.label_date,
                            "target_start_utc":r.start_utc,"sage_local_date":r.sage_local_date,
                            "sage_ready_utc":r.sage_ready_utc,"sage_age_hours":r.sage_age_hours,
                            "strict_before":bool(r.sage_ready_utc<r.start_utc)})
    sdf=pd.DataFrame(samples)

    coverage=[]
    for (part,win),g in p_direct.groupby(["partition","window"],sort=True):
        q=d[(d.partition==part)&(d.window==win)&(d.model=="S15_SESSION_ONLY")]
        aq=a[(a.partition==part)&(a.window==win)&(a.model=="S17_A1_SESSION")]
        coverage.append({"partition":part,"window":win,"direct_feature_rows":len(g),
                         "s15_scored":len(q),"s15_2023":int((q.year==2023).sum()),"s15_2024":int((q.year==2024).sum()),
                         "a1_sage_scored":len(aq),"a1_sage_2023":int((aq.year==2023).sum()),"a1_sage_2024":int((aq.year==2024).sum()),
                         "median_sage_age_hours":float(g.sage_age_hours.median())})
    cdf=pd.DataFrame(coverage)

    pred.to_csv(OUT/"predictions.csv",index=False);mdf.to_csv(OUT/"metrics.csv",index=False)
    pdf.to_csv(OUT/"paired.csv",index=False);gdf.to_csv(OUT/"transport_eligibility.csv",index=False)
    sdf.to_csv(OUT/"timing_samples.csv",index=False);cdf.to_csv(OUT/"coverage.csv",index=False)

    summary={
      "status":"SESSION_SAGE_V2_STAGE1_IMPLEMENTATION_CORRECTED_COMPLETE",
      "supersedes":"SESSION_SAGE_V1_STAGE1_COMPLETE for S1.5 gate and S1.7 direct-A1 comparison",
      "scope":"2022 warmup/training only; 2023-2024 scored; 2025/2026 unopened",
      "prereg":v1.PREREG.name,
      "corrections":[
        "S1.5 standalone eligibility filter now evaluates the actual S1.5-6 metric rows.",
        "S1.7 comparator now uses fresh p_A1_arcr directly; no downstream logistic refit of A1 logit."
      ],
      "transport_eligibility":gates,
      "metrics":mdf.to_dict("records"),
      "paired":pdf.to_dict("records"),
      "coverage":coverage,
      "guardrails":[
        "No preregistered rule, threshold, feature or clock changed after V1 results.",
        "Only implementation defects were corrected.",
        "2025/2026 unopened."
      ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD SESSION SAGE V2 — IMPLEMENTATION-CORRECTED STAGE-1 RESULT","",
      "**Status:** SESSION_SAGE_V2_STAGE1_IMPLEMENTATION_CORRECTED_COMPLETE","",
      "- Preregistered rules unchanged.",
      "- S1.5 gate filter corrected.",
      "- S1.7 comparator corrected to direct fresh A1 probability.",
      "- 2025/2026 unopened.","",
      "## Frozen-transport eligibility","",
      "| Stage | Partition | Window | Candidate | Comparator | N | Eligible | Reason |",
      "|---|---|---|---|---|---:|---|---|"]
    for r in gdf.itertuples(index=False):
        lines.append(f"| {r.stage_role} | {r.partition} | {r.window} | {r.candidate} | {r.comparator} | {r.combined_n} | {r.eligible} | {r.reason} |")
    lines+=["","## Combined 2023-2024 metrics","",
      "| Stage | Model | Partition | Window | N | Acc | BA | UP | DOWN | Brier |",
      "|---|---|---|---|---:|---:|---:|---:|---:|---:|"]
    for r in mdf[mdf.period=="2023-2024_SCORED"].itertuples(index=False):
        lines.append(f"| {r.stage_role} | {r.model} | {r.partition} | {r.window} | {r.n} | {100*r.accuracy:.2f}% | {100*r.balanced_accuracy:.2f}% | {100*r.up_recall:.2f}% | {100*r.down_recall:.2f}% | {r.brier:.4f} |")
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":summary["status"],"gates":gates},indent=2))

if __name__=="__main__":main()
