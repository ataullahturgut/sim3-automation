from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pandas as pd
import psycopg

ROOT=Path(__file__).resolve().parents[2]
AX=ROOT/"gold_axis_2026"
OUT=AX/"MACRO_EVENT_LEDGER_RAW_V1_OUT"; OUT.mkdir(exist_ok=True)

WGC=AX/"GOLD_SESSION_TARGETS_WGC2026_NY3_FINAL_V5_2023_2025.csv"
SOB=AX/"GOLD_SESSION_TARGETS_SOBTI5_ET_FINAL_V5_2023_2025.csv"

PAIRS={
 "CPI":("MACRO_CPI_ACTUAL_FIRST_PRINT","MACRO_CPI_CONSENSUS_PIT"),
 "NFP":("MACRO_NFP_ACTUAL_FIRST_PRINT","MACRO_NFP_CONSENSUS_PIT"),
 "UNEMP":("MACRO_UNEMP_ACTUAL_FIRST_PRINT","MACRO_UNEMP_CONSENSUS_PIT"),
 "AHE":("MACRO_AHE_ACTUAL_FIRST_PRINT","MACRO_AHE_CONSENSUS_PIT"),
}
FOMC_SERIES="MACRO_EVENT_V3_FOMC_SCORE"

def sha(p):
    h=hashlib.sha256()
    with p.open("rb") as f:
        for b in iter(lambda:f.read(1<<20),b""):h.update(b)
    return h.hexdigest()

def load_obs(series_ids):
    dsn=os.environ["NEON_DATABASE_URL"]
    with psycopg.connect(dsn,autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            cur.execute("""
              SELECT series_id,observation_ts,value,available_as_of,retrieved_at,lineage_id
              FROM observations
              WHERE series_id = ANY(%s)
                AND observation_ts >= '2023-01-01'
                AND observation_ts < '2026-01-01'
              ORDER BY observation_ts,series_id,retrieved_at
            """,(list(series_ids),))
            rows=cur.fetchall()
        conn.rollback()
    q=pd.DataFrame(rows,columns=["series_id","event_ts_utc","value","available_as_of","retrieved_at","lineage_id"])
    for c in ["event_ts_utc","available_as_of","retrieved_at"]:
        q[c]=pd.to_datetime(q[c],utc=True)
    q["value"]=pd.to_numeric(q.value,errors="raise")
    return q

def newest_vintage_per_event(q):
    # Preserve PIT fields; if duplicate retrievals exist, use the latest stored copy only
    # when their economic event/value/available_as_of are identical. Otherwise fail closed.
    key=["series_id","event_ts_utc"]
    bad=[]
    for k,g in q.groupby(key):
        if g.value.nunique(dropna=False)>1 or g.available_as_of.nunique(dropna=False)>1:
            bad.append((k,len(g),g.value.tolist(),g.available_as_of.astype(str).tolist()))
    if bad:
        raise RuntimeError(f"EVENT_VINTAGE_CONFLICT n={len(bad)} sample={bad[:5]}")
    return q.sort_values("retrieved_at").drop_duplicates(key,keep="last").reset_index(drop=True)

def build_ledger(q):
    rows=[]
    for kind,(act,con) in PAIRS.items():
        a=q[q.series_id==act].copy()
        c=q[q.series_id==con].copy()
        z=a.merge(c,on="event_ts_utc",how="outer",suffixes=("_actual","_cons"),indicator=True)
        for r in z.itertuples(index=False):
            both=r._merge=="both"
            actual=float(r.value_actual) if both and pd.notna(r.value_actual) else None
            consensus=float(r.value_cons) if both and pd.notna(r.value_cons) else None
            # The event surprise is not usable before both source records are available.
            ready=max(r.available_as_of_actual,r.available_as_of_cons) if both else pd.NaT
            rows.append({
              "event_type":kind,
              "event_ts_utc":r.event_ts_utc,
              "actual":actual,
              "consensus":consensus,
              "surprise":None if actual is None or consensus is None else actual-consensus,
              "actual_available_as_of_utc":r.available_as_of_actual if both else pd.NaT,
              "consensus_available_as_of_utc":r.available_as_of_cons if both else pd.NaT,
              "surprise_ready_at_utc":ready,
              "pair_complete":bool(both),
              "actual_lineage_id":r.lineage_id_actual if both else None,
              "consensus_lineage_id":r.lineage_id_cons if both else None,
              "pit_use":"POST_RELEASE_ONLY"
            })
    # FOMC score is useful for event timestamp discovery only because its historical
    # available_as_of is the 2026 reconstruction/load time, not the event time.
    f=q[q.series_id==FOMC_SERIES].copy()
    for r in f.itertuples(index=False):
        rows.append({
          "event_type":"FOMC",
          "event_ts_utc":r.event_ts_utc,
          "actual":None,"consensus":None,"surprise":None,
          "actual_available_as_of_utc":pd.NaT,
          "consensus_available_as_of_utc":pd.NaT,
          "surprise_ready_at_utc":pd.NaT,
          "pair_complete":False,
          "actual_lineage_id":r.lineage_id,
          "consensus_lineage_id":None,
          "pit_use":"EVENT_TIMESTAMP_ONLY_SCORE_VALUE_NOT_HISTORICAL_PIT"
        })
    out=pd.DataFrame(rows).sort_values(["event_ts_utc","event_type"]).reset_index(drop=True)
    return out

def session_map(ledger):
    frames=[]
    for p in [WGC,SOB]:
        q=pd.read_csv(p)
        q=q[q.final_trainable.astype(str).str.lower().eq("true")].copy()
        frames.append(q)
    t=pd.concat(frames,ignore_index=True)
    t["start_utc"]=pd.to_datetime(t.start_utc,utc=True)
    t["end_utc"]=pd.to_datetime(t.end_utc,utc=True)
    e=ledger.copy()
    e["event_ts_utc"]=pd.to_datetime(e.event_ts_utc,utc=True)
    e["surprise_ready_at_utc"]=pd.to_datetime(e.surprise_ready_at_utc,utc=True)

    rows=[]
    for r in t.itertuples(index=False):
        same=e[(e.event_ts_utc>=r.start_utc)&(e.event_ts_utc<r.end_utc)]
        pre=e[(e.event_ts_utc<r.start_utc)&(e.event_ts_utc>=r.start_utc-pd.Timedelta(days=2))]
        ready_pre=e[
            e.surprise_ready_at_utc.notna()
            & (e.surprise_ready_at_utc<=r.start_utc)
            & (e.event_ts_utc>=r.start_utc-pd.Timedelta(days=2))
        ]
        rows.append({
          "label_date":r.label_date,"partition":r.partition,"window":r.window,
          "target_start_utc":r.start_utc.isoformat(),"target_end_utc":r.end_utc.isoformat(),
          "events_inside_target":"|".join(same.event_type.astype(str).tolist()),
          "event_ts_inside_target":"|".join(same.event_ts_utc.astype(str).tolist()),
          "recent_prestart_events":"|".join(pre.event_type.astype(str).tolist()),
          "postrelease_surprises_ready_at_start":"|".join(ready_pre.event_type.astype(str).tolist()),
          "n_events_inside_target":int(len(same)),
          "n_surprises_ready_at_start":int(len(ready_pre))
        })
    return pd.DataFrame(rows)

def main():
    ids=set([FOMC_SERIES])
    for a,c in PAIRS.values(): ids.update([a,c])
    raw=newest_vintage_per_event(load_obs(ids))
    ledger=build_ledger(raw)
    smap=session_map(ledger)

    raw.to_csv(OUT/"raw_observations.csv",index=False)
    ledger.to_csv(OUT/"event_ledger.csv",index=False)
    smap.to_csv(OUT/"session_event_availability_map.csv",index=False)

    pair_summary={}
    for kind in list(PAIRS)+["FOMC"]:
        g=ledger[ledger.event_type==kind]
        pair_summary[kind]={
          "rows":int(len(g)),
          "first":None if g.empty else str(g.event_ts_utc.min()),
          "last":None if g.empty else str(g.event_ts_utc.max()),
          "pair_complete":int(g.pair_complete.sum()),
          "pit_surprise_ready":int(g.surprise_ready_at_utc.notna().sum()),
          "pit_use":sorted(g.pit_use.unique().tolist())
        }
    # Detect families explicitly absent from source inventory for governance.
    summary={
      "status":"MACRO_EVENT_LEDGER_RAW_V1_COMPLETE_PARTIAL_FAMILY_COVERAGE",
      "period":"2023-2025",
      "families":pair_summary,
      "absent_required_families":["PCE","JOLTS","ADP"],
      "rules":{
        "actual_consensus":"use source available_as_of; surprise ready=max(actual,consensus available_as_of)",
        "full_session":"same-session release cannot be used if surprise_ready_at > target_start",
        "fomc":"event timestamp usable; reconstructed FOMC score value not historical PIT because available_as_of is 2026 load time"
      },
      "hashes":{
        "raw_observations":sha(OUT/"raw_observations.csv"),
        "event_ledger":sha(OUT/"event_ledger.csv"),
        "session_event_availability_map":sha(OUT/"session_event_availability_map.csv")
      },
      "guardrail":"PCE/JOLTS/ADP are not silently synthesized. Any model requiring them remains blocked until raw timestamped actual/consensus history is governed."
    }
    (OUT/"summary.json").write_text(json.dumps(summary,indent=2,default=str)+"\n")
    print(json.dumps(summary,indent=2,default=str))

if __name__=="__main__":main()
