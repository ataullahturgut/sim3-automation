from __future__ import annotations

import importlib.util, json
from pathlib import Path
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
S14_PATH=AX/"tools"/"gold_session_structural_iris_s14_v2_warmup2022_20261007.py"
PREREG=AX/"GOLD_SESSION_SAGE_V1_PREREG_2026-10-07.md"
WARM_RAW=AX/"GOLD_XAUUSD_15M_UTC_2022_WITH_BUFFER.csv"
RAW=AX/"GOLD_XAUUSD_15M_UTC_2023_2025_WITH_BUFFER.csv"
OUT=AX/"SESSION_SAGE_V1_STAGE1_OUT";OUT.mkdir(exist_ok=True)

NY=ZoneInfo("America/New_York")
SEED=20261007
BLOCK=5
MIN_DIRECT=120
MIN_A1=80

SESSION_RET=["sess_asia","sess_europe","sess_us_am","sess_us_pm"]
SESSION_PHASE=[
 "sess_us_total","sess_west_total","sess_east_west","sess_us_reversal",
 "sess_dispersion","sess_sign_changes","sess_dominance",
 "sess_asia_us_interaction","sess_east_west_conflict","sess_us_conflict"
]
SESSION_ALL=SESSION_RET+SESSION_PHASE

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s);assert s.loader is not None;s.loader.exec_module(m);return m

s14=loadmod("s14v2",S14_PATH)
base=s14.base
res1h=s14.res1h
v15=s14.v15

def load_raw_ohlc():
    a=pd.read_csv(WARM_RAW);b=pd.read_csv(RAW)
    for q in (a,b):
        q["dt_utc"]=pd.to_datetime(q.dt_utc,utc=True)
        for c in ["open","high","low","close"]:q[c]=pd.to_numeric(q[c],errors="raise")
    b=b[b.dt_utc<pd.Timestamp("2025-01-01",tz="UTC")].copy()
    q=pd.concat([a[["dt_utc","open","high","low","close"]],b[["dt_utc","open","high","low","close"]]],ignore_index=True)
    q=q.sort_values("dt_utc").drop_duplicates("dt_utc",keep="last")
    q=q[(q.dt_utc>=pd.Timestamp("2021-12-30",tz="UTC"))&(q.dt_utc<pd.Timestamp("2025-01-01",tz="UTC"))].copy()
    return q.reset_index(drop=True)

def ny_boundary(d,hh,mm=0):
    return pd.Timestamp(datetime(d.year,d.month,d.day,hh,mm,tzinfo=NY)).tz_convert("UTC")

def build_sage_cycles(raw):
    op=dict(zip(raw.dt_utc,raw.open.astype(float)))
    local_dates=pd.date_range("2022-01-01","2024-12-31",freq="D").date
    rows=[]
    for d in local_dates:
        prev=d-timedelta(days=1)
        ts18=ny_boundary(prev,18);ts03=ny_boundary(d,3);ts08=ny_boundary(d,8);ts12=ny_boundary(d,12);ts16=ny_boundary(d,16)
        keys=[ts18,ts03,ts08,ts12,ts16]
        if not all(t in op for t in keys):continue
        lp=np.log([op[t] for t in keys])
        asia=float(lp[1]-lp[0]);eu=float(lp[2]-lp[1]);uam=float(lp[3]-lp[2]);upm=float(lp[4]-lp[3])
        seq=np.array([asia,eu,uam,upm],float)
        ust=uam+upm;west=eu+ust
        signs=np.sign(seq)
        ready=ny_boundary(d,16,15)
        rows.append({
          "sage_local_date":str(d),"sage_ready_utc":ready,
          "sage_18_utc":ts18,"sage_03_utc":ts03,"sage_08_utc":ts08,"sage_12_utc":ts12,"sage_16_utc":ts16,
          "sess_asia":asia,"sess_europe":eu,"sess_us_am":uam,"sess_us_pm":upm,
          "sess_us_total":ust,"sess_west_total":west,"sess_east_west":asia-west,
          "sess_us_reversal":upm-uam,"sess_dispersion":float(np.std(seq,ddof=0)),
          "sess_sign_changes":float(np.sum(signs[1:]*signs[:-1]<0)),
          "sess_dominance":float(np.max(np.abs(seq))/(np.sum(np.abs(seq))+1e-10)),
          "sess_asia_us_interaction":float(asia*ust),
          "sess_east_west_conflict":float(asia*west<0),
          "sess_us_conflict":float(uam*upm<0),
        })
    z=pd.DataFrame(rows).sort_values("sage_ready_utc").reset_index(drop=True)
    if z.empty:raise RuntimeError("NO_SAGE_CYCLES")
    return z

def attach_sage(panel,cycles):
    a=panel.sort_values("start_utc").copy()
    out=pd.merge_asof(
      a,cycles.sort_values("sage_ready_utc"),
      left_on="start_utc",right_on="sage_ready_utc",
      direction="backward",allow_exact_matches=False
    )
    valid=out.sage_ready_utc.notna()
    if not (out.loc[valid,"sage_ready_utc"]<out.loc[valid,"start_utc"]).all():raise RuntimeError("SAGE_READY_LEAK")
    out["sage_age_hours"]=(out.start_utc-out.sage_ready_utc).dt.total_seconds()/3600.0
    return out

def fit_predict(tr,te,features):
    Xtr=tr[features].astype(float).to_numpy();Xte=te[features].astype(float).to_numpy()
    sc=StandardScaler().fit(Xtr)
    m=LogisticRegression(C=1.0,solver="lbfgs",max_iter=5000,random_state=SEED)
    m.fit(sc.transform(Xtr),tr.y_up.to_numpy(int))
    return m.predict_proba(sc.transform(Xte))[:,1]

def replay(panel,models,min_train,role):
    rows=[]
    gcols=["partition","window"]
    for (part,win),g0 in panel.groupby(gcols,sort=True):
        g=g0.sort_values("start_utc").reset_index(drop=True)
        test=g[g.start_utc.dt.year.isin([2023,2024])].copy().reset_index(drop=True)
        for bs in range(0,len(test),BLOCK):
            te=test.iloc[bs:bs+BLOCK].copy()
            if te.empty:continue
            cutoff=te.start_utc.min()
            tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
            if len(tr)<min_train or tr.y_up.nunique()<2:continue
            for tag,features in models.items():
                p=fit_predict(tr,te,features)
                for r,pp in zip(te.itertuples(index=False),p):
                    rows.append({
                      "stage_role":role,"model":tag,"partition":part,"window":win,
                      "label_date":r.label_date,"start_utc":r.start_utc,"end_utc":r.end_utc,
                      "year":int(r.start_utc.year),"y_up":int(r.y_up),"p_up":float(pp),
                      "train_n":len(tr),"sage_local_date":r.sage_local_date,
                      "sage_ready_utc":r.sage_ready_utc,"sage_age_hours":float(r.sage_age_hours),
                    })
    return pd.DataFrame(rows)

def metrics_frame(pred):
    rows=[]
    for (role,model,part,win,yr),g in pred.groupby(["stage_role","model","partition","window","year"],sort=True):
        rows.append({"stage_role":role,"model":model,"partition":part,"window":win,"period":str(yr),**base.base.metrics(g.y_up,g.p_up)})
    for (role,model,part,win),g in pred.groupby(["stage_role","model","partition","window"],sort=True):
        rows.append({"stage_role":role,"model":model,"partition":part,"window":win,"period":"2023-2024_SCORED",**base.base.metrics(g.y_up,g.p_up)})
    return pd.DataFrame(rows)

def paired(pred,role,candidate,comparator):
    a=pred[(pred.stage_role==role)&(pred.model==candidate)].copy()
    b=pred[(pred.stage_role==role)&(pred.model==comparator)].copy()
    keys=["partition","window","label_date","start_utc","year","y_up"]
    z=a.merge(b,on=keys,suffixes=("_cand","_comp"),validate="one_to_one")
    rows=[]
    for (part,win),g0 in z.groupby(["partition","window"],sort=True):
        for period,g in [("2023",g0[g0.year==2023]),("2024",g0[g0.year==2024]),("2023-2024_SCORED",g0)]:
            if g.empty:continue
            mc=base.base.metrics(g.y_up,g.p_up_cand);mb=base.base.metrics(g.y_up,g.p_up_comp)
            rows.append({
              "stage_role":role,"partition":part,"window":win,"period":period,
              "candidate":candidate,"comparator":comparator,"n":len(g),
              "candidate_accuracy":mc["accuracy"],"candidate_ba":mc["balanced_accuracy"],"candidate_brier":mc["brier"],
              "candidate_up_recall":mc["up_recall"],"candidate_down_recall":mc["down_recall"],
              "comparator_accuracy":mb["accuracy"],"comparator_ba":mb["balanced_accuracy"],"comparator_brier":mb["brier"],
              "comparator_up_recall":mb["up_recall"],"comparator_down_recall":mb["down_recall"],
              "delta_ba_pp":100*(mc["balanced_accuracy"]-mb["balanced_accuracy"]),
              "delta_brier":mc["brier"]-mb["brier"],
            })
    return pd.DataFrame(rows)

def standalone_session_gate(mdf):
    rows=[]
    q=mdf[(mdf.stage_role=="S1.5")&(mdf.model=="S15_SESSION_ONLY")].copy()
    for (part,win),g in q.groupby(["partition","window"],sort=True):
        comb=g[g.period=="2023-2024_SCORED"]
        if comb.empty:continue
        c=comb.iloc[0]
        years={r.period:r for r in g[g.period.isin(["2023","2024"])].itertuples(index=False)}
        year_ok=True
        for y,r in years.items():
            if r.n>=40 and r.balanced_accuracy<.50:year_ok=False
        eligible=bool(c.n>=80 and min(c.up_recall,c.down_recall)>=.30 and c.balanced_accuracy>=.52 and year_ok)
        rows.append({"stage_role":"S1.5","partition":part,"window":win,"candidate":"S15_SESSION_ONLY",
                     "comparator":"NONE","combined_n":int(c.n),"eligible":eligible,
                     "reason":"PASS" if eligible else "FAIL_PREREG_GATE"})
    return rows

def pair_gate(pdf):
    rows=[]
    for (role,part,win,cand,comp),g in pdf.groupby(["stage_role","partition","window","candidate","comparator"],sort=True):
        comb=g[g.period=="2023-2024_SCORED"]
        if comb.empty:continue
        c=comb.iloc[0]
        year_ok=True
        y23=g[g.period=="2023"];y24=g[g.period=="2024"]
        if (not y23.empty) and (not y24.empty) and y23.iloc[0].n>=40 and y24.iloc[0].n>=40:
            if y23.iloc[0].candidate_ba+1e-12<y23.iloc[0].comparator_ba:year_ok=False
            if y24.iloc[0].candidate_ba+1e-12<y24.iloc[0].comparator_ba:year_ok=False
        eligible=bool(
          c.n>=80 and min(c.candidate_up_recall,c.candidate_down_recall)>=.30
          and c.candidate_ba+1e-12>=c.comparator_ba
          and c.candidate_brier<=c.comparator_brier+.010+1e-12
          and year_ok
        )
        reasons=[]
        if c.n<80:reasons.append("N_LT_80")
        if min(c.candidate_up_recall,c.candidate_down_recall)<.30:reasons.append("RECALL_FLOOR")
        if c.candidate_ba+1e-12<c.comparator_ba:reasons.append("BA_BELOW_COMPARATOR")
        if c.candidate_brier>c.comparator_brier+.010+1e-12:reasons.append("BRIER_GATE")
        if not year_ok:reasons.append("YEAR_SIGN_FAIL")
        rows.append({"stage_role":role,"partition":part,"window":win,"candidate":cand,"comparator":comp,
                     "combined_n":int(c.n),"eligible":eligible,"reason":"PASS" if eligible else "|".join(reasons)})
    return rows

def main():
    if "PREREGISTERED BEFORE SESSION-SAGE RESULTS" not in PREREG.read_text():raise RuntimeError("SAGE_PREREG_MISSING")

    panel,_=s14.build_panel()
    panel=panel.reset_index(drop=True);panel["row_id"]=np.arange(len(panel))
    raw_ohlc=load_raw_ohlc()
    cycles=build_sage_cycles(raw_ohlc)
    panel=attach_sage(panel,cycles)

    # Same-source 1h PATH from the governed 15m source.
    raw15=s14.combined_raw15()
    raw1h=s14.xau1h_from_15m(raw15)
    panel=res1h.attach(panel,raw1h,"g1h","1h")
    f1h=res1h.feature_names("g1h")

    # S1.5/S1.6 can use the 2022 warmup target history directly.
    p_direct=panel.dropna(subset=SESSION_ALL+f1h+["direction"]).copy()
    if not (p_direct.sage_ready_utc<p_direct.start_utc).all():raise RuntimeError("SAGE_TIME_LEAK_DIRECT")

    direct_models={
      "S15_SESSION_ONLY":SESSION_ALL,
      "S16_PATH_GLOBAL_MATCHED":f1h,
      "S16_PATH_SESSION":f1h+SESSION_ALL,
    }
    d=replay(p_direct,direct_models,MIN_DIRECT,"S1.5-6")

    # Fresh A1 is generated using 2022 warmup but exists only on 2023-2024 targets.
    fa1=s14.fresh_a1_with_warmup(panel)
    pa=panel.merge(fa1,on=["partition","window","start_utc"],how="inner",validate="one_to_one")
    pa=pa.dropna(subset=["a1_logit"]+SESSION_ALL+f1h+["direction"]).copy()
    if not (pa.sage_ready_utc<pa.start_utc).all():raise RuntimeError("SAGE_TIME_LEAK_A1")

    a1_models={
      "S17_A1_DIRECT_MATCHED":["a1_logit"],
      "S17_A1_SESSION":["a1_logit"]+SESSION_ALL,
      "S18_A1_PATH_MATCHED":["a1_logit"]+f1h,
      "S18_A1_PATH_SESSION":["a1_logit"]+f1h+SESSION_ALL,
    }
    a=replay(pa,a1_models,MIN_A1,"S1.7-8")

    pred=pd.concat([d,a],ignore_index=True)
    mdf=metrics_frame(pred)

    p16=paired(pred,"S1.5-6","S16_PATH_SESSION","S16_PATH_GLOBAL_MATCHED")
    p17=paired(pred,"S1.7-8","S17_A1_SESSION","S17_A1_DIRECT_MATCHED")
    p18=paired(pred,"S1.7-8","S18_A1_PATH_SESSION","S18_A1_PATH_MATCHED")
    pdf=pd.concat([p16,p17,p18],ignore_index=True)

    gates=standalone_session_gate(mdf)+pair_gate(pdf)
    gdf=pd.DataFrame(gates)

    # Timing audit samples.
    samples=[]
    for (part,win),g in panel.dropna(subset=SESSION_ALL).groupby(["partition","window"],sort=True):
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
        coverage.append({"partition":part,"window":win,"direct_feature_rows":len(g),
                         "s15_scored":len(q),"s15_2023":int((q.year==2023).sum()),"s15_2024":int((q.year==2024).sum()),
                         "median_sage_age_hours":float(g.sage_age_hours.median())})
    cdf=pd.DataFrame(coverage)

    pred.to_csv(OUT/"predictions.csv",index=False)
    mdf.to_csv(OUT/"metrics.csv",index=False)
    pdf.to_csv(OUT/"paired.csv",index=False)
    gdf.to_csv(OUT/"transport_eligibility.csv",index=False)
    sdf.to_csv(OUT/"timing_samples.csv",index=False)
    cdf.to_csv(OUT/"coverage.csv",index=False)
    cycles.to_csv(OUT/"sage_cycles.csv",index=False)

    summary={
      "status":"SESSION_SAGE_V1_STAGE1_COMPLETE",
      "scope":"2022 warmup/training only; 2023-2024 scored; 2025/2026 unopened",
      "prereg":PREREG.name,
      "session_features":SESSION_ALL,
      "source_rule":"exact 15m OPEN boundaries; SAGE cycle ready at 16:15 NY; latest ready strictly before target start",
      "models":direct_models|a1_models,
      "coverage":coverage,
      "transport_eligibility":gates,
      "metrics":mdf.to_dict("records"),
      "paired":pdf.to_dict("records"),
      "guardrails":[
        "SAGE preregistration committed before result run.",
        "2022 warmup only; no 2022 score used for promotion.",
        "Fresh A1 regenerated from raw daily metals; no archived A1/H3-SAGE predictions used.",
        "Same-source-derived 1h XAU PATH.",
        "SAGE ready time must be strictly earlier than target start.",
        "2025/2026 unopened."
      ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=["# GOLD SESSION SAGE V1 — STAGE-1 RESULT","",
      "**Status:** SESSION_SAGE_V1_STAGE1_COMPLETE","",
      "- 2022 warmup/training only; 2023–2024 scored.",
      "- 2025/2026 unopened.",
      "- SAGE phase contract preregistered before results.","",
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
    print(json.dumps({"status":summary["status"],"gates":gates},indent=2,default=str))

if __name__=="__main__":main()
