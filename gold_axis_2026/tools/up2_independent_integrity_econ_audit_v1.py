from __future__ import annotations

import argparse, csv, json, math, os
from collections import defaultdict
from pathlib import Path
import psycopg

TABLE="public.xau_intraday_research_cache_5m"
TZ="America/New_York"
CUTOFF="2026-01-02T05:00:00Z"

def read_csv(path):
    with path.open(newline="",encoding="utf-8") as f:
        return list(csv.DictReader(f))

def db_url():
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL_MISSING")
    return v

def daily_closes():
    sql=f"""
    select
      (observation_ts at time zone '{TZ}')::date as d,
      (array_agg(close::double precision order by observation_ts desc))[1]::double precision as close,
      count(*)::int as n
    from {TABLE}
    where observation_ts >= '2020-01-01'::timestamptz
      and observation_ts < %s::timestamptz
      and extract(isodow from (observation_ts at time zone '{TZ}')) between 1 and 5
    group by 1
    having count(*) >= 240
    order by 1
    """
    with psycopg.connect(db_url(),autocommit=True) as conn:
        with conn.cursor() as cur:
            cur.execute("set default_transaction_read_only = on")
            cur.execute(sql,(CUTOFF,))
            return {d.isoformat():float(c) for d,c,n in cur.fetchall()}

def close(a,b,tol=1e-11):
    return abs(a-b) <= tol*max(1.0,abs(a),abs(b))

def metrics(rows):
    calls=[r for r in rows if r["call"]==1]
    tp=sum(r["actual_up"]==1 for r in calls)
    fp=sum(r["actual_up"]==0 for r in calls)
    au=sum(r["actual_up"]==1 for r in rows)
    ad=len(rows)-au
    fn=au-tp
    tn=ad-fp
    return {
      "n":len(rows),
      "actual_up":au,
      "actual_down":ad,
      "up2_calls":len(calls),
      "true_up":tp,
      "false_up":fp,
      "missed_up":fn,
      "true_down_abstain":tn,
      "up_precision":tp/len(calls) if calls else None,
      "missed_up_recall":tp/au if au else None,
      "false_up_fpr":fp/ad if ad else None,
      "coverage":len(calls)/len(rows) if rows else None,
    }

def econ(rows):
    calls=[r for r in rows if r["call"]==1]
    true=[r for r in calls if r["actual_up"]==1]
    false=[r for r in calls if r["actual_up"]==0]
    abst=[r for r in rows if r["call"]==0]
    mup=[r for r in abst if r["actual_up"]==1]
    mdn=[r for r in abst if r["actual_up"]==0]
    gross_gain=sum(r["simple_db"] for r in true)
    false_loss=sum(-r["simple_db"] for r in false)
    net=sum(r["simple_db"] for r in calls)
    wealth=1.0
    for r in calls:
        wealth*=1.0+r["simple_db"]
    return {
      "calls":len(calls),
      "true_up":len(true),
      "false_up":len(false),
      "gross_true_up_gain_pct":100*gross_gain,
      "gross_false_up_loss_pct":100*false_loss,
      "net_fixed_notional_pnl_pct":100*net,
      "compounded_call_return_pct":100*(wealth-1.0),
      "missed_up_n":len(mup),
      "missed_up_opportunity_pct":100*sum(r["simple_db"] for r in mup),
      "missed_down_n":len(mdn),
      "missed_down_short_opportunity_pct":100*sum(-r["simple_db"] for r in mdn),
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--ledger",type=Path,required=True)
    ap.add_argument("--parent",type=Path,required=True)
    ap.add_argument("--result",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)

    led=read_csv(a.ledger)
    par=read_csv(a.parent)
    frozen=json.loads(a.result.read_text(encoding="utf-8"))
    pmap={(r["origin_date"],r["target_date"]):r for r in par}
    closes=daily_closes()

    errs=[]
    seen=set()
    rows=[]
    max_parent_db_log_diff=0.0
    max_simple_parent_db_diff=0.0

    for r in led:
        key=(r["origin_date"],r["target_date"])
        if key in seen: errs.append(f"DUPLICATE:{key}")
        seen.add(key)
        if not r["origin_date"] < r["target_date"]:
            errs.append(f"NON_CHRONO:{key}")
        p=pmap.get(key)
        if p is None:
            errs.append(f"PARENT_MISSING:{key}"); continue
        if r["origin_date"] not in closes or r["target_date"] not in closes:
            errs.append(f"DB_CLOSE_MISSING:{key}"); continue

        parent_log=float(p["target_close_return"])
        db_log=math.log(closes[r["target_date"]]/closes[r["origin_date"]])
        max_parent_db_log_diff=max(max_parent_db_log_diff,abs(parent_log-db_log))
        if not close(parent_log,db_log,2e-10):
            errs.append(f"PARENT_DB_RETURN_MISMATCH:{key}:{parent_log}:{db_log}")

        actual=int(r["actual_up"])
        if actual != int(parent_log>0):
            errs.append(f"LEDGER_PARENT_LABEL_MISMATCH:{key}")
        if actual != int(db_log>0):
            errs.append(f"LEDGER_DB_LABEL_MISMATCH:{key}")

        pup=float(r["p_up"]); tau=float(r["tau"]); call=int(r["up2_call"])
        if call != int(pup>tau):
            errs.append(f"CALL_RULE_MISMATCH:{key}:{pup}:{tau}:{call}")

        simple_parent=math.exp(parent_log)-1.0
        simple_db=closes[r["target_date"]]/closes[r["origin_date"]]-1.0
        max_simple_parent_db_diff=max(max_simple_parent_db_diff,abs(simple_parent-simple_db))
        rows.append({
          "year":int(r["evaluation_year"]),
          "origin":r["origin_date"],
          "target":r["target_date"],
          "actual_up":actual,
          "call":call,
          "simple_db":simple_db,
        })

    # Frozen result confusion-metric verification.
    for y in (2022,2023,2024):
        m=metrics([r for r in rows if r["year"]==y])
        fm=frozen["by_year_2022_2024"][str(y)]
        for k in ("n","actual_up","actual_down","up2_calls","true_up","false_up","missed_up","true_down_abstain"):
            if m[k] != fm[k]: errs.append(f"METRIC_MISMATCH:{y}:{k}:{m[k]}:{fm[k]}")
        for k in ("up_precision","missed_up_recall","false_up_fpr","coverage"):
            if m[k] is None and fm[k] is None: continue
            if not close(float(m[k]),float(fm[k]),1e-12):
                errs.append(f"METRIC_MISMATCH:{y}:{k}:{m[k]}:{fm[k]}")

    pooled=metrics([r for r in rows if r["year"]<=2024])
    fpool=frozen["pooled_2022_2024"]
    for k in ("n","actual_up","actual_down","up2_calls","true_up","false_up","missed_up","true_down_abstain"):
        if pooled[k] != fpool[k]: errs.append(f"POOL_MISMATCH:{k}:{pooled[k]}:{fpool[k]}")
    for k in ("up_precision","missed_up_recall","false_up_fpr","coverage"):
        if not close(float(pooled[k]),float(fpool[k]),1e-12):
            errs.append(f"POOL_MISMATCH:{k}:{pooled[k]}:{fpool[k]}")

    m25=metrics([r for r in rows if r["year"]==2025])
    f25=frozen["locked_2025"]
    for k in ("n","actual_up","actual_down","up2_calls","true_up","false_up","missed_up","true_down_abstain"):
        if m25[k] != f25[k]: errs.append(f"Y25_MISMATCH:{k}:{m25[k]}:{f25[k]}")
    for k in ("up_precision","missed_up_recall","false_up_fpr","coverage"):
        if not close(float(m25[k]),float(f25[k]),1e-12):
            errs.append(f"Y25_MISMATCH:{k}:{m25[k]}:{f25[k]}")

    economics={str(y):econ([r for r in rows if r["year"]==y]) for y in (2022,2023,2024,2025)}
    economics["2022_2024"]=econ([r for r in rows if r["year"]<=2024])

    result={
      "identity":"UP2_INDEPENDENT_INTEGRITY_ECON_AUDIT_V1_RESEARCH",
      "status":"AUDIT_PASS" if not errs else "AUDIT_FAIL",
      "integrity_errors":errs,
      "ledger_n":len(rows),
      "unique_pairs_n":len(seen),
      "max_abs_parent_vs_db_log_return_diff":max_parent_db_log_diff,
      "max_abs_parent_vs_db_simple_return_diff":max_simple_parent_db_diff,
      "recomputed_metrics":{
        "2022":metrics([r for r in rows if r["year"]==2022]),
        "2023":metrics([r for r in rows if r["year"]==2023]),
        "2024":metrics([r for r in rows if r["year"]==2024]),
        "2025":m25,
        "2022_2024":pooled,
      },
      "independent_db_close_economics":economics,
      "interpretation":{
        "false_up_long_losses_are_realized_under_long_on_UP2_assumption":True,
        "missed_up_down_are_opportunity_costs_if_flat":True,
        "whole_strategy_pnl":False,
        "fees_spread_slippage_leverage_included":False,
      }
    }
    (a.out/"GOLD_CONTROL_UP2_INDEPENDENT_INTEGRITY_ECON_AUDIT_V1_RESULT_2026-09-23.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    print(json.dumps(result,indent=2))
    return 0 if not errs else 2

if __name__=="__main__":
    raise SystemExit(main())
