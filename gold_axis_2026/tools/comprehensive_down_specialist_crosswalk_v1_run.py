from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd
import psycopg

IDENTITY = "COMPREHENSIVE_DOWN_SPECIALIST_CROSSWALK_V1R2_RESEARCH"
Z90 = 1.2815515655446004

CROSSDOMAIN = {
    "CROSSDOMAIN_STATIC_LOGIT_DOWN": "static_p_down",
    "CROSSDOMAIN_DYNAMIC_LOGIT_D99_DOWN": "dynamic_p_down",
    "CROSSDOMAIN_COMPETING_RISK_DOWN": "competing_p_down",
    "CROSSDOMAIN_EXPLICIT_DURATION_DOWN": "semimarkov_p_down",
}

EXPECTED_CBR_2024 = {
    "STRICT_P050": (7, 3, 4),
    "STRICT_RECALL75": (12, 5, 7),
    "CONTEXT_P050": (8, 3, 5),
    "CONTEXT_RECALL75": (17, 7, 10),
}
EXPECTED_SP500_2024 = {
    "Q10_RULE": (16, 6, 10),
    "LOGIT_P050": (9, 4, 5),
    "LOGIT_RECALL75": (13, 5, 8),
}
EXPECTED_CONS_2024 = (13, 6, 7)


def load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_SPEC_FAIL:{name}:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def wilson_lcb(k: int, n: int, z: float = Z90):
    if n <= 0:
        return None
    p = k / n
    den = 1 + z*z/n
    center = p + z*z/(2*n)
    rad = z * math.sqrt((p*(1-p) + z*z/(4*n))/n)
    return (center-rad)/den


def read_subset(path: Path) -> list[dict]:
    out=[]
    with path.open(newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append({
                "evaluation_year": int(r["evaluation_year"]),
                "origin_date": r["origin_date"],
                "target_date": r["target_date"],
                "actual_up": int(r["actual_up"]),
                "actual_high_risk": int(r["actual_high_risk"]),
                "sqrt_score": float(r["sqrt_score"]),
                "router_up": int(r["router_up"]),
            })
    return out


def metrics(subset: list[dict], predmap: dict[str, dict]) -> dict:
    vals=[]
    for r in subset:
        p=predmap.get(r["target_date"])
        if p is None:
            continue
        vals.append((r,p))
    n=len(vals)
    actual_down=sum(r["actual_up"]==0 for r,p in vals)
    actual_up=sum(r["actual_up"]==1 for r,p in vals)
    calls=[(r,p) for r,p in vals if int(p["down"])==1]
    dc=len(calls)
    correct=sum(r["actual_up"]==0 for r,p in calls)
    false=sum(r["actual_up"]==1 for r,p in calls)
    precision=correct/dc if dc else None
    recall=correct/actual_down if actual_down else None
    fpr=false/actual_up if actual_up else None
    return {
        "available_n": n,
        "subset_n": len(subset),
        "actual_down": actual_down,
        "actual_up": actual_up,
        "down_calls": dc,
        "correct_down": correct,
        "false_down": false,
        "down_precision": precision,
        "down_recall": recall,
        "false_down_fpr": fpr,
        "down_call_coverage": dc/n if n else None,
        "wilson90_lcb_down_precision": wilson_lcb(correct,dc),
    }


def screen_positive(m: dict) -> bool:
    return bool(
        m["available_n"] >= 10
        and m["down_calls"] >= 5
        and m["down_precision"] is not None
        and m["down_precision"] > 0.50
        and m["false_down_fpr"] is not None
        and m["false_down_fpr"] < 0.50
    )


def yearly_metrics(subset, predmap):
    return {
        str(y): metrics([r for r in subset if r["evaluation_year"]==y], predmap)
        for y in sorted({r["evaluation_year"] for r in subset})
    }


def reconstruct_2025(base, sqrt_parent: Path):
    days=base.load_days()
    tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    bmaps=base.bonato_maps(bdays)
    lmaps=base.logit_maps(ldays)
    contexts=base.legacy_context(daily)
    router=base.build_router_rows(trows,bmaps,lmaps,contexts)
    rmap={(r["origin_date"],r["target_date"]):r for r in router}
    sqrt=base.load_sqrt(sqrt_parent)
    aligned=[]
    for s in sqrt:
        if s["evaluation_year"] != 2025:
            continue
        rr=rmap.get((s["origin_date"],s["target_date"]))
        if rr is None:
            raise RuntimeError(f"ROUTER_2025_ROW_NOT_FOUND:{s['target_date']}")
        if int(rr["actual_up"]) != int(s["actual_up"]):
            raise RuntimeError(f"ROUTER_2025_SIGN_MISMATCH:{s['target_date']}")
        z=dict(s)
        z["router_up"]=int(rr["router_up"])
        z["router_selected_expert"]=rr["selected_expert"]
        aligned.append(z)
    return [r for r in aligned if r["router_up"]==0], router


def v153_maps(v153, contract_path: Path, primary: list[dict], stress25: list[dict]):
    contract=json.loads(contract_path.read_text(encoding="utf-8"))
    if contract["status"] != "FROZEN_BEFORE_V153_2025_2026_SUCCESSOR_SCORING":
        raise RuntimeError("V153_CONTRACT_NOT_FROZEN")
    with psycopg.connect(os.environ["NEON_DATABASE_URL"], autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
        daily=v153.load_daily_intraday_state(conn, contract["windows"]["source_start"], contract["windows"]["validation_end"])
    daily=v153.add_semivariance_state(daily,contract)
    exact=v153.exact_origin_frame(daily,contract).copy()
    exact["target_trade_date"]=exact["trade_date"].shift(-1)
    exact["target_date"]=pd.to_datetime(exact["target_trade_date"]).dt.strftime("%Y-%m-%d")

    maps={k:{} for k in [
        "V153_RSV_TTSM_S2_DOWN",
        "V153_EUROPE_CONT_DOWN",
        "V153_RAW_MOM20_DOWN",
    ]}
    diag={}
    for _,r in exact.iterrows():
        td=r.get("target_date")
        if not isinstance(td,str) or td=="NaT":
            continue
        if pd.isna(r.get("target_sign")):
            continue
        maps["V153_RSV_TTSM_S2_DOWN"][td]={"down":int(int(r["sig_ttsm_s2"])==-1),"score":float(r["sig_ttsm_s2"])}
        maps["V153_EUROPE_CONT_DOWN"][td]={"down":int(int(r["sig_europe"])==-1),"score":float(r["sig_europe"])}
        raw_sig=int(np.sign(r["mom20"])) if pd.notna(r["mom20"]) and float(r["mom20"])!=0 else 0
        maps["V153_RAW_MOM20_DOWN"][td]={"down":int(raw_sig==-1),"score":float(raw_sig)}
        diag[td]={"up":int(int(r["sig_downshock"])==1),"score":float(r["sig_downshock"])}

    # Exact sign crosswalk on rows the V1.53 source can represent.
    all_subset=primary+stress25
    emap={str(r["target_date"]):r for _,r in exact.iterrows() if isinstance(r.get("target_date"),str)}
    mism=[]
    for s in all_subset:
        er=emap.get(s["target_date"])
        if er is None or pd.isna(er.get("target_sign")):
            continue
        up=int(float(er["target_sign"])>0)
        if up != int(s["actual_up"]):
            mism.append(s["target_date"])
    return maps,diag,mism


def load_crossdomain(path: Path, subsets: list[dict]):
    need={r["target_date"]:r for r in subsets}
    maps={k:{} for k in CROSSDOMAIN}
    sign_mismatch=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            td=r["target_date"]
            if td not in need:
                continue
            target_down=int(r["target_down"])
            if target_down != int(need[td]["actual_up"]==0):
                sign_mismatch.append(td)
            for name,col in CROSSDOMAIN.items():
                p=float(r[col])
                maps[name][td]={"down":int(p>=0.5),"score":p}
    return maps,sign_mismatch


def cbr_predictions(cbr, sqrt_parent: Path, subsets_by_year: dict[int,list[dict]]):
    cbr.PARENT=sqrt_parent
    parent=cbr.load_parent()
    raw=cbr.load_paths([r["origin_date"] for r in parent])
    rows=cbr.enrich(parent,raw)
    bykey={(r["origin_date"],r["target_date"]):r for r in rows}

    full24=cbr.year_eval(rows,2024)
    integrity=[]
    for name,expected in EXPECTED_CBR_2024.items():
        m=full24["variants"][name]
        obs=(m.get("confirm_count"),m.get("tp"),m.get("fp"))
        if obs!=expected:
            integrity.append(f"CBR_FULL2024_{name}:{obs}!={expected}")

    maps={f"CBR_{name}_DOWN":{} for name in EXPECTED_CBR_2024}
    for year,subset in subsets_by_year.items():
        if year not in (2024,2025):
            continue
        cutoff=date(year-1,12,31)
        hist=[r for r in rows if date.fromisoformat(r["target_date"])<=cutoff]
        pools={
            "STRICT":[r for r in hist if int(r["sqrt_high_risk_alert"])==1],
            "CONTEXT":[r for r in hist if float(r["sqrt_normalized_risk_score"])>=0.80],
        }
        tests=[]
        for s in subset:
            rr=bykey.get((s["origin_date"],s["target_date"]))
            if rr is not None:
                tests.append(rr)
        for pname,pool in pools.items():
            probs={}
            for t in tests:
                p,d=cbr.case_prob(pool,t)
                probs[t["target_date"]]=p
            for mode in ("P050","RECALL75"):
                if mode=="P050":
                    thr=0.5
                else:
                    thr,sel=cbr.select_recall75(pool)
                    if thr is None:
                        continue
                name=f"CBR_{pname}_{mode}_DOWN"
                for t in tests:
                    p=probs[t["target_date"]]
                    maps[name][t["target_date"]]={"down":int(p>=thr),"score":float(p),"threshold":float(thr)}
    return maps,integrity,rows


def sp_predictions(spv, sqrt_parent: Path, subsets_by_year: dict[int,list[dict]]):
    spv.PARENT=sqrt_parent
    parent=spv.load_parent()
    sp=spv.load_sp500()
    rows,stale=spv.align(parent,sp)
    bykey={(r["origin_date"],r["target_date"]):r for r in rows}

    full24=spv.year_eval(rows,2024)
    integrity=[]
    for name,expected in EXPECTED_SP500_2024.items():
        m=full24[name]
        obs=(m.get("confirm_count"),m.get("tp"),m.get("fp"))
        if obs!=expected:
            integrity.append(f"SP500_FULL2024_{name}:{obs}!={expected}")

    maps={k:{} for k in [
        "SP500_Q10_CONFIRM_DOWN","SP500_LOGIT_P050_DOWN","SP500_LOGIT_RECALL75_DOWN"
    ]}
    probs_cache={}
    for year,subset in subsets_by_year.items():
        if year not in (2024,2025):
            continue
        cutoff=date(year-1,12,31)
        hist=[r for r in rows if date.fromisoformat(r["target_date"])<=cutoff]
        train=[r for r in hist if float(r["sqrt_normalized_risk_score"])>=0.80]
        q10=spv.nearest_rank(np.asarray([r["sp_ret1"] for r in hist]),.10)
        fit=spv.fit_logit(train)
        tests=[bykey[(s["origin_date"],s["target_date"])] for s in subset if (s["origin_date"],s["target_date"]) in bykey]
        p=spv.probs(fit,tests) if tests else np.array([])
        thr75,sel=spv.select_recall75(train)
        for i,t in enumerate(tests):
            td=t["target_date"]
            maps["SP500_Q10_CONFIRM_DOWN"][td]={"down":int(not (float(t["sp_ret1"])<=q10)),"score":float(t["sp_ret1"]),"threshold":q10}
            maps["SP500_LOGIT_P050_DOWN"][td]={"down":int(float(p[i])>=0.5),"score":float(p[i]),"threshold":0.5}
            if thr75 is not None:
                maps["SP500_LOGIT_RECALL75_DOWN"][td]={"down":int(float(p[i])>=thr75),"score":float(p[i]),"threshold":float(thr75)}
        probs_cache[year]={"rows":tests,"p":p,"train":train}
    return maps,integrity,rows,probs_cache


def consensus_predictions(cbr, spv, cbr_rows, sp_rows, subsets_by_year):
    smap={(r["origin_date"],r["target_date"]):r for r in sp_rows}
    merged=[]
    for r in cbr_rows:
        s=smap.get((r["origin_date"],r["target_date"]))
        if s is None:
            continue
        z=dict(r)
        for k in ("sp_date","sp_age_days","sp_ret1","sp_ret5","sp_vol20","sp_z1","gold_risk_margin"):
            z[k]=s[k]
        merged.append(z)
    bykey={(r["origin_date"],r["target_date"]):r for r in merged}
    maps={"HETERO_CONSENSUS_DOWN":{}}
    integrity=[]

    def year_preds(year, subset):
        cutoff=date(year-1,12,31)
        hist=[r for r in merged if date.fromisoformat(r["target_date"])<=cutoff]
        path_train=[r for r in hist if int(r["sqrt_high_risk_alert"])==1]
        sp_train=[r for r in hist if float(r["sqrt_normalized_risk_score"])>=0.80]
        spfit=spv.fit_logit(sp_train)
        tests=[bykey[(s["origin_date"],s["target_date"])] for s in subset if (s["origin_date"],s["target_date"]) in bykey]
        psp=spv.probs(spfit,tests) if tests else np.array([])
        for i,t in enumerate(tests):
            pp,d=cbr.case_prob(path_train,t)
            pc=max(float(pp),float(psp[i]))
            maps["HETERO_CONSENSUS_DOWN"][t["target_date"]]={"down":int(pc>=0.5),"score":pc,"path_p":float(pp),"sp_p":float(psp[i])}

    for y,subset in subsets_by_year.items():
        if y in (2024,2025):
            year_preds(y,subset)

    # Reproduce original full-2024 aggregate exactly.
    test24=[r for r in merged if int(r["evaluation_year"])==2024 and int(r["sqrt_high_risk_alert"])==1]
    cutoff=date(2023,12,31)
    hist=[r for r in merged if date.fromisoformat(r["target_date"])<=cutoff]
    path_train=[r for r in hist if int(r["sqrt_high_risk_alert"])==1]
    sp_train=[r for r in hist if float(r["sqrt_normalized_risk_score"])>=0.80]
    spfit=spv.fit_logit(sp_train)
    psp=spv.probs(spfit,test24)
    pred=[]; y=[]
    for i,t in enumerate(test24):
        pp,d=cbr.case_prob(path_train,t)
        pred.append(max(float(pp),float(psp[i]))>=.5)
        y.append(int(t["meta_y"]))
    tp=sum(p and yy==1 for p,yy in zip(pred,y))
    fp=sum(p and yy==0 for p,yy in zip(pred,y))
    obs=(sum(pred),tp,fp)
    if obs!=EXPECTED_CONS_2024:
        integrity.append(f"CONS_FULL2024:{obs}!={EXPECTED_CONS_2024}")
    return maps,integrity


def up_diag_metrics(subset, diagmap):
    vals=[]
    for r in subset:
        p=diagmap.get(r["target_date"])
        if p is not None:
            vals.append((r,p))
    calls=[(r,p) for r,p in vals if int(p["up"])==1]
    return {
        "available_n":len(vals),
        "up_calls":len(calls),
        "correct_up":sum(r["actual_up"]==1 for r,p in calls),
        "false_up":sum(r["actual_up"]==0 for r,p in calls),
        "up_precision":(
            sum(r["actual_up"]==1 for r,p in calls)/len(calls)
            if calls else None
        ),
    }


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-module",type=Path,required=True)
    ap.add_argument("--sqrt-parent",type=Path,required=True)
    ap.add_argument("--pre-ledger",type=Path,required=True)
    ap.add_argument("--crossdomain",type=Path,required=True)
    ap.add_argument("--v153-module",type=Path,required=True)
    ap.add_argument("--v153-contract",type=Path,required=True)
    ap.add_argument("--cbr-module",type=Path,required=True)
    ap.add_argument("--sp500-module",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)

    integrity=[]
    primary=read_subset(args.pre_ledger)
    if len(primary)!=26 or sum(r["actual_up"]==0 for r in primary)!=13 or sum(r["actual_up"]==1 for r in primary)!=13:
        integrity.append("PRIMARY_SUBSET_MISMATCH")

    base=load_mod("down_base",args.base_module)
    stress25,router= reconstruct_2025(base,args.sqrt_parent)
    if len(stress25)!=74 or sum(r["actual_up"]==0 for r in stress25)!=39 or sum(r["actual_up"]==1 for r in stress25)!=35:
        integrity.append(f"LOCKED2025_SUBSET_MISMATCH:{len(stress25)}/{sum(r['actual_up']==0 for r in stress25)}/{sum(r['actual_up']==1 for r in stress25)}")

    # Router exact integrity.
    for y,exp in {2022:(22,None,None),2023:(19,None,None),2024:(42,26,16),2025:(37,27,10)}.items():
        rr=[r for r in router if int(r["target_date"][:4])==y and r["router_up"]==1]
        tp=sum(r["actual_up"]==1 for r in rr);fp=sum(r["actual_up"]==0 for r in rr)
        if len(rr)!=exp[0] or (exp[1] is not None and (tp,fp)!=(exp[1],exp[2])):
            integrity.append(f"ROUTER_{y}_MISMATCH:{len(rr)}/{tp}/{fp}")
    r25=[r for r in router if r["target_date"].startswith("2025-") and r["router_up"]==1]
    if sum(r["selected_expert"]=="RM_LOGIT" for r in r25)!=37:
        integrity.append("ROUTER_2025_RM_COUNT_MISMATCH")

    # V1.53 was removed from R2 candidate scoring after the V1 integrity
    # gate proved that its exact-NY17 target clock does not map one-to-one
    # to the SQRT parent target-day sign by a simple target_date join.
    # No V1.53 output is used below.
    v153_clock_audit = {
        "status": "NOT_PROVEN_TARGET_CLOCK_ALIGNMENT",
        "v1_first_mismatches": [
            "2024-04-16", "2025-05-01", "2025-05-02", "2025-05-07", "2025-05-13"
        ],
        "candidate_scoring_authority": False
    }

    # Cross-domain retained exact rows.
    xdm,xd_mismatch=load_crossdomain(args.crossdomain,primary+stress25)
    if xd_mismatch:
        integrity.append(f"CROSSDOMAIN_TARGET_SIGN_MISMATCH:{xd_mismatch[:5]}")

    # CBR / SP500 / consensus exact reproductions.
    cbr=load_mod("downside_cbr_dtw_path_v1",args.cbr_module)
    spv=load_mod("downside_sp500_crossmarket_veto_v1",args.sp500_module)
    subsets_by_year={
        2022:[r for r in primary if r["evaluation_year"]==2022],
        2023:[r for r in primary if r["evaluation_year"]==2023],
        2024:[r for r in primary if r["evaluation_year"]==2024],
        2025:stress25,
    }
    cbrm,cbr_integrity,cbr_rows=cbr_predictions(cbr,args.sqrt_parent,subsets_by_year)
    integrity.extend(cbr_integrity)
    spm,sp_integrity,sp_rows,spcache=sp_predictions(spv,args.sqrt_parent,subsets_by_year)
    integrity.extend(sp_integrity)
    conm,cons_integrity=consensus_predictions(cbr,spv,cbr_rows,sp_rows,subsets_by_year)
    integrity.extend(cons_integrity)

    predmaps={}
    predmaps.update(xdm);predmaps.update(cbrm);predmaps.update(spm);predmaps.update(conm)

    primary_results={}
    positive=[]
    for name,pmap in predmaps.items():
        m=metrics(primary,pmap)
        yr=yearly_metrics(primary,pmap)
        pos=screen_positive(m)
        primary_results[name]={
            **m,
            "screen_positive_pre2025":pos,
            "by_year":yr,
        }
        if pos:
            positive.append(name)

    transport={}
    baseline25=39/74
    for name in positive:
        m=metrics(stress25,predmaps[name])
        supportive=bool(
            m["down_calls"]>=5
            and m["down_precision"] is not None
            and m["down_precision"]>baseline25
            and m["false_down_fpr"] is not None
            and m["false_down_fpr"]<0.50
        )
        transport[name]={
            **m,
            "baseline_down_prevalence":baseline25,
            "precision_lift_vs_baseline":(
                m["down_precision"]-baseline25 if m["down_precision"] is not None else None
            ),
            "transport_supportive":supportive,
        }

    diag={
        "V153_CLOCK_ALIGNMENT": v153_clock_audit
    }

    if integrity:
        status="BLOCKED_INTEGRITY_MISMATCH"
    elif not positive:
        status="NO_RETAINED_SPECIALIST_SCREEN_POSITIVE"
    elif any(v["transport_supportive"] for v in transport.values()):
        status="PRE2025_SPECIALIST_SIGNAL_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT"
    else:
        status="PRE2025_SPECIALIST_SIGNAL_BUT_LOCKED2025_TRANSPORT_WEAK"

    result={
        "identity":IDENTITY,
        "date":"2026-09-23",
        "status":status,
        "integrity_errors":integrity,
        "primary_subset":{"n":len(primary),"actual_down":13,"actual_up":13},
        "locked_2025_subset":{"n":len(stress25),"actual_down":39,"actual_up":35,"down_prevalence":baseline25},
        "screen_rule":{
            "available_n_min":10,
            "down_calls_min":5,
            "down_precision_gt":0.50,
            "false_down_fpr_lt":0.50,
        },
        "primary_candidate_results":primary_results,
        "screen_positive_candidates":positive,
        "locked_2025_transport":transport,
        "up_only_diagnostics":diag,
        "authority_exclusions":[
            "Market Shock / Macro Event: event/minute clock mismatch",
            "V1.53 family: NOT_PROVEN target-clock alignment with SQRT parent under simple date join; removed from R2 scoring",
            "weekly/H5/H10/H20/3D: horizon mismatch",
            "MONTHLY_DIRECTION_3M and MOMENTUM_3M: slow-clock priors",
            "Altuntas AlexNet: target clock unresolved",
            "V1.63: 2024 is training history under identity",
            "V1.69/later 1D: not imported without pre-scoring exact retained row artifact proof",
            "V1.48/V1.51/V1.55/V1.57/V1.58: exact row-level retained evidence NOT_FOUND in canonical consolidation"
        ],
        "governance":{
            "random_split":False,
            "threshold_tuning":False,
            "2025_used_for_selection":False,
            "2026_used":False,
            "production_writes":False,
            "runtime_promotion":False,
        }
    }
    (args.out/"GOLD_CONTROL_COMPREHENSIVE_DOWN_SPECIALIST_CROSSWALK_V1R2_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")

    # Long-form row ledger, only exact subset rows and frozen candidate calls.
    fields=["evaluation_year","origin_date","target_date","actual_up","actual_high_risk","sqrt_score"]
    for name in predmaps:
        fields += [f"{name}_available",f"{name}_down",f"{name}_score"]
    with (args.out/"GOLD_CONTROL_COMPREHENSIVE_DOWN_SPECIALIST_CROSSWALK_V1R2_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in primary:
            z={k:r.get(k,"") for k in fields[:6]}
            for name,pmap in predmaps.items():
                p=pmap.get(r["target_date"])
                z[f"{name}_available"]=int(p is not None)
                z[f"{name}_down"]="" if p is None else int(p["down"])
                z[f"{name}_score"]="" if p is None else p.get("score","")
            w.writerow(z)

    lines=[
        "# GOLD CONTROL — COMPREHENSIVE RETAINED DOWN-SPECIALIST CROSSWALK V1 RESULT","",
        f"**Status:** `{status}`  ",
        f"**Integrity errors:** {integrity if integrity else 'none'}","",
        "Primary unresolved subset: 26 = 13 DOWN + 13 UP.","",
        "| Candidate | n | DOWN calls | correct | false | precision | recall | false-DOWN FPR | screen+ |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---|"
    ]
    for name,m in primary_results.items():
        lines.append(
            f"| {name} | {m['available_n']} | {m['down_calls']} | {m['correct_down']} | {m['false_down']} | "
            f"{m['down_precision']} | {m['down_recall']} | {m['false_down_fpr']} | {m['screen_positive_pre2025']} |"
        )
    lines += ["",f"**Screen-positive pre-2025:** {positive or 'NONE'}",""]
    if transport:
        lines += ["## Locked 2025 transport",""]
        for name,m in transport.items():
            lines.append(
                f"- {name}: n={m['available_n']}, DOWN calls={m['down_calls']}, "
                f"precision={m['down_precision']}, recall={m['down_recall']}, FPR={m['false_down_fpr']}, "
                f"supportive={m['transport_supportive']}."
            )
    lines += ["","No threshold was changed; 2025 did not select or redesign candidates; 2026 was not used."]
    (args.out/"GOLD_CONTROL_COMPREHENSIVE_DOWN_SPECIALIST_CROSSWALK_V1R2_RESULT_2026-09-23.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

    print(json.dumps({
        "status":status,
        "integrity_errors":integrity,
        "screen_positive_candidates":positive,
        "primary_candidate_results":primary_results,
        "locked_2025_transport":transport,
        "up_only_diagnostics":diag,
    },indent=2))
    return 0 if not integrity else 2


if __name__=="__main__":
    raise SystemExit(main())
