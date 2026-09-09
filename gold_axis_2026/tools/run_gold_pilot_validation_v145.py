from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
AUDITS = ROOT / "data_pipeline/audits"
PILOT_MONTHS = [f"{y}-{m:02d}" for y, months in ((2025, range(1, 13)), (2026, range(1, 9))) for m in months]
ENGINES = ["CAUSAL_PATCH", "VW_MIDAS_MSVR_SUCCESSOR_V1", "MOMENTUM_3M", "RANDOM_WALK",
           "MONTHLY_DIRECTION_3M", "FAST", "SLOW", "MACRO_EVENT_SUCCESSOR_V2",
           "BOCPD_RETURN_SUCCESSOR_V1", "EMERGENCY_LEVEL", "EMERGENCY_REVERSAL", "GVZ_RISK"]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sign(x: float) -> int:
    return 1 if x > 0 else (-1 if x < 0 else 0)


def safe(v):
    if v is None or (isinstance(v, float) and not math.isfinite(v)):
        return None
    return float(v) if isinstance(v, (np.floating, float)) else int(v) if isinstance(v, np.integer) else v


def stats(rows: pd.DataFrame) -> dict:
    if rows.empty:
        return {"n": 0, "status": "BLOCKED_DATA"}
    ae = (rows.forecast - rows.actual).abs()
    ape = ae / rows.actual.abs() * 100
    actual_dir = np.sign(rows.actual - rows.rw)
    forecast_dir = np.sign(rows.forecast - rows.rw)
    return {"n": int(len(rows)), "mae": float(ae.mean()), "mape_pct": float(ape.mean()),
            "median_ae": float(ae.median()), "median_ape_pct": float(ape.median()),
            "rmse": float(np.sqrt(np.mean(np.square(rows.forecast - rows.actual)))),
            "direction_accuracy": float(np.mean(actual_dir == forecast_dir)),
            "worst_ae": float(ae.max()), "status": "SCORED"}


def h1_data(vw_path: Path, component: dict) -> pd.DataFrame:
    base = pd.read_csv(ROOT / "patch_repro_v1/locked_replay_v7_daily_feature_pit_43.csv")
    vw = pd.read_csv(vw_path).set_index("target_month")
    base = base[base.month.isin(PILOT_MONTHS)].copy().set_index("month")
    rows = []
    cols = {"CAUSAL_PATCH": "patch_v7", "MOMENTUM_3M": "mom", "RANDOM_WALK": "rw"}
    for engine in ENGINES[:4]:
        for month in PILOT_MONTHS:
            if month == "2026-08":
                item = component["h1_2026_08"][engine]
                rows.append({"engine_id": engine, "target_month": month, "origin_month": item["origin_month"],
                             "forecast": item["forecast"], "actual": np.nan, "rw": component["h1_2026_08"]["RANDOM_WALK"]["forecast"],
                             "cell_status": "BLOCKED_DATA", "blocker_code": "REALIZED_TARGET_2026_08_NOT_FOUND"})
                continue
            if month not in base.index:
                rows.append({"engine_id": engine, "target_month": month, "cell_status": "BLOCKED_DATA", "blocker_code": "FROZEN_FORECAST_NOT_FOUND"})
                continue
            b = base.loc[month]
            forecast = float(vw.loc[month, "forecast"]) if engine == "VW_MIDAS_MSVR_SUCCESSOR_V1" else float(b[cols[engine]])
            rows.append({"engine_id": engine, "target_month": month,
                         "origin_month": str((pd.Period(month, freq="M") - 1)), "forecast": forecast,
                         "actual": float(b.actual), "rw": float(b.rw), "cell_status": "SCORED", "blocker_code": ""})
    return pd.DataFrame(rows)


def runs(values: list) -> list[int]:
    if not values: return []
    out, n = [], 1
    for a, b in zip(values, values[1:]):
        if a == b: n += 1
        else: out.append(n); n = 1
    out.append(n)
    return out


def context_metrics(ny: pd.DataFrame, gvz: pd.DataFrame) -> dict:
    ny = ny.copy(); ny["date"] = pd.to_datetime(ny.date); ny["next_return"] = ny.groupby("target_month").close.shift(-1) / ny.close - 1
    out = {}
    month = ny.groupby("target_month").agg(first_close=("monthly_reference", "first"), last_close=("close", "last"), state=("monthly_direction_3m", "first"))
    truth = np.sign(month.last_close / month.first_close - 1)
    pred = month.state.map({"UP": 1, "DOWN": -1, "NEUTRAL": 0}).fillna(0)
    out["MONTHLY_DIRECTION_3M"] = {"cells": int(len(month)), "hits": int(((truth == pred) & (pred != 0)).sum()),
        "misses": int(((truth != pred) & (pred != 0)).sum()), "neutral": int((pred == 0).sum()), "hit_rate_non_neutral": safe(((truth == pred) & (pred != 0)).sum() / max(1, (pred != 0).sum()))}
    for engine, col in (("FAST", "fast_state"), ("SLOW", "slow_state")):
        code = ny[col].map({"ROBUST_UP": 1, "ROBUST_DOWN": -1}).fillna(0)
        nxt = np.sign(ny.next_return.fillna(0))
        direct_flips = int((((code.shift(1) == 1) & (code == -1)) | ((code.shift(1) == -1) & (code == 1))).sum())
        rr = runs(code.tolist())
        out[engine] = {"observations": int(len(ny)), "state_changes": int((code != code.shift(1)).sum()-1),
                       "direct_false_flip_proxy": direct_flips, "mean_persistence_observations": safe(np.mean(rr)),
                       "next_observation_direction_agreement": safe(np.mean((code == nxt)[ny.next_return.notna()])),
                       "distinct_state_share": safe(np.mean(code != 0))}
    for engine, col in (("EMERGENCY_LEVEL", "emergency_level"), ("EMERGENCY_REVERSAL", "emergency_reversal")):
        active = ~ny[col].isin(["NEUTRAL", "OFF"])
        out[engine] = {"observations": int(len(ny)), "alert_observations": int(active.sum()),
                       "alert_months": int(ny.loc[active, "target_month"].nunique()),
                       "first_alert_by_month": ny.loc[active].groupby("target_month").date.min().dt.strftime("%Y-%m-%d").to_dict(),
                       "independent_false_miss_label": "NOT_PROVEN"}
    gvz = gvz.copy(); gvz["observation_date"] = pd.to_datetime(gvz.observation_date)
    joined = gvz.merge(ny[["date", "close"]], left_on="observation_date", right_on="date", how="left").sort_values("observation_date")
    joined["next_gold_return"] = joined.close.shift(-1) / joined.close - 1
    stressed = joined.cap.astype(float) < 1.0
    out["GVZ_RISK"] = {"observations": int(len(gvz)), "cap_below_one": int(stressed.sum()), "panic": int(gvz.panic.astype(str).str.lower().eq("true").sum()),
                       "mean_next_gold_return_stressed": safe(joined.loc[stressed, "next_gold_return"].mean()),
                       "mean_next_gold_return_unstressed": safe(joined.loc[~stressed, "next_gold_return"].mean()),
                       "cap_runs_mean": safe(np.mean(runs(gvz.cap.astype(float).tolist())))}
    return out


def contribution(h1: pd.DataFrame, contexts: dict, macro: dict, macro_reaction: dict) -> dict:
    scored = h1[h1.cell_status.eq("SCORED")].copy()
    rw = scored[scored.engine_id.eq("RANDOM_WALK")].set_index("target_month")
    rows=[]
    for engine in ENGINES[:4]:
        e=scored[scored.engine_id.eq(engine)].set_index("target_month"); j=e.join(rw[["actual","forecast"]],rsuffix="_bench")
        delta=(j.forecast_bench-j.actual).abs()-(j.forecast-j.actual).abs(); win=float((delta>0).mean())
        label="MANDATORY_BENCHMARK" if engine=="RANDOM_WALK" else ("UNIQUE_CONTRIBUTION_PROVEN" if float(delta.sum())>0 and win>0.5 else ("HARMFUL_EVIDENCE" if float(delta.sum())<0 and win<=0.5 else "INSUFFICIENT_EVIDENCE"))
        rows.append({"engine_id":engine,"classification":label,"n":len(j),"sum_ae_reduction_vs_rw":float(delta.sum()),"monthly_win_rate_vs_rw":win,
                     "residual_correlation_with_rw":safe((j.forecast-j.actual).corr(j.forecast_bench-j.actual))})
    for engine in ENGINES[4:]:
        if engine=="BOCPD_RETURN_SUCCESSOR_V1": label="INSUFFICIENT_EVIDENCE"
        elif engine=="MACRO_EVENT_SUCCESSOR_V2": label="COMPLEMENTARY" if macro.get("status","").startswith("PASS") and macro_reaction.get("status")=="PASS_EVENT_REACTION_EVIDENCE" else "INSUFFICIENT_EVIDENCE"
        elif engine in {"EMERGENCY_LEVEL","EMERGENCY_REVERSAL"}: label="INSUFFICIENT_EVIDENCE"
        else: label="COMPLEMENTARY"
        rows.append({"engine_id":engine,"classification":label,"role_metric":contexts.get(engine,{}),"cross_objective_ranking":"PROHIBITED"})
    return {"rows":rows,"weights_optimized":False,"thresholds_changed":False,"cross_role_ranking":False}


def main() -> int:
    p=argparse.ArgumentParser(); p.add_argument("--vw",required=True,type=Path); p.add_argument("--macro",required=True,type=Path); p.add_argument("--macro-reaction",required=True,type=Path); p.add_argument("--macro-rows",required=True,type=Path); p.add_argument("--bocpd",required=True,type=Path); p.add_argument("--bocpd-rows",required=True,type=Path); p.add_argument("--out",required=True,type=Path); a=p.parse_args()
    a.out.mkdir(parents=True,exist_ok=True)
    component=json.loads((AUDITS/"component_role_replays_v145/component_role_replays_v145.json").read_text())
    component_final=json.loads((AUDITS/"component_verification_v145_r3_final.json").read_text())
    macro=json.loads(a.macro.read_text()); macro_reaction=json.loads(a.macro_reaction.read_text()); macro_rows=pd.DataFrame(json.loads(a.macro_rows.read_text())); bocpd=json.loads(a.bocpd.read_text()); bocpd_rows=pd.read_csv(a.bocpd_rows)
    h1=h1_data(a.vw,component); ny=pd.read_csv(AUDITS/"component_role_replays_v145/ny17_context_role_replay_v145.csv"); gvz=pd.read_csv(AUDITS/"component_role_replays_v145/gvz_role_replay_v145.csv")
    ctx=context_metrics(ny,gvz); ctx["MACRO_EVENT_SUCCESSOR_V2"]={"status":macro.get("status"),"complete_case_months":macro.get("complete_case_months"),"state_counts":macro.get("state_counts"),"shock_events":macro.get("shock_events"),"event_reaction":macro_reaction,"contractual_exclusion":"2025-10"}
    ctx["BOCPD_RETURN_SUCCESSOR_V1"]={"status":"BLOCKED_DATA","blocker_code":"CORE5_GOLD_MONTHLY_2026_08_NOT_FOUND","partial_risk_validation":bocpd.get("validation_status")}
    cv={r["engine_id"]:r["component_verification_status"] for r in component_final["rows"]}
    role=[]
    for engine in ENGINES:
        status="BLOCKED" if cv[engine]=="BLOCKED" else ("VALIDATED_CORE" if engine in ENGINES[:4] else "VALIDATED_COMPLEMENTARY")
        if engine=="MACRO_EVENT_SUCCESSOR_V2" and (not macro.get("status","").startswith("PASS") or macro_reaction.get("status")!="PASS_EVENT_REACTION_EVIDENCE"): status="NOT_PROVEN"
        if engine in {"EMERGENCY_LEVEL","EMERGENCY_REVERSAL"}: status="NOT_PROVEN"
        role.append({"engine_id":engine,"component_status":cv[engine],"role_validation_status":status,
                     "metrics":({w:stats(h1[(h1.engine_id==engine)&h1.target_month.str.startswith(w)]) for w in ("2025","2026")} if engine in ENGINES[:4] else ctx.get(engine,{}))})
    role_doc={"contract_state":"FROZEN_BEFORE_ROLE_METRICS_AND_CONTRIBUTION_RESULTS","engine_count":12,"rows":role,"auto_selector":"OFF","auto_ensemble":"OFF","production_authority":False,"prospective_claim":False}
    contrib=contribution(h1,ctx,macro,macro_reaction)
    def window(year):
        monthly=[]; summaries=[]
        scoped_ny=ny[ny.target_month.str.startswith(year)].copy(); scoped_gvz=gvz[gvz.target_month.str.startswith(year)].copy()
        scoped_ctx=context_metrics(scoped_ny,scoped_gvz)
        ms=macro_rows[macro_rows.reference_month.astype(str).str.startswith(year)]
        scoped_ctx["MACRO_EVENT_SUCCESSOR_V2"]={"status":macro.get("status"),"event_reaction_status":macro_reaction.get("status"),"monthly_states":ms[["reference_month","state","evidence_window"]].to_dict("records"),"contractual_exclusion":"2025-10" if year=="2025" else None}
        bs=bocpd_rows[bocpd_rows.month.astype(str).str.startswith(year)]
        scoped_ctx["BOCPD_RETURN_SUCCESSOR_V1"]={"status":"BLOCKED_DATA" if year=="2026" else bocpd.get("validation_status"),"monthly_states":bs[[c for c in ("month","state","cp_probability","run_length_map") if c in bs.columns]].to_dict("records"),"blocker_code":"CORE5_GOLD_MONTHLY_2026_08_NOT_FOUND" if year=="2026" else None}
        for engine in ENGINES:
            if engine in ENGINES[:4]:
                z=h1[(h1.engine_id==engine)&h1.target_month.str.startswith(year)]; summaries.append({"engine_id":engine,"role":"H1_PRICE","status":"PARTIAL_BLOCKED_DATA" if (z.cell_status=="BLOCKED_DATA").any() else "COMPLETE","aggregate":stats(z[z.cell_status=="SCORED"]),"known_limitations":["2026-08_REALIZED_TARGET_NOT_FOUND"] if year=="2026" else []})
                monthly.extend(z.to_dict("records"))
            else: summaries.append({"engine_id":engine,"role":"CONTEXT_OR_RISK","status":next(r["role_validation_status"] for r in role if r["engine_id"]==engine),"aggregate":scoped_ctx.get(engine,{}),"known_limitations":(["2026-08_BLOCKED_DATA"] if engine=="BOCPD_RETURN_SUCCESSOR_V1" and year=="2026" else [])})
        return {"window":"2025-01..2025-12" if year=="2025" else "2026-01..2026-08","evidence_class":"RETROSPECTIVE_VALIDATION_WINDOW" if year=="2025" else "RETROSPECTIVE_FROZEN_OOS_TEST","monthly_evidence":monthly,"rows":summaries,"no_tuning_confirmation":True}
    reports={"2025":window("2025"),"2026":window("2026")}
    cby={r["engine_id"]:r["classification"] for r in contrib["rows"]}; architecture=[]
    for r in role:
        if r["component_status"]=="BLOCKED": dec="BLOCKED_DATA"
        elif r["role_validation_status"]=="NOT_PROVEN": dec="NOT_PROVEN"
        elif r["engine_id"] in ENGINES[:4]: dec="VALIDATED_CORE"
        else: dec="VALIDATED_COMPLEMENTARY"
        architecture.append({"engine_id":r["engine_id"],"decision":dec,"technical":r["component_status"],"role":r["role_validation_status"],"contribution":cby[r["engine_id"]],"single_metric_removal":False})
    arch={"rows":architecture,"auto_selector":"OFF","auto_ensemble":"OFF","weight_optimization":"NONE","production_authority":False}
    shadow={"status":"BLOCKED_DATA","prospective_shadow_ready":False,"blockers":["BOCPD_2026_08_EXACT_CORE5_GOLD_MONTHLY_NOT_FOUND","PROSPECTIVE_SOURCE_AVAILABILITY_NOT_PROVEN_FOR_ALL_12"],"lane":"OBSERVATION_AND_EVALUATION_ONLY","historical_reconstruction_is_prospective":False,"trade_authority":False,"auto_selector":"OFF","auto_ensemble":"OFF","requirements":{"immutable_origin_timestamps":True,"lineage":True,"no_hindsight":True,"fail_closed":True,"drift_detection":True,"monitoring":True}}
    objects={"role_specific_validation_v145.json":role_doc,"incremental_contribution_v145.json":contrib,"retrospective_validation_2025_v145.json":reports["2025"],"frozen_oos_2026_jan_aug_v145.json":reports["2026"],"architecture_review_v145.json":arch,"prospective_shadow_readiness_v145.json":shadow}
    for name,obj in objects.items(): (a.out/name).write_text(json.dumps(obj,indent=2,sort_keys=True,default=safe)+"\n")
    h1.to_csv(a.out/"pilot_h1_monthly_evidence_v145.csv",index=False)
    pd.DataFrame([{"engine_id":r["engine_id"],"component_status":r["component_status"],"role_validation_status":r["role_validation_status"]} for r in role]).to_csv(a.out/"role_specific_validation_v145.csv",index=False)
    pd.DataFrame([{k:v for k,v in r.items() if k!="role_metric"} for r in contrib["rows"]]).to_csv(a.out/"incremental_contribution_v145.csv",index=False)
    for year,name in (("2025","retrospective_validation_2025_v145.csv"),("2026","frozen_oos_2026_jan_aug_v145.csv")):
        pd.DataFrame([{"engine_id":r["engine_id"],"role":r["role"],"status":r["status"],"n":r["aggregate"].get("n"),"mae":r["aggregate"].get("mae"),"mape_pct":r["aggregate"].get("mape_pct"),"direction_accuracy":r["aggregate"].get("direction_accuracy")} for r in reports[year]["rows"]]).to_csv(a.out/name,index=False)
    pd.DataFrame(architecture).to_csv(a.out/"architecture_review_v145.csv",index=False)
    for name,obj in objects.items():
        md="# "+name.replace("_"," ").replace(".json","")+"\n\n```json\n"+json.dumps(obj,indent=2,sort_keys=True,default=safe)+"\n```\n"; (a.out/name.replace(".json",".md")).write_text(md)
    manifest={"inputs":{"vw_sha256":sha(a.vw),"macro_sha256":sha(a.macro),"macro_reaction_sha256":sha(a.macro_reaction),"macro_rows_sha256":sha(a.macro_rows),"bocpd_sha256":sha(a.bocpd),"bocpd_rows_sha256":sha(a.bocpd_rows)},"outputs":{p.name:sha(p) for p in a.out.iterdir() if p.is_file()},"engine_count":12,"pilot_months":20,"production_writes":"NONE","authority_created":False}
    (a.out/"pilot_validation_run_manifest_v145.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"engine_count":12,"role_statuses":pd.Series([r["role_validation_status"] for r in role]).value_counts().to_dict(),"shadow":shadow["status"]},sort_keys=True))
    return 0

if __name__=="__main__": raise SystemExit(main())
