from __future__ import annotations

import importlib.util
import json
import os
from pathlib import Path

import numpy as np
import pandas as pd

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"SESSION_BOCPD_V1_STAGE3_OUT"
OUT.mkdir(exist_ok=True)

PREREG=AX/"GOLD_SESSION_BOCPD_V1_STAGE3_2025_PREREG_2026-10-07.md"
B2P=AX/"tools"/"gold_session_bocpd_v1_stage2_20261007.py"
M05P=AX/"tools"/"gold_session_model05b_structural_iris_1h_feature_selection_20261007.py"
SAGE25P=AX/"tools"/"gold_session_sage_frozen_2025_transport_20261007.py"
INCP=AX/"tools"/"gold_session_incremental_disagreement_v1_20261007.py"
FROZEN_STRUCT=AX/"GOLD_SESSION_MODEL05B_STRUCTURAL_IRIS_1H_FEATURE_SELECTION_FROZEN_FEATURES_2026-10-07.json"
STAGE2_GATE=AX/"GOLD_SESSION_BOCPD_V1_STAGE2_GATE_2026-10-07.csv"

DATASET="GLBX.MDP3"
SCHEMA="ohlcv-1h"
START="2025-01-01"
END="2026-01-01"
BASE_SYMBOLS=["GC.v.0","SI.v.0","NQ.v.0","ZN.n.0","CL.c.0"]
MAX_COST_USD=2.00

def loadmod(name,path):
    s=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(s)
    assert s.loader is not None
    s.loader.exec_module(m)
    return m

b2=loadmod("bocpd_stage2",B2P)
m05=loadmod("model05b",M05P)
sage25=loadmod("sage25",SAGE25P)
inc=loadmod("incremental",INCP)

def fetch_2025_databento():
    key=os.environ.get("DATABENTO_API_KEY","").strip()
    if not key:
        raise RuntimeError("DATABENTO_API_KEY_MISSING")
    import databento as db
    client=db.Historical(key)
    req=dict(dataset=DATASET,schema=SCHEMA,symbols=BASE_SYMBOLS,stype_in="continuous",start=START,end=END)
    cost=float(client.metadata.get_cost(**req))
    if cost>MAX_COST_USD:
        raise RuntimeError(f"COST_CAP_EXCEEDED:{cost:.6f}")
    q=client.timeseries.get_range(**req).to_df().reset_index()
    if "ts_event" not in q.columns and "index" in q.columns:
        q=q.rename(columns={"index":"ts_event"})
    need=["ts_event","symbol","instrument_id","open","high","low","close","volume"]
    miss=[c for c in need if c not in q.columns]
    if miss:
        raise RuntimeError(f"DATABENTO_MISSING_COLUMNS:{miss}")
    q=q[need].copy()
    q["ts_event"]=pd.to_datetime(q.ts_event,utc=True,errors="raise")
    q["symbol"]=q.symbol.astype(str)
    for c in ["open","high","low","close","volume"]:
        q[c]=pd.to_numeric(q[c],errors="raise")
    if set(BASE_SYMBOLS)-set(q.symbol.unique()):
        raise RuntimeError("DATABENTO_MISSING_SYMBOLS")
    if q.duplicated(["ts_event","symbol"]).any():
        raise RuntimeError("DATABENTO_DUPLICATE_TS_SYMBOL")
    q=q.sort_values(["symbol","ts_event"]).reset_index(drop=True)
    q.to_csv(OUT/"databento_base_2025.csv.gz",index=False,compression="gzip")
    return q,cost

def combined_archives(raw25):
    hist=b2.load_archives()
    out={}
    for roll in ["c","n","v"]:
        h=hist[roll].copy()
        suffix="."+roll+".0"
        z=raw25[raw25.symbol.str.endswith(suffix)].copy()
        z["available_at_utc"]=z.ts_event+pd.Timedelta(hours=1)
        z=z[["ts_event","available_at_utc","symbol","close","volume"]]
        q=pd.concat([h,z],ignore_index=True,sort=False)
        q=q.sort_values(["symbol","ts_event"]).drop_duplicates(["symbol","ts_event"],keep="last")
        out[roll]=q.reset_index(drop=True)
    return out

def build_path_panel_extended():
    p=m05.load_targets_extended().copy()
    p=p[p.start_utc.dt.year.isin([2022,2023,2024,2025])].reset_index(drop=True)
    p["row_id"]=np.arange(len(p))
    x15=m05.load_xau15_extended()
    p=m05.s14.ma15.attach(p,x15,"g")
    req=["g_ret_6h","g_ret_12h","g_rv_12","g_up_semivol_24","g_down_semivol_24",
         "g_upfrac_24","g_close_location_24","g_age_max_neg_24","g_age_max_pos_24",
         "g_jump_concentration_24","g_range_24","g_max_drawdown_24","g_recovery_24",
         "g_anchor_available","g_max_reference_stale_min"]
    p=p.dropna(subset=req+["direction"]).copy()
    if not (p.g_anchor_available<p.start_utc).all():
        raise RuntimeError("STAGE3_XAU_LEAK")
    if p.g_max_reference_stale_min.gt(60).any():
        raise RuntimeError("STAGE3_XAU_STALE")
    sign=np.where(p.g_ret_12h.to_numpy(float)>=0,1.0,-1.0)
    up2=p.g_up_semivol_24.to_numpy(float)**2
    dn2=p.g_down_semivol_24.to_numpy(float)**2
    total=up2+dn2+b2.EPS
    p["trend_strength"]=np.abs(p.g_ret_12h)/(p.g_rv_12+b2.EPS)
    p["opposite_semivar_share"]=np.where(sign>0,dn2/total,up2/total)
    p["deceleration_6h"]=-sign*(2.0*p.g_ret_6h-p.g_ret_12h)/(p.g_rv_12+b2.EPS)
    p["path_consistency"]=sign*(2.0*p.g_upfrac_24-1.0)
    p["trend_close_location"]=np.where(sign>0,p.g_close_location_24,1.0-p.g_close_location_24)
    p["opposite_extreme_recency"]=np.where(sign>0,1.0/(1.0+p.g_age_max_neg_24),1.0/(1.0+p.g_age_max_pos_24))
    p["jump_concentration_24"]=p.g_jump_concentration_24
    p["trend_to_range"]=np.abs(p.g_ret_12h)/(p.g_range_24+b2.EPS)
    p["adverse_excursion"]=np.where(sign>0,-p.g_max_drawdown_24/(p.g_range_24+b2.EPS),p.g_recovery_24/(p.g_range_24+b2.EPS))
    p["momentum_up"]=(p.g_ret_12h>=0).astype(int)
    p["year"]=p.start_utc.dt.year
    p["y_up"]=(p.direction=="UP").astype(int)
    h=m05.load_xau1h(x15)
    h["logp"]=np.log(h.value.astype(float))
    h["ny_date"]=h.available_at_utc.dt.tz_convert("America/New_York").dt.date
    vals=[]
    for r in p.itertuples(index=False):
        T=pd.Timestamp(r.start_utc)
        q=h[h.available_at_utc<T]
        d=q[q.ny_date==T.tz_convert("America/New_York").date()]
        if d.empty:
            vals.append(np.nan)
            continue
        sess=float(d.iloc[-1].logp-d.iloc[0].logp)
        s=1.0 if float(r.g_ret_12h)>=0 else -1.0
        vals.append(float(-s*sess/(float(r.g_rv_12)+b2.EPS)))
    p["session_against_trend"]=vals
    p=p.dropna(subset=["trend_strength","session_against_trend","trend_close_location","adverse_excursion","momentum_up"])
    return p.sort_values(["partition","window","start_utc"]).reset_index(drop=True)


def structural_2025():
    common,path_features,_=m05.build_common()
    frozen=json.loads(FROZEN_STRUCT.read_text())
    pred=m05.transport_2025(common,path_features,frozen)
    q=pred[
        pred.model.eq("S14_A1_PLUS_1H_FULL")&
        pred.partition.eq("SOBTI_5_ET")&
        pred.window.eq("NY_LONDON_LIT")
    ].copy()
    if q.empty:
        raise RuntimeError("NO_STRUCTURAL_2025")
    q["base_model"]="STRUCTURAL_IRIS_1H"
    return q[["partition","window","start_utc","end_utc","year","y_up","p_up","base_model"]]

def s17_asia_afternoon_2025():
    panel,_=m05.load_panel_extended()
    fa1=m05.fresh_a1_extended(panel)
    panel=panel.merge(fa1,on=["partition","window","start_utc"],how="inner",validate="one_to_one")
    rr=sage25.raw()
    cyc=sage25.cycles(rr)
    panel=pd.merge_asof(
        panel.sort_values("start_utc"),
        cyc.sort_values("sage_ready_utc"),
        left_on="start_utc",right_on="sage_ready_utc",
        direction="backward",allow_exact_matches=False
    )
    valid=panel.sage_ready_utc.notna()
    if not (panel.loc[valid,"sage_ready_utc"]<panel.loc[valid,"start_utc"]).all():
        raise RuntimeError("S17_SAGE_LEAK")
    x1=sage25.x1h(rr)
    panel=panel.reset_index(drop=True)
    panel["row_id"]=np.arange(len(panel))
    panel=sage25.res1h.attach(panel,x1,"g1h","1h")
    f1=sage25.res1h.feature_names("g1h")
    feats=["a1_logit"]+sage25.v1.SESSION_ALL
    panel=panel.dropna(subset=feats+f1+["direction"]).copy()
    g=panel[
        panel.partition.eq("SOBTI_5_ET")&
        panel.window.eq("ASIA_AFTERNOON_LIT")
    ].sort_values("start_utc").reset_index(drop=True)
    teall=g[g.year.eq(2025)].reset_index(drop=True)
    rows=[]
    for bs in range(0,len(teall),sage25.BLOCK):
        te=teall.iloc[bs:bs+sage25.BLOCK].copy()
        if te.empty:
            continue
        cutoff=te.start_utc.min()
        tr=g[(g.end_utc<=cutoff)&(g.start_utc<cutoff)].copy()
        if len(tr)<sage25.v1.MIN_A1 or tr.y_up.nunique()<2:
            continue
        pp=sage25.v1.fit_predict(tr,te,feats)
        for r,pv in zip(te.itertuples(index=False),pp):
            rows.append({
                "partition":r.partition,"window":r.window,
                "start_utc":r.start_utc,"end_utc":r.end_utc,
                "year":2025,"y_up":int(r.y_up),"p_up":float(pv),
                "base_model":"S17_A1_SESSION"
            })
    q=pd.DataFrame(rows)
    if q.empty:
        raise RuntimeError("NO_S17_ASIA_AFTERNOON_2025")
    return q

def historical_eligible_bases():
    long,_=inc.load_models()
    q=long[
        (
            long.partition.eq("SOBTI_5_ET")&
            long.window.eq("ASIA_AFTERNOON_LIT")&
            long.model.eq("S17_A1_SESSION")
        )|
        (
            long.partition.eq("SOBTI_5_ET")&
            long.window.eq("NY_LONDON_LIT")&
            long.model.eq("STRUCTURAL_IRIS_1H")
        )
    ].copy()
    q=q.rename(columns={"model":"base_model"})
    return q[["partition","window","start_utc","end_utc","year","y_up","p_up","base_model"]]

def replay_2025(hist_plus_2025,state):
    z=hist_plus_2025.merge(
        state[["partition","window","start_utc","momentum_up","leadlag_score_premax","internal_now","internal_d1"]],
        on=["partition","window","start_utc"],how="inner",validate="one_to_one"
    )
    z=z[z.start_utc.dt.year.isin([2023,2024,2025])].copy()
    z["baseline_pred"]=(z.p_up>=0.5).astype(int)
    z["baseline_correct"]=z.baseline_pred.eq(z.y_up.astype(int))
    z["handoff_alarm"]=(
        (pd.to_numeric(z.leadlag_score_premax,errors="coerce")>=0.60)&
        (pd.to_numeric(z.internal_now,errors="coerce")>=0.60)&
        (pd.to_numeric(z.internal_d1,errors="coerce")>=0.0)&
        z.baseline_pred.eq(z.momentum_up.astype(int))
    )
    z["competence_y"]=(~z.baseline_correct).astype(int)
    z["act"]=False
    z["p_rescue_pre"]=np.nan
    z["p_theta_gt_half_pre"]=np.nan
    z["n_updates_pre"]=np.nan
    timeline=[]
    for (part,win),idx in z.groupby(["partition","window"],sort=True).groups.items():
        ids=sorted(list(idx),key=lambda j:z.loc[j,"start_utc"])
        model=b2.BetaBernoulliBOCPD()
        pending=[]
        for j in ids:
            row=z.loc[j]
            T=pd.Timestamp(row.start_utc)
            matured=[x for x in pending if x["maturity"]<=T]
            pending=[x for x in pending if x["maturity"]>T]
            matured.sort(key=lambda x:(x["maturity"],x["origin"]))
            for x in matured:
                model.update(x["y"])
            if not bool(row.handoff_alarm):
                continue
            pre=model.predictive()
            act=bool(pre["p_rescue"]>=b2.PRED_THRESHOLD and pre["p_theta_gt_half"]>=b2.P_GT_HALF_THRESHOLD)
            z.at[j,"act"]=act
            z.at[j,"p_rescue_pre"]=pre["p_rescue"]
            z.at[j,"p_theta_gt_half_pre"]=pre["p_theta_gt_half"]
            z.at[j,"n_updates_pre"]=pre["n_updates"]
            pending.append({"maturity":pd.Timestamp(row.end_utc),"origin":T,"y":int(row.competence_y)})
            if T.year==2025:
                timeline.append({
                    "partition":part,"window":win,"base_model":row.base_model,
                    "start_utc":T,"end_utc":pd.Timestamp(row.end_utc),
                    "y_up":int(row.y_up),"baseline_pred":int(row.baseline_pred),
                    "momentum_up":int(row.momentum_up),"act":act,
                    "outcome":"RESCUE" if int(row.competence_y)==1 else "BROKEN",
                    **pre
                })
    z["p_assisted"]=z.p_up.astype(float)
    z.loc[z.act,"p_assisted"]=1.0-z.loc[z.act,"p_up"].astype(float)
    return z,pd.DataFrame(timeline)


def metrics_and_gate(z):
    rows=[]
    gates=[]
    s2=pd.read_csv(STAGE2_GATE)
    for (part,win),g in z.groupby(["partition","window"],sort=True):
        d=g[g.start_utc.dt.year.isin([2023,2024])].copy()
        old=s2[(s2.partition.eq(part))&(s2.window.eq(win))].iloc[0]
        if len(d)!=int(old.base_eligible_n):
            raise RuntimeError(f"STAGE2_N_MISMATCH:{part}:{win}:{len(d)}:{int(old.base_eligible_n)}")
        if int(d.handoff_alarm.sum())!=int(old.base_handoff_alarms):
            raise RuntimeError(f"STAGE2_ALARM_MISMATCH:{part}:{win}")
        if int(d.act.sum())!=int(old.base_acts):
            raise RuntimeError(f"STAGE2_ACT_MISMATCH:{part}:{win}")

        q=g[g.start_utc.dt.year.eq(2025)].copy()
        if q.empty:
            raise RuntimeError(f"NO_2025_ROWS:{part}:{win}")
        mb=b2.metric(q.y_up,q.p_up)
        ma=b2.metric(q.y_up,q.p_assisted)
        acted=q[q.act].copy()
        rescue=int((~acted.baseline_correct).sum())
        broken=int(acted.baseline_correct.sum())
        net=rescue-broken
        passed=bool(
            int(q.act.sum())>=1 and
            net>0 and
            ma["balanced_accuracy"]+1e-12>=mb["balanced_accuracy"] and
            ma["accuracy"]+0.01+1e-12>=mb["accuracy"]
        )
        rows.append({
            "partition":part,"window":win,"base_model":q.base_model.iloc[0],
            "n":int(len(q)),"handoff_alarms":int(q.handoff_alarm.sum()),
            "acts":int(q.act.sum()),"rescue":rescue,"broken":broken,
            "net_rescue":net,"action_precision":float(rescue/max(len(acted),1)),
            **{f"base_{k}":v for k,v in mb.items()},
            **{f"assisted_{k}":v for k,v in ma.items()}
        })
        gates.append({
            "partition":part,"window":win,"base_model":q.base_model.iloc[0],
            "retained":passed,"reason":"PASS" if passed else "TRANSPORT_FAIL",
            "n":int(len(q)),"acts":int(q.act.sum()),"rescue":rescue,
            "broken":broken,"net_rescue":net,
            "base_ba":mb["balanced_accuracy"],"assisted_ba":ma["balanced_accuracy"],
            "base_accuracy":mb["accuracy"],"assisted_accuracy":ma["accuracy"]
        })
    return pd.DataFrame(rows),pd.DataFrame(gates)

def main():
    if "FROZEN BEFORE 2025 BOCPD RESULT" not in PREREG.read_text():
        raise RuntimeError("STAGE3_PREREG_MISSING")

    raw25,cost=fetch_2025_databento()
    archives=combined_archives(raw25)
    path=build_path_panel_extended()

    mapping=b2.VARIANTS["BASE"]
    raw_ifbc=b2.build_ifbc_raw(path,archives,mapping)
    ifbc=b2.apply_ifbc_calibration(raw_ifbc)
    hourly=b2.sync_hourly(archives,mapping)
    llrs=b2.build_llrs(path,hourly)
    state=b2.build_handoff_state(ifbc,llrs)

    hist=historical_eligible_bases()
    y25=pd.concat([s17_asia_afternoon_2025(),structural_2025()],ignore_index=True)
    allbase=pd.concat([hist,y25],ignore_index=True,sort=False)
    allbase["start_utc"]=pd.to_datetime(allbase.start_utc,utc=True)
    allbase["end_utc"]=pd.to_datetime(allbase.end_utc,utc=True)
    allbase["year"]=allbase.start_utc.dt.year
    allbase=allbase.sort_values(["partition","window","start_utc"]).drop_duplicates(
        ["partition","window","start_utc"],keep="last"
    ).reset_index(drop=True)

    z,timeline=replay_2025(allbase,state)
    metrics,gate=metrics_and_gate(z)

    timeline.to_csv(OUT/"actions_2025.csv",index=False)
    metrics.to_csv(OUT/"metrics_2025.csv",index=False)
    gate.to_csv(OUT/"gate_2025.csv",index=False)

    retained=gate[gate.retained].to_dict("records")
    summary={
        "status":"SESSION_BOCPD_V1_STAGE3_2025_COMPLETE",
        "databento_2025":{
            "dataset":DATASET,"schema":SCHEMA,"symbols":BASE_SYMBOLS,
            "start":START,"end":END,"estimated_cost_usd":cost,"rows":int(len(raw25))
        },
        "eligible_heads_opened":[
            "SOBTI_5_ET/ASIA_AFTERNOON_LIT/S17_A1_SESSION",
            "SOBTI_5_ET/NY_LONDON_LIT/STRUCTURAL_IRIS_1H"
        ],
        "metrics":metrics.to_dict("records"),
        "gate":gate.to_dict("records"),
        "retained":retained,
        "stage4_2026":{
            "status":"DATA_BLOCKED",
            "reason":"No governed V5-equivalent 2026 SESSION target population; 2026 is not used for BOCPD tuning or transport selection."
        },
        "guardrails":[
            "Only Stage-2 eligible heads were opened in 2025.",
            "BOCPD thresholds, hazard and Handoff rules are unchanged.",
            "BASE continuous mapping only; no source selection on 2025 outcomes.",
            "Stage-2 chronology is reproduced exactly before accepting the 2025 replay.",
            "2026 remains closed and data-blocked."
        ]
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")

    lines=[
        "# GOLD SESSION — BOCPD V1 FROZEN 2025 TRANSPORT RESULT","",
        "**Status:** SESSION_BOCPD_V1_STAGE3_2025_COMPLETE","",
        f"- Databento 2025 BASE raw cost estimate: **USD {cost:.4f}**.",
        "- Only the two Stage-2 eligible heads were opened.",
        "- No BOCPD/Handoff/source parameter was retuned.","",
        "## 2025 frozen transport","",
        "| Partition | Window | Base | N | Handoff | ACT | Rescue | Break | Net | Precision | Base BA | Assisted BA | Base Acc | Assisted Acc | Decision |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    gmap={(r.partition,r.window):r for r in gate.itertuples(index=False)}
    for r in metrics.itertuples(index=False):
        gg=gmap[(r.partition,r.window)]
        lines.append(
            f"| {r.partition} | {r.window} | {r.base_model} | {r.n} | {r.handoff_alarms} | {r.acts} | "
            f"{r.rescue} | {r.broken} | {r.net_rescue:+d} | {100*r.action_precision:.1f}% | "
            f"{100*r.base_balanced_accuracy:.2f}% | {100*r.assisted_balanced_accuracy:.2f}% | "
            f"{100*r.base_accuracy:.2f}% | {100*r.assisted_accuracy:.2f}% | "
            f"{'RETAIN' if gg.retained else 'REJECT'} |"
        )
    lines += [
        "",
        "## 2026",
        "",
        "**DATA_BLOCKED** — no governed V5-equivalent 2026 SESSION target population is available. No daily/H3 label is substituted."
    ]
    (OUT/"result.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"status":summary["status"],"retained":retained,"metrics":summary["metrics"]},indent=2,default=str))

if __name__=="__main__":
    main()
