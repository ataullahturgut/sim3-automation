from __future__ import annotations
import json, os, time
from pathlib import Path
import requests

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"DATA_AVAILABILITY_GATE_OUT"; OUT.mkdir(exist_ok=True)

TD="https://api.twelvedata.com/time_series"

def probe(symbol, interval, start, end):
    key=os.environ.get("TWELVE_DATA_API_KEY","").strip()
    p={"symbol":symbol,"interval":interval,"start_date":start,"end_date":end,
       "timezone":"America/New_York","order":"ASC","apikey":key}
    r=requests.get(TD,params=p,timeout=90)
    try:j=r.json()
    except Exception:j={"raw":r.text[:500]}
    vals=j.get("values") if isinstance(j,dict) else None
    return {
      "symbol":symbol,"interval":interval,"start":start,"end":end,
      "http":r.status_code,"rows":len(vals) if vals else 0,
      "first":vals[0].get("datetime") if vals else None,
      "last":vals[-1].get("datetime") if vals else None,
      "message":j.get("message") if isinstance(j,dict) else None
    }

def main():
    tests=[]
    windows=[
      ("2023","2023-06-12 00:00:00","2023-06-14 23:59:59"),
      ("2024","2024-06-10 00:00:00","2024-06-12 23:59:59"),
      ("2025","2025-06-09 00:00:00","2025-06-11 23:59:59"),
      ("2026","2026-06-08 00:00:00","2026-06-10 23:59:59"),
    ]
    for year,a,b in windows:
      for interval in ["15min","1h"]:
        x=probe("XAU/USD",interval,a,b); x["year"]=year; tests.append(x); time.sleep(8)
    # Minimal session-context probes: one representative recent date for major FX clocks.
    for sym in ["EUR/USD","USD/JPY","GBP/USD"]:
      x=probe(sym,"15min","2025-06-09 00:00:00","2025-06-10 23:59:59"); x["year"]="2025"; tests.append(x); time.sleep(8)
    summary={
      "status":"DATA_AVAILABILITY_GATE_PROBE",
      "twelve_data_tests":tests,
      "internal_authority":{
        "xau_1h_registered_2022_2024_rows":17644,
        "xau_1h_2025_2026_recent_chunk_fetch":"PASS_IN_EXECUTION_AUDITS",
        "xau_15m_2026_aug_sep":"PASS_IN_INTRADAY_WINDOW_SCAN",
        "databento_glbx_mdp3_access":"PASS_COST_AND_SYMBOLOGY_PROBE",
        "databento_historical_coverage":"2010_PLUS_DOC_CONFIRMED",
        "lbma_continuous_otc_intraday":"NOT_IN_REPO",
        "sge_intraday_history":"NOT_IN_REPO",
        "macro_us_event_calendar":"PARTIAL_RESEARCH_LEDGER_EXISTS",
        "historical_consensus_surprises":"PARTIAL_NOT_GOVERNED_FULL_HISTORY",
        "europe_china_event_consensus":"NOT_GOVERNED"
      },
      "gate_rule":"Do not design session-specific models until the required price/event series pass historical coverage and timestamp provenance."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(json.dumps(summary,indent=2))
if __name__=="__main__":main()
