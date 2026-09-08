from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import pandas as pd
import psycopg

from gold_axis_2026.tools import market_shock_challenger_v1 as v1
from gold_axis_2026.tools import market_shock_unified_replay_v1 as market_unified
from gold_axis_2026.tools import emergency_intraday_replay_validation_v146 as emergency

EXPECTED_RUN_ID = 34173429840
EXPECTED_MARKET = {
    "rows": 482734,
    "first_ts": "2020-04-06T00:00:00+00:00",
    "last_ts": "2026-08-31T23:55:00+00:00",
    "segments": {
        2024: {"signal_bars": 2, "episodes": 2},
        2025: {"signal_bars": 110, "episodes": 80},
        2026: {"signal_bars": 187, "episodes": 108},
    },
    "min_2pct_power": 0.9433333333333334,
    "max_rate": 0.00268381244887122,
}
EXPECTED_EMERGENCY = {
    "months_requested_with_anchor": 43,
    "months_retrieved": 43,
    "observed_minutes": 1393783,
    "level_episodes": 1030,
    "reversal_alert_episodes": 848,
    "reversal_alert_rows": 225982,
    "cross_through_transitions": 7,
    "cross_through_without_expected_alert": 0,
    "zero_observation_months": [],
}


def _db_url() -> str:
    v=os.environ.get("NEON_DATABASE_URL","").strip()
    if not v:
        raise RuntimeError("NEON_DATABASE_URL is not set")
    return v


class CacheFiveMinuteClient:
    def earliest(self):
        with psycopg.connect(_db_url()) as conn, conn.cursor() as cur:
            cur.execute("select min(observation_ts) from xau_intraday_research_cache_5m")
            x=cur.fetchone()[0]
            return x.isoformat() if x else None

    def history(self, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
        with psycopg.connect(_db_url()) as conn, conn.cursor() as cur:
            cur.execute("""
              select observation_ts, close
              from xau_intraday_research_cache_5m
              where observation_ts between %s and %s
              order by observation_ts
            """, (start.to_pydatetime(), end.to_pydatetime()))
            rows=cur.fetchall()
        return pd.DataFrame({"ts":[pd.Timestamp(r[0]) for r in rows],"close":[float(r[1]) for r in rows]})


def _cache_fetch_month(_session, month: str):
    start,end=emergency._month_bounds(month)
    with psycopg.connect(_db_url()) as conn, conn.cursor() as cur:
        cur.execute("""
          select observation_ts, close
          from xau_intraday_research_cache_1m
          where observation_ts between %s and %s
          order by observation_ts
        """, (start.to_pydatetime(), end.to_pydatetime()))
        rows=cur.fetchall()
    return [(pd.Timestamp(r[0]), float(r[1])) for r in rows], 0


def _cache_earliest(_session):
    with psycopg.connect(_db_url()) as conn, conn.cursor() as cur:
        cur.execute("select min(observation_ts) from xau_intraday_research_cache_1m")
        x=cur.fetchone()[0]
    return x.isoformat() if x else None


def _run_market(path: Path) -> int:
    original=v1.TwelveClient
    try:
        v1.TwelveClient=CacheFiveMinuteClient
        argv=sys.argv[:]
        sys.argv=["market_shock_unified_replay_v1.py","--start","2020-04-06 00:00:00","--end","2026-08-31 23:59:59","--output",str(path)]
        rc=market_unified.main()
        sys.argv=argv
    finally:
        v1.TwelveClient=original
    report=json.loads(path.read_text())
    report["input_source"]="NEON_RESEARCH_CACHE"
    report["cache_tables"]=["xau_intraday_research_cache_5m"]
    report["provider_requests_this_replay"]=0
    path.write_text(json.dumps(report,indent=2,sort_keys=True))
    return rc


def _run_emergency(json_path: Path, csv_path: Path) -> int:
    orig_session=emergency._session
    orig_earliest=emergency._earliest_timestamp
    orig_fetch=emergency._fetch_month
    try:
        emergency._session=lambda: None
        emergency._earliest_timestamp=_cache_earliest
        emergency._fetch_month=_cache_fetch_month
        argv=sys.argv[:]
        sys.argv=["emergency_intraday_replay_validation_v146.py","--start-month","2023-01","--end-month","2026-07","--output-json",str(json_path),"--output-csv",str(csv_path)]
        rc=emergency.main()
        sys.argv=argv
    finally:
        emergency._session=orig_session
        emergency._earliest_timestamp=orig_earliest
        emergency._fetch_month=orig_fetch
    report=json.loads(json_path.read_text())
    report["input_source"]="NEON_RESEARCH_CACHE"
    report["cache_tables"]=["xau_intraday_research_cache_1m"]
    report["provider_requests_this_replay"]=0
    json_path.write_text(json.dumps(report,indent=2,sort_keys=True))
    return rc


def _equivalence(m: dict, e: dict) -> dict:
    checks=[]
    def ck(name, actual, expected, tol=0.0):
        ok = abs(actual-expected) <= tol if isinstance(actual,(int,float)) and isinstance(expected,(int,float)) else actual==expected
        checks.append({"check":name,"status":"PASS" if ok else "FAIL","actual":actual,"expected":expected})
    ck("MARKET_ROWS",m["history"]["rows"],EXPECTED_MARKET["rows"])
    ck("MARKET_FIRST_TS",m["history"]["first_ts"],EXPECTED_MARKET["first_ts"])
    ck("MARKET_LAST_TS",m["history"]["last_ts"],EXPECTED_MARKET["last_ts"])
    seg={int(x["year"]):x["consensus"] for x in m["segments"]}
    for year,exp in EXPECTED_MARKET["segments"].items():
        ck(f"MARKET_{year}_SIGNAL_BARS",seg[year]["signal_bars"],exp["signal_bars"])
        ck(f"MARKET_{year}_EPISODES",seg[year]["episodes"],exp["episodes"])
    ck("MARKET_MIN_2PCT_POWER",m["gates"]["MIN_2PCT_SYNTHETIC_CONSENSUS_POWER"],EXPECTED_MARKET["min_2pct_power"],1e-12)
    ck("MARKET_MAX_RATE",m["gates"]["MAX_HISTORICAL_CONSENSUS_BAR_RATE"],EXPECTED_MARKET["max_rate"],1e-15)
    for k,v in EXPECTED_EMERGENCY.items():
        ck(f"EMERGENCY_{k.upper()}",e["aggregate"][k],v)
    return {
      "contract":"GOLD_CONTROL_XAU_INTRADAY_CACHE_REPLAY_EQUIVALENCE_V1",
      "baseline_api_run_id":EXPECTED_RUN_ID,
      "baseline_head_sha":"61f7b21f54083258be16d4e2acc182979dff1ce2",
      "methodology_changed":False,
      "data_source_execution_changed":"TWELVE_DIRECT_TO_NEON_RESEARCH_CACHE",
      "provider_requests_this_replay":0,
      "checks":checks,
      "status":"PASS" if all(x["status"]=="PASS" for x in checks) else "FAIL",
      "production_promotion":"BLOCKED_RESEARCH_ONLY",
    }


def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--market-json",default="market_shock_cache_replay_v1.json")
    p.add_argument("--emergency-json",default="emergency_cache_replay_v146.json")
    p.add_argument("--emergency-csv",default="emergency_cache_replay_v146_months.csv")
    p.add_argument("--equivalence-json",default="xau_intraday_cache_replay_equivalence_v1.json")
    args=p.parse_args()
    mpath=Path(args.market_json); epath=Path(args.emergency_json); cpath=Path(args.emergency_csv); qpath=Path(args.equivalence_json)
    rc1=_run_market(mpath)
    rc2=_run_emergency(epath,cpath)
    m=json.loads(mpath.read_text()); e=json.loads(epath.read_text())
    eq=_equivalence(m,e)
    qpath.write_text(json.dumps(eq,indent=2,sort_keys=True))
    print(json.dumps(eq,indent=2,sort_keys=True))
    return 0 if rc1==0 and rc2==0 and eq["status"]=="PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
