from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import sys
import types
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

IDENTITY = "CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESEARCH"
MIRROR_COMMIT = "922f83a60cc574e7395fb27397077288055a1ef6"
EXTERNAL_SPINE_COMMIT = "509c5ffa762f4ea49644b8ffe723ed2591ba52bf"
SQRT_CODE_COMMIT = "ad0fc4dcbe1687833bd9a153cd4bc6a754523464"
CBR_CODE_COMMIT = "f187f89c166a75cefa8cf60709dcd4ce1027663d"
BASE_AUDIT_COMMIT = "7982b422476df61eb0339b74265afd553414f2d2"
Z90 = 1.2815515655446004


@dataclass(frozen=True)
class DailyLike:
    d: date
    close: float
    dr: float


def load_mod(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_SPEC_FAIL:{name}:{path}")
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_sqrt_mod(path: Path):
    # The pinned SQRT module imports Daily only for typing. Inject a minimal
    # compatibility module so the exact pinned function can be executed
    # without importing unrelated direction engines.
    dummy = types.ModuleType("regime_v1_data")
    dummy.Daily = DailyLike
    old = sys.modules.get("regime_v1_data")
    sys.modules["regime_v1_data"] = dummy
    try:
        return load_mod("pinned_regime_v1_router_sqrt", path)
    finally:
        if old is None:
            sys.modules.pop("regime_v1_data", None)
        else:
            sys.modules["regime_v1_data"] = old


def wilson_lcb(k: int, n: int):
    if n <= 0:
        return None
    p = k / n
    z = Z90
    den = 1.0 + z*z/n
    center = p + z*z/(2*n)
    rad = z * math.sqrt((p*(1-p) + z*z/(4*n))/n)
    return (center-rad)/den


def build_external_5m(raw_root: Path) -> dict[str, dict]:
    ask_dir = raw_root / "xauusd" / "ask" / "m1"
    bid_dir = raw_root / "xauusd" / "bid" / "m1"
    ask_files = sorted(list(ask_dir.glob("xauusd_ask_m1_2020_*.csv")) +
                       list(ask_dir.glob("xauusd_ask_m1_2021_*.csv")) +
                       list(ask_dir.glob("xauusd_ask_m1_2022_01.csv")))
    bid_files = sorted(list(bid_dir.glob("xauusd_bid_m1_2020_*.csv")) +
                       list(bid_dir.glob("xauusd_bid_m1_2021_*.csv")) +
                       list(bid_dir.glob("xauusd_bid_m1_2022_01.csv")))
    if len(ask_files) != 25 or len(bid_files) != 25:
        raise RuntimeError(f"RAW_FILE_COUNT:{len(ask_files)}/{len(bid_files)}!=25/25")

    def read_side(files, side):
        frames=[]
        for p in files:
            z=pd.read_csv(p,usecols=["timestamp","close"])
            z["timestamp"]=pd.to_numeric(z["timestamp"],errors="raise").astype("int64")
            z["close"]=pd.to_numeric(z["close"],errors="raise").astype(float)
            z=z.rename(columns={"close":f"close_{side}"})
            frames.append(z)
        out=pd.concat(frames,ignore_index=True)
        out=out.drop_duplicates("timestamp",keep="last").sort_values("timestamp")
        return out

    ask=read_side(ask_files,"ask")
    bid=read_side(bid_files,"bid")
    m=bid.merge(ask,on="timestamp",how="inner",validate="one_to_one")
    if len(m) < 900_000:
        raise RuntimeError(f"RAW_JOIN_TOO_SHORT:{len(m)}")
    m["mid"]=(m["close_bid"]+m["close_ask"])/2.0
    m["dt_utc"]=pd.to_datetime(m["timestamp"],unit="ms",utc=True)
    m["bin_utc"]=m["dt_utc"].dt.floor("5min")
    bars=(m.sort_values("timestamp")
            .groupby("bin_utc",as_index=False)
            .agg(mid=("mid","last")))
    bars["dt_ny"]=bars["bin_utc"].dt.tz_convert("America/New_York")
    bars=bars[(bars["dt_ny"].dt.weekday < 5) & (bars["dt_ny"].dt.hour != 17)].copy()
    bars["date"]=bars["dt_ny"].dt.strftime("%Y-%m-%d")
    bars=bars.sort_values(["date","bin_utc"])

    out={}
    for d,g in bars.groupby("date",sort=True):
        if not (d.startswith("2020-") or d.startswith("2021-")):
            continue
        close=g["mid"].to_numpy(float)
        n=len(close)
        if n < 240:
            continue
        rets=np.diff(np.log(close))
        rv=float(np.sum(rets*rets))
        if not math.isfinite(rv) or rv <= 0:
            continue
        dr=float(np.sum(np.where(rets<=0,rets*rets,0.0)))
        r3=float(np.sum(rets**3))
        rp=float(np.sum(np.where(rets>0,rets*rets,0.0)))
        rm=float(np.sum(np.where(rets<0,rets*rets,0.0)))
        out[d]={
            "n_bars":n,
            "close":float(close[-1]),
            "rv":rv,
            "dr":dr,
            "r3":r3,
            "rs_plus":rp,
            "rs_minus":rm,
            "rets":rets,
        }
    return out


def load_external_spine(path: Path) -> list[dict]:
    rows=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "date":r["date"],
                "n_bars":int(r["n_bars"]),
                "close":float(r["close_mid"]),
                "rv":float(r["rv_5m"]),
                "dr":float(r["dr_5m"]),
                "r3":float(r["r3_5m"]),
                "rs_plus":float(r["rs_plus_5m"]),
                "rs_minus":float(r["rs_minus_5m"]),
            })
    return rows


def external_reconstruction_audit(raw: dict[str,dict], spine: list[dict]) -> dict:
    ref={r["date"]:r for r in spine if r["date"].startswith(("2020-","2021-"))}
    dates_raw=set(raw)
    dates_ref=set(ref)
    missing=sorted(dates_ref-dates_raw)
    extra=sorted(dates_raw-dates_ref)
    common=sorted(dates_raw & dates_ref)
    max_close=max((abs(raw[d]["close"]-ref[d]["close"]) for d in common),default=float("inf"))
    max_rv=max((abs(raw[d]["rv"]-ref[d]["rv"]) for d in common),default=float("inf"))
    max_dr=max((abs(raw[d]["dr"]-ref[d]["dr"]) for d in common),default=float("inf"))
    bad_bars=[d for d in common if raw[d]["n_bars"]!=276 or ref[d]["n_bars"]!=276]
    passed=(not missing and not extra and not bad_bars and
            max_close<=1e-8 and max_rv<=1e-12 and max_dr<=1e-12)
    return {
        "passed":passed,
        "raw_n":len(raw),"spine_n":len(ref),"common_n":len(common),
        "missing_dates":missing[:20],"extra_dates":extra[:20],
        "bad_276_bar_dates":bad_bars[:20],
        "max_abs_close_diff":max_close,
        "max_abs_rv_diff":max_rv,
        "max_abs_dr_diff":max_dr,
    }


def load_external_daily_for_sqrt(spine: list[dict]) -> list[DailyLike]:
    return [DailyLike(date.fromisoformat(r["date"]),r["close"],r["dr"]) for r in spine]


def external_sqrt_cases(sqrt_mod, daily: list[DailyLike]) -> tuple[list[dict],dict]:
    rows=[]
    summary={}
    for year in (2020,2021):
        yr=sqrt_mod.sqrt_rows(daily,year)
        alarms=[r for r in yr if int(r["sqrt_alarm"])==1]
        down=sum(float(r["target_return"])<0 for r in alarms)
        up=sum(float(r["target_return"])>0 for r in alarms)
        summary[str(year)]={"alarms":len(alarms),"down":down,"up":up}
        for r in alarms:
            z=dict(r)
            z["evaluation_year"]=year
            z["meta_y"]=int(float(r["target_return"])<0)
            z["source"]="EXTERNAL_DUKASCOPY_V2"
            rows.append(z)
    return rows,summary


def load_frozen_parent(path: Path) -> list[dict]:
    out=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            y=int(r["evaluation_year"])
            if y not in (2022,2023,2024,2025):
                continue
            if int(r["sqrt_high_risk_alert"])!=1:
                continue
            ret=float(r["target_close_return"])
            out.append({
                "evaluation_year":y,
                "origin_date":r["origin_date"],
                "target_date":r["target_date"],
                "meta_y":int(ret<0),
                "actual_up":int(ret>0),
                "source":"GOVERNED_FROZEN",
            })
    return out


def load_pre_unresolved(path: Path) -> list[dict]:
    out=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            out.append({
                "evaluation_year":int(r["evaluation_year"]),
                "origin_date":r["origin_date"],
                "target_date":r["target_date"],
                "actual_up":int(r["actual_up"]),
                "meta_y":int(int(r["actual_up"])==0),
            })
    return out


def external_base_days(base, spine: list[dict]):
    out=[]
    for r in spine:
        out.append(base.BaseDay(
            date.fromisoformat(r["date"]),
            float(r["close"]),
            int(r["n_bars"]),
            int(r["n_bars"])-1,
            float(r["rv"]),
            float(r["r3"]),
            float(r["rs_plus"]),
            float(r["rs_minus"]),
        ))
    return out


def external_router_rows(base, spine: list[dict]) -> tuple[list[dict],dict]:
    """Exact Router-V2-style external extension: Y-1 formation, causal within-year updates."""
    days=external_base_days(base,spine)
    tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    tmap={r["target_date"]:r for r in trows}
    bmaps=base.bonato_maps(bdays)
    lmaps=base.logit_maps(ldays)
    contexts=base.legacy_context(daily)

    common=sorted(
        set(tmap)
        & set(bmaps["BONATO_AR1_RM_QBOOST_H1"])
        & set(lmaps["AR1_RM_LOGIT"])
        & set(lmaps["RM_LOGIT"])
    )
    base_rows=[]
    for td in common:
        t=tmap[td]
        b=bmaps["BONATO_AR1_RM_QBOOST_H1"][td]
        ar=lmaps["AR1_RM_LOGIT"][td]
        rm=lmaps["RM_LOGIT"][td]
        od=t["origin_date"]
        if not (od==b["origin_date"]==ar["origin_date"]==rm["origin_date"]):
            raise RuntimeError(f"EXTERNAL_ROUTER_ORIGIN_MISMATCH:{td}")
        vals=[int(t["actual_up"]),int(b["actual_up"]),int(ar["actual_up"]),int(rm["actual_up"])]
        if len(set(vals))!=1:
            raise RuntimeError(f"EXTERNAL_ROUTER_ACTUAL_MISMATCH:{td}:{vals}")
        ctx=contexts[od]
        base_rows.append({
            "origin_date":od,"target_date":td,"actual_up":vals[0],
            "TTSM_S2":int(t["ttsm_s2_signal"]==1),
            "TTSM_S1":int(t["ttsm_s1_signal"]==1),
            "BONATO_AR1_RM_QBOOST_H1":int(b["up"]),
            "AR1_RM_LOGIT":int(ar["up"]),
            "RM_LOGIT":int(rm["up"]),
            **ctx,
        })

    by_year={}
    for r in base_rows:
        by_year.setdefault(int(r["target_date"][:4]),[]).append(r)

    def score_year(eval_rows, history):
        hist=[dict(r) for r in history]
        scored=[]
        for base_row in eval_rows:
            row=dict(base_row)
            eligible=[]
            for expert in base.DIRECT_UP_EXPERTS:
                if row[expert]!=1:
                    continue
                st=base.router_stats(hist,expert,row["legacy_bucket"])
                if st is None:
                    continue
                if st["n_up"]<30 or st["precision"]<=0.50 or st["fpr"]>=0.50:
                    continue
                eligible.append((expert,st))
            if eligible:
                eligible.sort(key=lambda x:(
                    -x[1]["lcb"],x[1]["fpr"],-x[1]["precision"],base.ROUTER_TIE_ORDER[x[0]]
                ))
                selected,st=eligible[0]
                row["router_up"]=1
                row["selected_expert"]=selected
            else:
                row["router_up"]=0
                row["selected_expert"]=""
            scored.append(row)
            hist.append(dict(base_row))
        return scored

    scored=[]
    for year in (2020,2021):
        scored.extend(score_year(by_year.get(year,[]),by_year.get(year-1,[])))

    summary={}
    for year in (2020,2021):
        rr=[r for r in scored if int(r["target_date"][:4])==year]
        up=[r for r in rr if int(r["router_up"])==1]
        summary[str(year)]={
            "n":len(rr),"router_up":len(up),
            "tp":sum(r["actual_up"]==1 for r in up),
            "fp":sum(r["actual_up"]==0 for r in up),
        }
    return scored,summary


def route_external_sqrt_cases(ext_sqrt: list[dict], router_rows: list[dict]) -> tuple[list[dict],dict]:
    rmap={(r["origin_date"],r["target_date"]):r for r in router_rows}
    unresolved=[]
    summary={}
    for year in (2020,2021):
        alarms=[r for r in ext_sqrt if int(r["evaluation_year"])==year]
        overlap=[]
        abstain=[]
        for s in alarms:
            rr=rmap.get((s["origin_date"],s["target_date"]))
            if rr is None:
                raise RuntimeError(f"EXTERNAL_ROUTER_ROW_NOT_FOUND:{s['origin_date']}->{s['target_date']}")
            actual_up=int(float(s["target_return"])>0)
            if int(rr["actual_up"])!=actual_up:
                raise RuntimeError(f"EXTERNAL_ROUTER_SIGN_MISMATCH:{s['target_date']}")
            z=dict(s)
            z["actual_up"]=actual_up
            z["router_up"]=int(rr["router_up"])
            z["selected_expert"]=rr["selected_expert"]
            z["meta_y"]=int(actual_up==0)
            if z["router_up"]==1:
                overlap.append(z)
            else:
                z["source"]="EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN"
                abstain.append(z)
                unresolved.append(z)
        summary[str(year)]={
            "sqrt_alarms":len(alarms),
            "router_up_overlap":len(overlap),
            "overlap_actual_up":sum(r["actual_up"]==1 for r in overlap),
            "overlap_actual_down":sum(r["actual_up"]==0 for r in overlap),
            "router_abstain":len(abstain),
            "abstain_actual_down":sum(r["actual_up"]==0 for r in abstain),
            "abstain_actual_up":sum(r["actual_up"]==1 for r in abstain),
        }
    return unresolved,summary


def reconstruct_2025(base, sqrt_parent: Path) -> list[dict]:
    days=base.load_days()
    tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    tmap={r["target_date"]:r for r in trows}
    bmaps=base.bonato_maps(bdays)
    lmaps=base.logit_maps(ldays)
    contexts=base.legacy_context(daily)
    router=base.build_router_rows(trows,bmaps,lmaps,contexts)
    rmap={(r["origin_date"],r["target_date"]):r for r in router}
    sqrt=base.load_sqrt(sqrt_parent)
    out=[]
    for s in sqrt:
        if s["evaluation_year"]!=2025:
            continue
        rr=rmap.get((s["origin_date"],s["target_date"]))
        if rr is None:
            raise RuntimeError(f"ROUTER25_NOT_FOUND:{s['target_date']}")
        if int(rr["actual_up"])!=int(s["actual_up"]):
            raise RuntimeError(f"ROUTER25_SIGN_MISMATCH:{s['target_date']}")
        if int(rr["router_up"])==0:
            out.append({
                "evaluation_year":2025,
                "origin_date":s["origin_date"],
                "target_date":s["target_date"],
                "actual_up":int(s["actual_up"]),
                "meta_y":int(int(s["actual_up"])==0),
            })
    return out


def attach_paths(rows: list[dict], path_map: dict[str,np.ndarray], source: str) -> list[dict]:
    out=[]
    for r in rows:
        p=path_map.get(r["origin_date"])
        if p is None:
            raise RuntimeError(f"MISSING_{source}_PATH:{r['origin_date']}->{r['target_date']}")
        z=dict(r)
        z["path"]=p
        z["path_source"]=source
        out.append(z)
    return out


def corr(a,b):
    x=np.asarray(a,float).ravel()
    y=np.asarray(b,float).ravel()
    if np.std(x)<=1e-15 or np.std(y)<=1e-15:
        return 1.0 if np.allclose(x,y,atol=1e-12,rtol=0) else 0.0
    return float(np.corrcoef(x,y)[0,1])


def path_harmonization(cbr, ext_raw: dict[str,dict], governed_raw: dict[str,list[float]]) -> dict:
    calendar_common=sorted(set(ext_raw) & set(governed_raw))
    common=[]
    skipped_short=[]
    skipped_bad_rv=[]
    ext_paths={}
    gov_paths={}
    for d in calendar_common:
        er=np.asarray(ext_raw[d]["rets"],float)
        gr=np.asarray(governed_raw[d],float)
        if len(er)<239 or len(gr)<239:
            skipped_short.append({"date":d,"external_returns":len(er),"governed_returns":len(gr)})
            continue
        if not (float(np.sum(er*er))>0 and float(np.sum(gr*gr))>0):
            skipped_bad_rv.append(d)
            continue
        ext_paths[d]=cbr.path_repr(er)
        gov_paths[d]=cbr.path_repr(gr)
        common.append(d)

    same_d=[];shift_d=[];cors=[]
    for d in common:
        same_d.append(cbr.dtw(ext_paths[d],gov_paths[d]))
        cors.append(corr(ext_paths[d],gov_paths[d]))
    if common:
        for i,d in enumerate(common):
            d2=common[(i+1)%len(common)]
            shift_d.append(cbr.dtw(ext_paths[d],gov_paths[d2]))
    med_same=float(np.median(same_d)) if same_d else None
    med_shift=float(np.median(shift_d)) if shift_d else None
    ratio=(med_same/med_shift) if med_same is not None and med_shift and med_shift>0 else None
    frac=(float(np.mean(np.asarray(same_d)<med_shift)) if same_d and med_shift is not None else None)
    med_corr=float(np.median(cors)) if cors else None
    passed=bool(
        len(common)>=300
        and med_corr is not None and med_corr>=0.98
        and ratio is not None and ratio<0.25
        and frac is not None and frac>=0.90
    )
    return {
        "passed":passed,
        "calendar_overlap_n":len(calendar_common),
        "overlap_n":len(common),
        "skipped_short_n":len(skipped_short),
        "skipped_short_examples":skipped_short[:20],
        "skipped_nonpositive_rv_n":len(skipped_bad_rv),
        "median_same_date_flat_corr":med_corr,
        "median_same_date_dtw":med_same,
        "median_shifted_date_dtw":med_shift,
        "median_same_to_shifted_dtw_ratio":ratio,
        "fraction_same_below_shifted_median":frac,
        "p90_same_date_dtw":float(np.quantile(same_d,.90)) if same_d else None,
    }


def case_prob_with_neighbors(cbr, train: list[dict], target: dict):
    ds=[]
    for r in train:
        d=cbr.dtw(r["path"],target["path"])
        ds.append((float(d),int(r["meta_y"]),r))
    ds.sort(key=lambda x:x[0])
    nn=ds[:cbr.K]
    exact=[y for d,y,r in nn if d<1e-12]
    if exact:
        p=float(np.mean(exact))
    else:
        w=np.asarray([1.0/(d+cbr.EPS) for d,y,r in nn],float)
        y=np.asarray([y for d,y,r in nn],float)
        p=float(np.sum(w*y)/np.sum(w))
    details=[{
        "distance":d,
        "down_label":y,
        "target_date":r["target_date"],
        "evaluation_year":int(r["evaluation_year"]),
        "source":r.get("source",r.get("path_source","")),
    } for d,y,r in nn]
    return p,float(np.mean([d for d,y,r in nn])),details


def metrics(rows: list[dict]) -> dict:
    n=len(rows)
    actual_down=sum(r["meta_y"]==1 for r in rows)
    actual_up=n-actual_down
    calls=[r for r in rows if r["down_call"]==1]
    dc=len(calls)
    correct=sum(r["meta_y"]==1 for r in calls)
    false=sum(r["meta_y"]==0 for r in calls)
    precision=correct/dc if dc else None
    recall=correct/actual_down if actual_down else None
    fpr=false/actual_up if actual_up else None
    return {
        "n":n,"actual_down":actual_down,"actual_up":actual_up,
        "down_calls":dc,"correct_down":correct,"false_down":false,
        "down_precision":precision,"down_recall":recall,
        "false_down_fpr":fpr,
        "call_coverage":dc/n if n else None,
        "wilson90_lcb_down_precision":wilson_lcb(correct,dc),
        "mean_p_down":float(np.mean([r["p_down"] for r in rows])) if rows else None,
        "mean_neighbor_distance":float(np.mean([r["neighbor_distance"] for r in rows])) if rows else None,
    }


def score_year(cbr, train: list[dict], test: list[dict]) -> tuple[list[dict],dict]:
    scored=[]
    for t in test:
        p,d,nn=case_prob_with_neighbors(cbr,train,t)
        z=dict(t)
        z["p_down"]=p
        z["neighbor_distance"]=d
        z["down_call"]=int(p>=0.50)
        z["neighbors"]=nn
        scored.append(z)
    m=metrics(scored)
    m["train_n"]=len(train)
    m["train_down"]=sum(r["meta_y"]==1 for r in train)
    m["train_up"]=sum(r["meta_y"]==0 for r in train)
    m["train_by_year"]={}
    for y in sorted({int(r["evaluation_year"]) for r in train}):
        sub=[r for r in train if int(r["evaluation_year"])==y]
        m["train_by_year"][str(y)]={
            "n":len(sub),
            "down":sum(r["meta_y"]==1 for r in sub),
            "up":sum(r["meta_y"]==0 for r in sub),
            "source_counts":{
                s:sum(r.get("source","")==s for r in sub)
                for s in sorted({r.get("source","") for r in sub})
            }
        }
    return scored,m


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument("--raw-root",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    ap.add_argument("--sqrt-code",type=Path,required=True)
    ap.add_argument("--cbr-code",type=Path,required=True)
    ap.add_argument("--base-module",type=Path,required=True)
    ap.add_argument("--sqrt-parent",type=Path,required=True)
    ap.add_argument("--pre-ledger",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)

    cbr=load_mod("pinned_cbr_dtw_v1",args.cbr_code)
    sqrt_mod=load_sqrt_mod(args.sqrt_code)

    ext_spine=load_external_spine(args.external_spine)
    ext_raw=build_external_5m(args.raw_root)
    ext_audit=external_reconstruction_audit(ext_raw,ext_spine)
    if not ext_audit["passed"]:
        result={
            "identity":IDENTITY,"status":"BLOCKED_EXTERNAL_PATH_RECONSTRUCTION",
            "external_reconstruction":ext_audit,
            "integrity_errors":["EXTERNAL_PATH_RECONSTRUCTION_FAILED"],
        }
        (args.out/"GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2

    # Load governed paths over the full 2020-2025 range once. This is read-only.
    governed_raw=cbr.load_paths(["2020-01-02","2025-12-31"])
    harmon=path_harmonization(cbr,ext_raw,governed_raw)
    if not harmon["passed"]:
        result={
            "identity":IDENTITY,"status":"BLOCKED_PATH_HARMONIZATION",
            "external_reconstruction":ext_audit,
            "path_harmonization":harmon,
            "integrity_errors":["PATH_HARMONIZATION_GATE_FAILED"],
        }
        (args.out/"GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2

    ext_daily=load_external_daily_for_sqrt(ext_spine)
    ext_sqrt,ext_sqrt_summary=external_sqrt_cases(sqrt_mod,ext_daily)
    expected_sqrt={"2020":{"alarms":212,"down":97,"up":115},
                   "2021":{"alarms":28,"down":16,"up":12}}
    if ext_sqrt_summary!=expected_sqrt:
        result={
            "identity":IDENTITY,"status":"BLOCKED_EXTERNAL_SQRT_ROUTER_MISMATCH",
            "external_reconstruction":ext_audit,
            "path_harmonization":harmon,
            "external_sqrt_summary":ext_sqrt_summary,
            "expected_external_sqrt_summary":expected_sqrt,
            "integrity_errors":["EXTERNAL_SQRT_AGGREGATE_MISMATCH"],
        }
        (args.out/"GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2

    base=load_mod("pinned_down_audit_base",args.base_module)
    ext_router,ext_router_summary=external_router_rows(base,ext_spine)
    expected_router={
        "2020":{"n":260,"router_up":185,"tp":111,"fp":74},
        "2021":{"n":258,"router_up":33,"tp":19,"fp":14},
    }
    if ext_router_summary!=expected_router:
        result={
            "identity":IDENTITY,"status":"BLOCKED_EXTERNAL_SQRT_ROUTER_MISMATCH",
            "external_reconstruction":ext_audit,
            "path_harmonization":harmon,
            "external_sqrt_summary":ext_sqrt_summary,
            "external_router_summary":ext_router_summary,
            "expected_external_router_summary":expected_router,
            "integrity_errors":["EXTERNAL_ROUTER_AGGREGATE_MISMATCH"],
        }
        (args.out/"GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2

    ext_unresolved,ext_route_summary=route_external_sqrt_cases(ext_sqrt,ext_router)
    expected_route={
        "2020":{"sqrt_alarms":212,"router_up_overlap":140,"overlap_actual_up":80,"overlap_actual_down":60,
                "router_abstain":72,"abstain_actual_down":37,"abstain_actual_up":35},
        "2021":{"sqrt_alarms":28,"router_up_overlap":2,"overlap_actual_up":1,"overlap_actual_down":1,
                "router_abstain":26,"abstain_actual_down":15,"abstain_actual_up":11},
    }
    if ext_route_summary!=expected_route:
        result={
            "identity":IDENTITY,"status":"BLOCKED_EXTERNAL_SQRT_ROUTER_MISMATCH",
            "external_reconstruction":ext_audit,
            "path_harmonization":harmon,
            "external_sqrt_summary":ext_sqrt_summary,
            "external_router_summary":ext_router_summary,
            "external_route_summary":ext_route_summary,
            "expected_external_route_summary":expected_route,
            "integrity_errors":["EXTERNAL_ROUTE_INTERSECTION_MISMATCH"],
        }
        (args.out/"GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2

    ext_path_map={d:cbr.path_repr(v["rets"]) for d,v in ext_raw.items()}
    ext_cases=attach_paths(ext_unresolved,ext_path_map,"EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN")
    if len(ext_cases)!=98 or sum(r["meta_y"] for r in ext_cases)!=52:
        raise RuntimeError(f"EXTERNAL_ROUTE_LIBRARY_MISMATCH:{len(ext_cases)}/{sum(r['meta_y'] for r in ext_cases)}")

    gov_path_map={
        d:cbr.path_repr(rets)
        for d,rets in governed_raw.items()
        if len(rets)>=239 and float(np.sum(np.asarray(rets,float)**2))>0
    }

    primary=load_pre_unresolved(args.pre_ledger)
    counts={}
    for year in (2022,2023,2024):
        sub=[r for r in primary if r["evaluation_year"]==year]
        counts[str(year)]={"n":len(sub),"down":sum(r["meta_y"] for r in sub),"up":sum(1-r["meta_y"] for r in sub)}
    expected_gov={"2022":{"n":11,"down":6,"up":5},"2023":{"n":2,"down":1,"up":1},"2024":{"n":13,"down":6,"up":7}}
    if counts!=expected_gov:
        result={
            "identity":IDENTITY,"status":"BLOCKED_GOVERNED_ROUTE_MISMATCH",
            "governed_unresolved_summary":counts,
            "expected_governed_unresolved_summary":expected_gov,
            "integrity_errors":["GOVERNED_PRE2025_ROUTE_MISMATCH"],
        }
        (args.out/"GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2
    primary=attach_paths(primary,gov_path_map,"GOVERNED_ROUTER_ABSTAIN")
    gov_cases=[dict(r,source="GOVERNED_ROUTER_ABSTAIN") for r in primary]

    stress25=reconstruct_2025(base,args.sqrt_parent)
    if len(stress25)!=74 or sum(r["meta_y"] for r in stress25)!=39:
        result={
            "identity":IDENTITY,"status":"BLOCKED_GOVERNED_ROUTE_MISMATCH",
            "locked_2025":{"n":len(stress25),"down":sum(r["meta_y"] for r in stress25)},
            "integrity_errors":["LOCKED2025_ROUTE_MISMATCH"],
        }
        (args.out/"GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
        print(json.dumps(result,indent=2))
        return 2
    stress25=attach_paths(stress25,gov_path_map,"GOVERNED_ROUTER_ABSTAIN")

    by_year={}
    scored_all=[]
    for year in (2022,2023,2024):
        train=[r for r in ext_cases if int(r["evaluation_year"])<=2021]
        train += [r for r in gov_cases if int(r["evaluation_year"])<year]
        test=[r for r in primary if int(r["evaluation_year"])==year]
        scored,m=score_year(cbr,train,test)
        by_year[str(year)]=m
        scored_all.extend(scored)

    expected_train_n={"2022":98,"2023":109,"2024":111}
    observed_train_n={y:int(by_year[y]["train_n"]) for y in ("2022","2023","2024")}
    if observed_train_n!=expected_train_n:
        raise RuntimeError(f"ROUTE_TRAIN_COUNTS_MISMATCH:{observed_train_n}!={expected_train_n}")

    pooled=metrics(scored_all)
    pre_support=bool(
        pooled["n"]==26
        and pooled["down_calls"]>=5
        and pooled["down_precision"] is not None and pooled["down_precision"]>0.50
        and pooled["false_down_fpr"] is not None and pooled["false_down_fpr"]<0.50
    )

    train25=[r for r in ext_cases if int(r["evaluation_year"])<=2021]
    train25 += [r for r in gov_cases if int(r["evaluation_year"])<=2024]
    scored25,m25=score_year(cbr,train25,stress25)
    if int(m25["train_n"])!=124:
        raise RuntimeError(f"ROUTE_TRAIN25_COUNT_MISMATCH:{m25['train_n']}!=124")
    baseline25=39/74
    transport_support=bool(
        m25["down_calls"]>=5
        and m25["down_precision"] is not None and m25["down_precision"]>baseline25
        and m25["false_down_fpr"] is not None and m25["false_down_fpr"]<0.50
    )
    m25["baseline_down_prevalence"]=baseline25
    m25["precision_lift_vs_baseline"]=(
        m25["down_precision"]-baseline25 if m25["down_precision"] is not None else None
    )
    m25["transport_supportive"]=transport_support

    if pre_support and transport_support:
        status="CASCADE_ROUTE_CONSISTENT_WITH_SUPPORTIVE_LOCKED2025_TRANSPORT"
    elif pre_support:
        status="CASCADE_ROUTE_CONSISTENT_PRE2025_ONLY"
    else:
        status="CASCADE_ROUTE_CONSISTENT_NOT_SUPPORTED"

    # Neighbor provenance diagnostic.
    neighbor_counts={}
    for label,rows in [("pre2025",scored_all),("locked2025",scored25)]:
        counts={}
        for r in rows:
            for n in r["neighbors"]:
                key=f"{n['source']}:{n['evaluation_year']}"
                counts[key]=counts.get(key,0)+1
        neighbor_counts[label]=counts

    result={
        "identity":IDENTITY,
        "date":"2026-09-23",
        "status":status,
        "integrity_errors":[],
        "pins":{
            "mirror_commit":MIRROR_COMMIT,
            "external_spine_commit":EXTERNAL_SPINE_COMMIT,
            "sqrt_code_commit":SQRT_CODE_COMMIT,
            "cbr_code_commit":CBR_CODE_COMMIT,
            "base_audit_commit":BASE_AUDIT_COMMIT,
        },
        "frozen_method":{
            "npts":int(cbr.NPTS),"dtw_band":int(cbr.BAND),"k":int(cbr.K),
            "eps":float(cbr.EPS),"threshold":0.50,
            "strict_pool":"historical SQRT HIGH RISK + frozen UP Verifier ABSTAIN only",
        },
        "external_reconstruction":ext_audit,
        "path_harmonization":harmon,
        "external_sqrt_summary":ext_sqrt_summary,
        "external_router_summary":ext_router_summary,
        "external_route_summary":ext_route_summary,
        "external_route_consistent_training_cases":{
            "n":len(ext_cases),
            "down":sum(r["meta_y"] for r in ext_cases),
            "up":sum(1-r["meta_y"] for r in ext_cases),
        },
        "by_year_2022_2024":by_year,
        "pooled_2022_2024":pooled,
        "pre2025_extension_supportive":pre_support,
        "locked_2025":m25,
        "neighbor_provenance_counts":neighbor_counts,
        "original_comparators":{
            "2024_unresolved_original_cbr":{
                "n":13,"down_calls":5,"correct_down":3,"false_down":2,
                "precision":0.60,"recall":0.50,"false_down_fpr":2/7,
            },
            "2025_unresolved_original_cbr":{
                "n":74,"down_calls":33,"correct_down":21,"false_down":12,
                "precision":21/33,"recall":21/39,"false_down_fpr":12/35,
            },
        },
        "governance":{
            "random_split":False,
            "threshold_tuning":False,
            "k_band_representation_tuning":False,
            "2025_used_for_selection":False,
            "2026_used":False,
            "raw_third_party_committed":False,
            "production_writes":False,
            "runtime_promotion":False,
        },
    }
    out_json=args.out/"GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESULT_2026-09-23.json"
    out_json.write_text(json.dumps(result,indent=2),encoding="utf-8")

    # Exact scored rows for audit; neighbors are JSON-encoded.
    all_rows=scored_all+scored25
    fields=["evaluation_year","origin_date","target_date","actual_up","meta_y",
            "p_down","down_call","neighbor_distance","neighbors"]
    with (args.out/"GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_LEDGER_2026-09-23.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for r in all_rows:
            w.writerow({
                "evaluation_year":r["evaluation_year"],
                "origin_date":r["origin_date"],
                "target_date":r["target_date"],
                "actual_up":r["actual_up"],
                "meta_y":r["meta_y"],
                "p_down":r["p_down"],
                "down_call":r["down_call"],
                "neighbor_distance":r["neighbor_distance"],
                "neighbors":json.dumps(r["neighbors"],separators=(",",":")),
            })

    lines=[
        "# GOLD CONTROL — CBR CASCADE-ROUTE-CONSISTENT EXTENSION V1 RESULT","",
        f"**Status:** `{status}`  ",
        "**Integrity errors:** none","",
        "## External/path integrity","",
        f"- external reconstruction pass: {ext_audit['passed']}",
        f"- overlap path harmonization n: {harmon['overlap_n']}",
        f"- median same-date path correlation: {harmon['median_same_date_flat_corr']}",
        f"- median same/shifted DTW ratio: {harmon['median_same_to_shifted_dtw_ratio']}",
        f"- fraction same-date DTW below shifted median: {harmon['fraction_same_below_shifted_median']}",
        "",
        "## Historical extension results","",
        "| Year | n | Train n | DOWN calls | Correct | False | Precision | Recall | FPR |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|"
    ]
    for y in ("2022","2023","2024"):
        m=by_year[y]
        lines.append(
            f"| {y} | {m['n']} | {m['train_n']} | {m['down_calls']} | {m['correct_down']} | "
            f"{m['false_down']} | {m['down_precision']} | {m['down_recall']} | {m['false_down_fpr']} |"
        )
    lines += [
        "",
        f"Pooled 2022–2024: n={pooled['n']}, DOWN calls={pooled['down_calls']}, "
        f"correct={pooled['correct_down']}, false={pooled['false_down']}, "
        f"precision={pooled['down_precision']}, recall={pooled['down_recall']}, FPR={pooled['false_down_fpr']}.",
        "",
        "## Locked 2025 transport","",
        f"n={m25['n']}; DOWN calls={m25['down_calls']}; correct={m25['correct_down']}; "
        f"false={m25['false_down']}; precision={m25['down_precision']}; recall={m25['down_recall']}; "
        f"FPR={m25['false_down_fpr']}; baseline={baseline25}; "
        f"precision lift={m25['precision_lift_vs_baseline']}; supportive={transport_support}.",
        "",
        "No threshold, K, DTW band or representation was changed. 2025 remained locked transport only; 2026 was not used."
    ]
    (args.out/"GOLD_CONTROL_CBR_CASCADE_ROUTE_CONSISTENT_EXTENSION_V1_RESULT_2026-09-23.md").write_text("\n".join(lines)+"\n",encoding="utf-8")

    print(json.dumps({
        "status":status,
        "external_reconstruction":ext_audit,
        "path_harmonization":harmon,
        "external_sqrt_summary":ext_sqrt_summary,
        "external_router_summary":ext_router_summary,
        "external_route_summary":ext_route_summary,
        "by_year":by_year,
        "pooled_2022_2024":pooled,
        "locked_2025":m25,
        "neighbor_provenance_counts":neighbor_counts,
    },indent=2))
    return 0


if __name__=="__main__":
    raise SystemExit(main())
