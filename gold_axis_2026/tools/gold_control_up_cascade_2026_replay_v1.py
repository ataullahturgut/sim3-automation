from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import os
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import psycopg

IDENTITY="GOLD_CONTROL_UP_CASCADE_2026_REPLAY_V1"
TZ="America/New_York"
TABLE="public.xau_intraday_research_cache_5m"
MIN_BARS=240
CUTOFF="2026-09-01T05:00:00Z"

def load_mod(name,path):
    spec=importlib.util.spec_from_file_location(name,str(path))
    if spec is None or spec.loader is None:
        raise RuntimeError(f"IMPORT_FAIL:{name}:{path}")
    mod=importlib.util.module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def load_days_extended(base):
    sql=f"""
    with b as (
      select
        (observation_ts at time zone '{TZ}')::date as d,
        observation_ts,
        close::double precision as close,
        lag(close::double precision) over (
          partition by (observation_ts at time zone '{TZ}')::date
          order by observation_ts
        ) as prev_close
      from {TABLE}
      where observation_ts >= '2020-01-01'::timestamptz
        and observation_ts < %s::timestamptz
        and extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    ),
    intr as (
      select d, observation_ts, close,
             case when prev_close is not null and prev_close > 0
                  then ln(close/prev_close) else null end as r
      from b
    )
    select d,
      count(*)::int,
      count(r)::int,
      (array_agg(close order by observation_ts desc))[1]::double precision,
      coalesce(sum(r*r),0)::double precision,
      coalesce(sum(r*r*r),0)::double precision,
      coalesce(sum(case when r > 0 then r*r else 0 end),0)::double precision,
      coalesce(sum(case when r < 0 then r*r else 0 end),0)::double precision
    from intr
    group by d
    having count(*) >= {MIN_BARS}
    order by d
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only=on")
            cur.execute(sql,(CUTOFF,))
            raw=cur.fetchall()
    out=[]
    for d,n,m,c,rv,r3,rp,rm in raw:
        vals=[float(c),float(rv),float(r3),float(rp),float(rm)]
        if not all(math.isfinite(x) for x in vals) or vals[0]<=0:
            raise RuntimeError(f"BAD_DAY:{d}")
        out.append(base.BaseDay(d,vals[0],int(n),int(m),vals[1],vals[2],vals[3],vals[4]))
    if len(out)<1200:
        raise RuntimeError(f"EXTENDED_DAYS_TOO_SHORT:{len(out)}")
    return out

def build_router_rows_extended(base,days):
    tdays,bdays,ldays,daily=base.transformed(days)
    trows=base.ttsm_mod.build_signal_rows(tdays)
    bmaps=base.bonato_maps(bdays)
    lmaps=base.logit_maps(ldays)
    contexts=base.legacy_context(daily)

    tmap={r["target_date"]:r for r in trows}
    common=sorted(
        set(tmap)
        & set(bmaps["BONATO_AR1_RM_QBOOST_H1"])
        & set(lmaps["AR1_RM_LOGIT"])
        & set(lmaps["RM_LOGIT"])
    )
    base_rows=[]
    for td in common:
        t=tmap[td]; b=bmaps["BONATO_AR1_RM_QBOOST_H1"][td]
        ar=lmaps["AR1_RM_LOGIT"][td]; rm=lmaps["RM_LOGIT"][td]
        od=t["origin_date"]
        if not (od==b["origin_date"]==ar["origin_date"]==rm["origin_date"]):
            raise RuntimeError(f"ORIGIN_MISMATCH:{td}")
        ys=[int(t["actual_up"]),int(b["actual_up"]),int(ar["actual_up"]),int(rm["actual_up"])]
        if len(set(ys))!=1:
            raise RuntimeError(f"ACTUAL_MISMATCH:{td}:{ys}")
        base_rows.append({
            "origin_date":od,"target_date":td,"actual_up":ys[0],
            "TTSM_S2":int(t["ttsm_s2_signal"]==1),
            "TTSM_S1":int(t["ttsm_s1_signal"]==1),
            "BONATO_AR1_RM_QBOOST_H1":int(b["up"]),
            "AR1_RM_LOGIT":int(ar["up"]),
            "RM_LOGIT":int(rm["up"]),
            **contexts[od],
        })

    by_year=defaultdict(list)
    for r in base_rows:
        by_year[int(r["target_date"][:4])].append(r)

    def score(eval_rows,history):
        hist=[dict(r) for r in history]
        scored=[]
        for br in eval_rows:
            row=dict(br)
            elig=[]
            for expert in base.DIRECT_UP_EXPERTS:
                if row[expert]!=1:
                    continue
                st=base.router_stats(hist,expert,row["legacy_bucket"])
                if st is None:
                    continue
                if st["n_up"]<30 or st["precision"]<=0.50 or st["fpr"]>=0.50:
                    continue
                elig.append((expert,st))
            if elig:
                elig.sort(key=lambda x:(
                    -x[1]["lcb"],x[1]["fpr"],-x[1]["precision"],base.ROUTER_TIE_ORDER[x[0]]
                ))
                expert,st=elig[0]
                row.update({
                    "router_up":1,
                    "selected_expert":expert,
                    "selected_lcb":st["lcb"],
                    "selected_precision":st["precision"],
                    "selected_fpr":st["fpr"],
                    "selected_history_n_up":st["n_up"],
                    "selected_scope":st["scope"],
                })
            else:
                row.update({
                    "router_up":0,"selected_expert":"",
                    "selected_lcb":None,"selected_precision":None,
                    "selected_fpr":None,"selected_history_n_up":None,
                    "selected_scope":"",
                })
            scored.append(row)
            hist.append(dict(br))
        return scored,hist

    scored=[]
    for y in (2022,2023):
        sy,_=score(by_year.get(y,[]),by_year.get(y-1,[]))
        scored.extend(sy)

    s24,h=score(by_year.get(2024,[]),by_year.get(2023,[])); scored.extend(s24)
    s25,h=score(by_year.get(2025,[]),h); scored.extend(s25)
    s26,h=score(by_year.get(2026,[]),h); scored.extend(s26)
    return scored

def load_parent(path):
    rows=[]
    with path.open(newline="",encoding="utf-8") as f:
        for r in csv.DictReader(f):
            y=int(r["evaluation_year"])
            if y not in (2022,2023,2024,2025,2026):
                continue
            ret=float(r["target_close_return"])
            if ret==0:
                continue
            rows.append({
                "evaluation_year":y,
                "origin_date":r["origin_date"],
                "target_date":r["target_date"],
                "sqrt_alert":int(r["sqrt_high_risk_alert"]),
                "sqrt_score":float(r["sqrt_normalized_risk_score"]),
                "actual_up":int(ret>0),
                "target_close_return":ret,
            })
    return rows

def router_metrics(rows):
    calls=[r for r in rows if int(r["router_up"])==1]
    tp=sum(int(r["actual_up"])==1 for r in calls)
    fp=sum(int(r["actual_up"])==0 for r in calls)
    actual_up=sum(int(r["actual_up"])==1 for r in rows)
    actual_down=sum(int(r["actual_up"])==0 for r in rows)
    n=len(rows); nc=len(calls)
    return {
        "n":n,
        "actual_up":actual_up,
        "actual_down":actual_down,
        "up_calls":nc,
        "true_up":tp,
        "false_up":fp,
        "up_precision":tp/nc if nc else None,
        "call_error_rate":fp/nc if nc else None,
        "false_up_fpr":fp/actual_down if actual_down else None,
        "actual_up_recall":tp/actual_up if actual_up else None,
        "coverage":nc/n if n else None,
        "abstain":n-nc,
        "selected_counts":dict(Counter(r["selected_expert"] for r in calls)),
        "output_bucket_counts":dict(Counter(r["legacy_bucket"] for r in calls)),
    }

def make_external_cases(route,up2,base,sqrt_mod,cbr,raw_root,external_spine):
    ext_spine=route.load_external_spine(external_spine)
    ext_raw=route.build_external_5m(raw_root)
    audit=route.external_reconstruction_audit(ext_raw,ext_spine)
    if not audit["passed"]:
        raise RuntimeError("EXTERNAL_RECONSTRUCTION_FAILED")
    ext_daily=route.load_external_daily_for_sqrt(ext_spine)
    ext_sqrt,sqsum=route.external_sqrt_cases(sqrt_mod,ext_daily)
    ext_router,rsum=route.external_router_rows(base,ext_spine)
    unresolved,routesum=route.route_external_sqrt_cases(ext_sqrt,ext_router)
    expected={
        "2020":{"sqrt_alarms":212,"router_up_overlap":140,"overlap_actual_up":80,"overlap_actual_down":60,
                "router_abstain":72,"abstain_actual_down":37,"abstain_actual_up":35},
        "2021":{"sqrt_alarms":28,"router_up_overlap":2,"overlap_actual_up":1,"overlap_actual_down":1,
                "router_abstain":26,"abstain_actual_down":15,"abstain_actual_up":11},
    }
    if routesum!=expected:
        raise RuntimeError(f"EXTERNAL_ROUTE_MISMATCH:{routesum}")
    rmap={(r["origin_date"],r["target_date"]):r for r in ext_router}
    smap={(r["origin_date"],r["target_date"]):r for r in ext_sqrt}
    lag=up2.lag_map_from_spine(ext_spine)
    cases=[]
    for r in unresolved:
        key=(r["origin_date"],r["target_date"])
        cases.append(up2.enrich_case(
            r,smap[key]["sqrt_normalized_risk_score"],rmap[key],
            lag[r["origin_date"]],ext_raw[r["origin_date"]]["rets"],
            "EXTERNAL_DUKASCOPY_V2_ROUTER_ABSTAIN"
        ))
    if len(cases)!=98 or sum(r["actual_up"] for r in cases)!=46:
        raise RuntimeError("EXTERNAL_CASE_MISMATCH")
    return cases,{"external_reconstruction":audit,"external_sqrt":sqsum,"external_router":rsum,"external_route":routesum}

def governed_residual_cases(up2,cbr,days,router,parent):
    rmap={(r["origin_date"],r["target_date"]):r for r in router}
    lag=up2.lag_map_from_base_days(days)
    origins=[r["origin_date"] for r in parent if r["sqrt_alert"]==1]
    raw=cbr.load_paths(origins)
    cases=[]
    for p in parent:
        if p["sqrt_alert"]!=1:
            continue
        key=(p["origin_date"],p["target_date"])
        rr=rmap.get(key)
        if rr is None:
            raise RuntimeError(f"ROUTER_NOT_FOUND:{key}")
        if int(rr["actual_up"])!=int(p["actual_up"]):
            raise RuntimeError(f"ROUTER_SIGN_MISMATCH:{key}")
        if int(rr["router_up"])==1:
            continue
        if p["origin_date"] not in raw:
            raise RuntimeError(f"RAW_PATH_NOT_FOUND:{p['origin_date']}")
        cases.append(up2.enrich_case(
            p,p["sqrt_score"],rr,lag[p["origin_date"]],
            raw[p["origin_date"]],"GOVERNED_ROUTER_ABSTAIN"
        ))
    return cases

def combined_alarm_metrics(alarm_rows,residual_scored):
    primary=[r for r in alarm_rows if int(r["router_up"])==1]
    second=[r for r in residual_scored if int(r["up2_call"])==1]
    tp=sum(int(r["actual_up"])==1 for r in primary)+sum(int(r["actual_up"])==1 for r in second)
    fp=sum(int(r["actual_up"])==0 for r in primary)+sum(int(r["actual_up"])==0 for r in second)
    calls=len(primary)+len(second)
    actual_up=sum(int(r["actual_up"])==1 for r in alarm_rows)
    actual_down=sum(int(r["actual_up"])==0 for r in alarm_rows)
    remain=[r for r in residual_scored if int(r["up2_call"])==0]
    return {
        "alarm_n":len(alarm_rows),
        "actual_up":actual_up,
        "actual_down":actual_down,
        "positive_up_calls":calls,
        "true_up":tp,
        "false_up":fp,
        "up_precision":tp/calls if calls else None,
        "call_error_rate":fp/calls if calls else None,
        "false_up_fpr":fp/actual_down if actual_down else None,
        "actual_up_recall":tp/actual_up if actual_up else None,
        "coverage":calls/len(alarm_rows) if alarm_rows else None,
        "remaining_hard_residual_n":len(remain),
        "remaining_actual_up":sum(int(r["actual_up"])==1 for r in remain),
        "remaining_actual_down":sum(int(r["actual_up"])==0 for r in remain),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--base-module",type=Path,required=True)
    ap.add_argument("--route-module",type=Path,required=True)
    ap.add_argument("--up2-module",type=Path,required=True)
    ap.add_argument("--cbr-code",type=Path,required=True)
    ap.add_argument("--sqrt-code",type=Path,required=True)
    ap.add_argument("--sqrt-parent",type=Path,required=True)
    ap.add_argument("--raw-root",type=Path,required=True)
    ap.add_argument("--external-spine",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)

    route=load_mod("route_authority_2026",args.route_module)
    up2=load_mod("up2_authority_2026",args.up2_module)
    cbr=load_mod("cbr_authority_2026",args.cbr_code)
    base=load_mod("base_authority_2026",args.base_module)
    sqrt_mod=route.load_sqrt_mod(args.sqrt_code)

    days=load_days_extended(base)
    router=build_router_rows_extended(base,days)
    parent=load_parent(args.sqrt_parent)
    pmap={(r["origin_date"],r["target_date"]):r for r in parent}
    rmap={(r["origin_date"],r["target_date"]):r for r in router}

    # Frozen checkpoint integrity.
    integrity=[]
    for y,exp in {
        2024:(42,26,16),
        2025:(37,27,10),
    }.items():
        rr=[r for r in router if int(r["target_date"][:4])==y]
        m=router_metrics(rr)
        got=(m["up_calls"],m["true_up"],m["false_up"])
        if got!=exp:
            integrity.append(f"PRIMARY_{y}:{got}!={exp}")
        if y==2025 and m["selected_counts"].get("RM_LOGIT",0)!=37:
            integrity.append(f"PRIMARY_2025_RM:{m['selected_counts'].get('RM_LOGIT',0)}!=37")

    p26=[p for p in parent if p["evaluation_year"]==2026]
    a26=[p for p in p26 if p["sqrt_alert"]==1]
    if len(p26)!=173:
        integrity.append(f"PARENT_2026_N:{len(p26)}!=173")
    if len(a26)!=148:
        integrity.append(f"PARENT_2026_ALARMS:{len(a26)}!=148")
    if sum(p["actual_up"] for p in a26)!=74:
        integrity.append("PARENT_2026_ALARM_UP_NOT_74")

    # Standalone primary 2026: use rows whose targets exist in frozen 2026 parent axis.
    primary26=[]
    alarm26=[]
    for p in p26:
        rr=rmap.get((p["origin_date"],p["target_date"]))
        if rr is None:
            integrity.append(f"PRIMARY26_ROW_MISSING:{p['target_date']}")
            continue
        if int(rr["actual_up"])!=int(p["actual_up"]):
            integrity.append(f"PRIMARY26_SIGN:{p['target_date']}")
            continue
        z=dict(rr); z["sqrt_alert"]=p["sqrt_alert"]; z["sqrt_score"]=p["sqrt_score"]
        primary26.append(z)
        if p["sqrt_alert"]==1:
            alarm26.append(z)

    primary26_metrics=router_metrics(primary26)
    primary26_alarm_metrics=router_metrics(alarm26)

    external_cases,extdiag=make_external_cases(
        route,up2,base,sqrt_mod,cbr,args.raw_root,args.external_spine
    )
    gov_cases=governed_residual_cases(up2,cbr,days,router,parent)

    by_year={y:[r for r in gov_cases if int(r["evaluation_year"])==y] for y in (2022,2023,2024,2025,2026)}
    expected_cases={2022:(11,5),2023:(2,1),2024:(13,7),2025:(74,35)}
    for y,(n,u) in expected_cases.items():
        got=(len(by_year[y]),sum(int(r["actual_up"]) for r in by_year[y]))
        if got!=(n,u):
            integrity.append(f"RESIDUAL_{y}:{got}!={(n,u)}")

    # Reproduce historical UP2 before opening 2026 score.
    hist=list(external_cases)
    scored_pre=[]
    for y in (2022,2023,2024):
        train=[r for r in hist if int(r["evaluation_year"])<y]
        scored,m=up2.score_year(train,by_year[y],y)
        scored_pre.extend(scored)
        hist.extend(by_year[y])
    pooled=up2.pooled_metrics(scored_pre)
    if not (pooled["n"]==26 and pooled["up2_calls"]==11 and pooled["true_up"]==8 and pooled["false_up"]==3):
        integrity.append(f"UP2_PRE:{pooled}")

    train25=external_cases+by_year[2022]+by_year[2023]+by_year[2024]
    scored25,m25=up2.score_year(train25,by_year[2025],2025)
    if not (m25.get("n")==74 and m25.get("up2_calls")==25 and m25.get("true_up")==13 and m25.get("false_up")==12):
        integrity.append(f"UP2_2025_COUNTS:{m25}")
    if m25.get("tau") is None or abs(float(m25["tau"])-0.5312265857773989)>1e-10:
        integrity.append(f"UP2_2025_TAU:{m25.get('tau')}")

    if integrity:
        raise RuntimeError("INTEGRITY_FAIL|"+"|".join(integrity))

    train26=external_cases+by_year[2022]+by_year[2023]+by_year[2024]+by_year[2025]
    scored26,m26=up2.score_year(train26,by_year[2026],2026)
    m26["call_error_rate"]=(
        m26["false_up"]/m26["up2_calls"] if m26.get("up2_calls") else None
    )

    combined=combined_alarm_metrics(alarm26,scored26)

    # Write row ledgers.
    fields_primary=[
        "origin_date","target_date","actual_up","sqrt_alert","legacy_bucket",
        "legacy_up_count","TTSM_S2","TTSM_S1","BONATO_AR1_RM_QBOOST_H1",
        "AR1_RM_LOGIT","RM_LOGIT","router_up","selected_expert",
        "selected_lcb","selected_precision","selected_fpr","selected_history_n_up","selected_scope"
    ]
    with (args.out/"GOLD_CONTROL_PRIMARY_UP_V2_2026_LEDGER.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields_primary); w.writeheader()
        for r in primary26:
            w.writerow({k:r.get(k,"") for k in fields_primary})

    fields_up2=[
        "evaluation_year","origin_date","target_date","actual_up",
        *up2.FEATURES,"p_up","tau","up2_call"
    ]
    with (args.out/"GOLD_CONTROL_UP2_2026_LEDGER.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields_up2); w.writeheader()
        for r in scored26:
            w.writerow({k:r.get(k,"") for k in fields_up2})

    result={
        "identity":IDENTITY,
        "date":"2026-10-02",
        "period":"2026 through 2026-08-31",
        "parent_2026":{
            "n":len(p26),"sqrt_high_risk_alarms":len(a26),
            "alarm_actual_up":sum(p["actual_up"] for p in a26),
            "alarm_actual_down":sum(1-p["actual_up"] for p in a26),
        },
        "primary_up_v2_standalone_2026":primary26_metrics,
        "primary_up_v2_inside_sqrt_2026":primary26_alarm_metrics,
        "up2_residual_2026":m26,
        "combined_positive_up_cascade_inside_sqrt_2026":combined,
        "integrity":{
            "passed":True,
            "primary_2024_reproduced":True,
            "primary_2025_reproduced":True,
            "up2_2022_2024_reproduced":True,
            "up2_2025_reproduced":True,
            **extdiag,
        },
        "governance":{
            "2026_used_for_tuning":False,
            "frozen_rules_changed":False,
            "production_writes":False,
            "runtime_promotion":False,
        }
    }
    (args.out/"GOLD_CONTROL_UP_CASCADE_2026_REPLAY_V1_RESULT_2026-10-02.json").write_text(
        json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8"
    )

    p=primary26_metrics; pa=primary26_alarm_metrics; u=m26; c=combined
    lines=[
        "# GOLD CONTROL — FROZEN UP CASCADE 2026 REPLAY V1 RESULT","",
        "**Period:** 2026 observed stress through 2026-08-31.  ",
        "**Rules:** frozen; no 2026 tuning.","",
        "## Primary UP Verifier V2 — standalone 2026","",
        "| Timeline | UP calls | True UP | False UP | Precision | Call-error | False-UP FPR | UP recall | Coverage |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| {p['n']} | {p['up_calls']} | {p['true_up']} | {p['false_up']} | {100*p['up_precision']:.2f}% | {100*p['call_error_rate']:.2f}% | {100*p['false_up_fpr']:.2f}% | {100*p['actual_up_recall']:.2f}% | {100*p['coverage']:.2f}% |",
        "",
        f"Selected experts: \`{json.dumps(p['selected_counts'],sort_keys=True)}\`.","",
        "## Primary UP Verifier V2 inside SQRT HIGH RISK","",
        f"148 alarms = 74 actual UP + 74 actual DOWN. Primary emits {pa['up_calls']} UP calls: "
        f"{pa['true_up']} true + {pa['false_up']} false; precision {100*pa['up_precision']:.2f}%.","",
        "## One-Sided UP-2 on Primary residual","",
        "| Residual n | Actual UP | Actual DOWN | UP2 calls | True UP | False UP | Precision | Call-error | Recall | FPR | AUC | Tau |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| {u['n']} | {u['actual_up']} | {u['actual_down']} | {u['up2_calls']} | {u['true_up']} | {u['false_up']} | {100*u['up_precision']:.2f}% | {100*u['call_error_rate']:.2f}% | {100*u['missed_up_recall']:.2f}% | {100*u['false_up_fpr']:.2f}% | {u['auc']:.4f} | {u['tau']:.6f} |",
        "",
        "## Combined positive-UP cascade inside SQRT HIGH RISK","",
        "| Calls | True UP | False UP | Precision | Call-error | False-UP FPR | Actual-UP recall | Coverage | Remaining residual | Remaining UP/DOWN |",
        "|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
        f"| {c['positive_up_calls']} | {c['true_up']} | {c['false_up']} | {100*c['up_precision']:.2f}% | {100*c['call_error_rate']:.2f}% | {100*c['false_up_fpr']:.2f}% | {100*c['actual_up_recall']:.2f}% | {100*c['coverage']:.2f}% | {c['remaining_hard_residual_n']} | {c['remaining_actual_up']}/{c['remaining_actual_down']} |",
        "",
        "Historical frozen checkpoints were reproduced before the 2026 metrics were accepted.",
        "ABSTAIN remains UNCERTAIN; no DOWN authority is inferred."
    ]
    (args.out/"GOLD_CONTROL_UP_CASCADE_2026_REPLAY_V1_RESULT_2026-10-02.md").write_text(
        "\n".join(lines)+"\n",encoding="utf-8"
    )
    print((args.out/"GOLD_CONTROL_UP_CASCADE_2026_REPLAY_V1_RESULT_2026-10-02.md").read_text())
    return 0

if __name__=="__main__":
    raise SystemExit(main())
