from __future__ import annotations

"""Macro Event V3 R2 scorer: governed Neon channels only, no provider HTTP."""

import hashlib
import json
import math
import os
import statistics
import subprocess
import uuid
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row

ENGINE="MACRO_EVENT_SUCCESSOR_V3"
PIPELINE_VERSION="MACRO_EVENT_SUCCESSOR_V3_EXISTING_CHANNELS_R2_2026-09-08"
INFLATION_SOURCE_PIPELINE="MACRO_EVENT_SUCCESSOR_V3_INFLATION_EXISTING_CHANNEL_R2_2026-09-08"
EMPLOYMENT_FROZEN_RUN_ID="6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a"
MIN_PRIOR=24
MAD_NORMAL_SCALE=1.4826
IQR_NORMAL_DENOM=1.3489795003921634
STRONG_THRESHOLD=1.0
EMPLOYMENT_IDS={
 "nfp_actual":"MACRO_NFP_ACTUAL_FIRST_PRINT","nfp_consensus":"MACRO_NFP_CONSENSUS_PIT",
 "unemp_actual":"MACRO_UNEMP_ACTUAL_FIRST_PRINT","unemp_consensus":"MACRO_UNEMP_CONSENSUS_PIT",
 "ahe_actual":"MACRO_AHE_ACTUAL_FIRST_PRINT","ahe_consensus":"MACRO_AHE_CONSENSUS_PIT"}
INFLATION_IDS={
 "cpi_actual":"MACRO_CPI_ACTUAL_FIRST_PRINT","cpi_consensus":"MACRO_CPI_CONSENSUS_PIT",
 "core_actual":"MACRO_CORE_CPI_ACTUAL_FIRST_PRINT","core_consensus":"MACRO_CORE_CPI_CONSENSUS_PIT"}
SCORE_IDS={"employment":"MACRO_EVENT_V3_EMPLOYMENT_SCORE","inflation":"MACRO_EVENT_V3_INFLATION_SCORE"}
DECISION_TABLES=("monthly_forecast_contracts","decision_signal_snapshots","decision_runs","decision_events")


def db_url():
 v=os.environ.get("NEON_DATABASE_URL","").strip()
 if not v: raise RuntimeError("NEON_DATABASE_URL_NOT_SET")
 return v


def git_sha():
 try: return subprocess.run(["git","rev-parse","HEAD"],check=True,capture_output=True,text=True,timeout=5).stdout.strip()
 except Exception: return os.environ.get("GITHUB_SHA")


def robust_scale(xs):
 if len(xs)<MIN_PRIOR: return None,None
 med=statistics.median(xs); mad=statistics.median([abs(x-med) for x in xs])
 if mad>1e-12: return MAD_NORMAL_SCALE*mad,"MAD"
 q=statistics.quantiles(xs,n=4,method="inclusive"); iqr=q[2]-q[0]
 if iqr>1e-12: return iqr/IQR_NORMAL_DENOM,"IQR"
 sd=statistics.pstdev(xs)
 if sd>1e-12: return sd,"PSTD_FALLBACK"
 return None,"ZERO_SCALE"


def state_from_score(score,oriented,breadth):
 adverse=sum(x<0 for x in oriented); supportive=sum(x>0 for x in oriented)
 if score<=-STRONG_THRESHOLD and adverse>=breadth: return "GOLD_ADVERSE_MACRO_SHOCK"
 if score>=STRONG_THRESHOLD and supportive>=breadth: return "GOLD_SUPPORTIVE_MACRO_SHOCK"
 return "MACRO_MIXED_OR_SMALL"


def fetch_rows_for_run(conn,run_id,ids):
 with conn.cursor(row_factory=dict_row) as cur:
  cur.execute("""select series_id,observation_ts,value,available_as_of,quality_status,lineage_id,metadata
                 from observations where run_id=%s and series_id=any(%s)
                 order by observation_ts,series_id""",(run_id,list(ids.values())))
  return [dict(x) for x in cur.fetchall()]


def latest_inflation_source_run(conn):
 with conn.cursor(row_factory=dict_row) as cur:
  cur.execute("""select run_id from retrieval_runs where pipeline_version=%s and status='SUCCESS'
                 and observations_written>0 order by finished_at desc limit 1""",(INFLATION_SOURCE_PIPELINE,))
  r=cur.fetchone()
 if not r: raise RuntimeError("INFLATION_EXISTING_CHANNEL_SOURCE_RUN_NOT_FOUND")
 return str(r["run_id"])


def build_panel(rows,ids):
 reverse={v:k for k,v in ids.items()}; by={}
 for r in rows:
  k=reverse.get(r["series_id"])
  if k: by.setdefault(r["observation_ts"],{})[k]=float(r["value"])
 need=set(ids)
 return [{"observation_ts":ts,**v} for ts,v in sorted(by.items()) if set(v)>=need]


def score_employment(panel):
 prior={"nfp":[],"unemp":[],"ahe":[]}; out=[]
 for r in panel:
  e={"nfp":r["nfp_actual"]-r["nfp_consensus"],"unemp":r["unemp_actual"]-r["unemp_consensus"],"ahe":r["ahe_actual"]-r["ahe_consensus"]}
  scales={k:robust_scale(prior[k]) for k in prior}
  if all(scales[k][0] is not None for k in prior):
   z={k:e[k]/float(scales[k][0]) for k in prior}; oriented=[-z["nfp"],z["unemp"],-z["ahe"]]; score=sum(oriented)/3
   out.append({"observation_ts":r["observation_ts"],"score":score,"state":state_from_score(score,oriented,2),
    "components":oriented,"surprises":e,"scale_methods":{k:scales[k][1] for k in prior},"scale_values":{k:scales[k][0] for k in prior}})
  for k in prior: prior[k].append(e[k])
 return out


def score_inflation(panel):
 prior={"cpi":[],"core":[]}; out=[]
 for r in panel:
  e={"cpi":r["cpi_actual"]-r["cpi_consensus"],"core":r["core_actual"]-r["core_consensus"]}
  scales={k:robust_scale(prior[k]) for k in prior}
  if all(scales[k][0] is not None for k in prior):
   z={k:e[k]/float(scales[k][0]) for k in prior}; oriented=[-z["cpi"],-z["core"]]; score=sum(oriented)/2
   out.append({"observation_ts":r["observation_ts"],"score":score,"state":state_from_score(score,oriented,2),
    "components":oriented,"surprises":e,"scale_methods":{k:scales[k][1] for k in prior},"scale_values":{k:scales[k][0] for k in prior}})
  for k in prior: prior[k].append(e[k])
 return out


def decision_counts(conn):
 out={}
 with conn.cursor(row_factory=dict_row) as cur:
  for t in DECISION_TABLES:
   cur.execute(f"select count(*)::bigint n from {t}"); out[t]=int(cur.fetchone()["n"])
 return out


def persist_scores(conn,family,scores,source_run_id,run_id,retrieved):
 sid=SCORE_IDS[family]; inserted=0
 with conn.cursor(row_factory=dict_row) as cur:
  cur.execute("select series_id from source_registry where series_id=%s",(sid,))
  if not cur.fetchone(): raise RuntimeError(f"SCORE_SERIES_NOT_GOVERNED:{sid}")
 for s in scores:
  lineage=f"V3R2_SCORE_{family.upper()}_{s['observation_ts'].strftime('%Y%m%dT%H%M%SZ')}"
  metadata={"engine":ENGINE,"family":family,"state":s["state"],"components":s["components"],"surprises":s["surprises"],
   "scale_methods":s["scale_methods"],"scale_values":s["scale_values"],"source_run_id":source_run_id,
   "evidence_class":"HISTORICAL_REPLAY_RECONSTRUCTION","historical_consensus_pit":"NOT_PROVEN_PROVIDER_UPDATE_TIMESTAMP",
   "context_only":True,"direction_vote":False,"market_shock_threshold_changed":False,"raw_market_shock_episode_changed":False,
   "production_authority":False}
  with conn.cursor(row_factory=dict_row) as cur:
   cur.execute("""select value from observations where series_id=%s and observation_ts=%s and lineage_id=%s
                  order by retrieved_at desc limit 1""",(sid,s["observation_ts"],lineage)); prev=cur.fetchone()
  if prev:
   if not math.isclose(float(prev["value"]),float(s["score"]),rel_tol=0,abs_tol=1e-12):
    raise RuntimeError(f"FROZEN_V3_SCORE_CHANGED:{sid}:{s['observation_ts']}")
   continue
  ph=hashlib.sha256(json.dumps(metadata,sort_keys=True).encode()).hexdigest()
  with conn.cursor() as cur:
   cur.execute("""insert into observations
    (run_id,series_id,observation_ts,value,source,source_symbol,provider_as_of,available_as_of,first_seen_at,retrieved_at,
     frequency,unit,transform,quality_status,lineage_id,payload_hash,metadata)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
    (run_id,sid,s["observation_ts"],s["score"],"Derived from governed Macro Event raw observations",None,
     s["observation_ts"],s["observation_ts"],retrieved,retrieved,"event_monthly","robust_z","ROBUST_EVENT_SURPRISE_SCORE",
     "RESEARCH_CONTEXT_ONLY",lineage,ph,json.dumps(metadata,sort_keys=True)))
  inserted+=1
 return inserted


def main():
 retrieved=datetime.now(timezone.utc); score_run_id=str(uuid.uuid4())
 with psycopg.connect(db_url(),autocommit=False) as conn:
  before=decision_counts(conn)
  emp_rows=fetch_rows_for_run(conn,EMPLOYMENT_FROZEN_RUN_ID,EMPLOYMENT_IDS)
  if len(emp_rows)!=756: raise RuntimeError(f"EMPLOYMENT_FROZEN_SOURCE_ROW_COUNT_DRIFT:{len(emp_rows)}/756")
  emp_panel=build_panel(emp_rows,EMPLOYMENT_IDS)
  if len(emp_panel)!=126: raise RuntimeError(f"EMPLOYMENT_COMPLETE_CASE_DRIFT:{len(emp_panel)}/126")
  inflation_run=latest_inflation_source_run(conn); inf_rows=fetch_rows_for_run(conn,inflation_run,INFLATION_IDS); inf_panel=build_panel(inf_rows,INFLATION_IDS)
  if len(inf_panel)<=MIN_PRIOR: raise RuntimeError(f"INFLATION_COMPLETE_CASES_INSUFFICIENT:{len(inf_panel)}")
  emp_scores=score_employment(emp_panel); inf_scores=score_inflation(inf_panel)

  # FK invariant: retrieval_runs parent must exist before derived observations.
  with conn.cursor() as cur:
   cur.execute("""insert into retrieval_runs
    (run_id,started_at,finished_at,pipeline_version,git_sha,trigger_type,status,observations_read,observations_written,notes,metadata)
    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",
    (score_run_id,retrieved,retrieved,PIPELINE_VERSION,git_sha(),"macro_event_v3_existing_channels_score","SUCCESS",
     len(emp_rows)+len(inf_rows),0,"V3 score transaction parent row; finalized in same transaction",json.dumps({"engine_id":ENGINE,"transaction_state":"PENDING_DERIVED_ROWS"})))

  emp_written=persist_scores(conn,"employment",emp_scores,EMPLOYMENT_FROZEN_RUN_ID,score_run_id,retrieved)
  inf_written=persist_scores(conn,"inflation",inf_scores,inflation_run,score_run_id,retrieved)
  fomc_status="BLOCKED_CME_FEDWATCH_API_NOT_CONFIGURED" if not all(os.environ.get(k,"").strip() for k in
   ("CME_FEDWATCH_API_URL","CME_FEDWATCH_API_KEY","CME_FEDWATCH_SCHEMA_VERSION")) else "BLOCKED_PATH_FACTOR_METHOD_NOT_FROZEN"
  result={"engine_id":ENGINE,"status":"PASS_EMPLOYMENT_INFLATION_EXISTING_CHANNELS_FOMC_BLOCKED",
   "employment":{"source_run_id":EMPLOYMENT_FROZEN_RUN_ID,"raw_events":len(emp_panel),"scored_events":len(emp_scores),"latest":emp_scores[-1] if emp_scores else None},
   "inflation":{"source_run_id":inflation_run,"raw_events":len(inf_panel),"scored_events":len(inf_scores),"latest":inf_scores[-1] if inf_scores else None},
   "fomc":{"status":fomc_status},"model_layer_external_http_calls":False,"market_shock_threshold_changed":False,
   "raw_market_shock_episode_changed":False,"production_authority":False,"evidence_class":"HISTORICAL_REPLAY_RECONSTRUCTION"}
  finished=datetime.now(timezone.utc)
  with conn.cursor() as cur:
   cur.execute("""update retrieval_runs set finished_at=%s,observations_written=%s,notes=%s,metadata=%s::jsonb where run_id=%s""",
    (finished,emp_written+inf_written,"V3 model score from governed Neon channels only; no provider calls; no Market Shock mutation",
     json.dumps(result,sort_keys=True,default=str),score_run_id))
  after=decision_counts(conn)
  if after!=before: raise RuntimeError(f"DECISION_AUTHORITY_STORE_CHANGED:{before}->{after}")
  conn.commit()
 with open("macro_event_successor_v3_existing_channels_r2_result.json","w",encoding="utf-8") as f:
  json.dump(result,f,indent=2,sort_keys=True,default=str)
 print(json.dumps(result,indent=2,sort_keys=True,default=str)); return 0


if __name__=="__main__":
 raise SystemExit(main())
