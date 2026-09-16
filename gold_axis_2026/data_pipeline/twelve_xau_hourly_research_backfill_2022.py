from __future__ import annotations

import hashlib
import json
import math
import os
import time
import uuid
from datetime import datetime, timezone

import pandas as pd
import psycopg
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API_URL = "https://api.twelvedata.com/time_series"
SERIES_ID = "XAU_USD_TWELVE_1H_RESEARCH_V1"
SOURCE = "Twelve Data"
SYMBOL = "XAU/USD"
INTERVAL = "1h"
UNIT = "USD_per_troy_ounce"
QUALITY_STATUS = "APPROVED_HISTORICAL_RESEARCH_BACKFILL_NOT_PIT_ISSUED"
PIPELINE_VERSION = "XAU_1H_RESEARCH_BACKFILL_2022_V1_2026-09-16"
START = pd.Timestamp("2022-01-01 00:00:00", tz="UTC")
END = pd.Timestamp("2023-01-01 00:00:00", tz="UTC")
OUTPUTSIZE = 5000


def secret(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise RuntimeError(f"{name}_MISSING")
    return v


def session() -> requests.Session:
    s = requests.Session()
    retry = Retry(total=5, connect=5, read=5, backoff_factor=2.0,
                  status_forcelist=(408,425,429,500,502,503,504),
                  allowed_methods=frozenset(["GET"]), respect_retry_after_header=True)
    s.mount("https://", HTTPAdapter(max_retries=retry))
    s.headers.update({"User-Agent":"GoldControl-XAU1H-Research-2022/1.0","Accept":"application/json"})
    return s


def fmt(ts: pd.Timestamp) -> str:
    return ts.tz_convert("UTC").strftime("%Y-%m-%d %H:%M:%S")


def fetch() -> list[tuple[pd.Timestamp,float,str,str,str]]:
    key = secret("TWELVE_DATA_API_KEY")
    s = session()
    rows = []
    starts = pd.date_range(START, END, freq="QS", inclusive="left")
    for i, st in enumerate(starts, 1):
        en = min(st + pd.DateOffset(months=3), END)
        params = {"symbol":SYMBOL,"interval":INTERVAL,"start_date":fmt(st),
                  "end_date":fmt(en-pd.Timedelta(seconds=1)),"timezone":"UTC",
                  "order":"ASC","outputsize":OUTPUTSIZE,"format":"JSON","apikey":key}
        r = s.get(API_URL, params=params, timeout=(10,60)); r.raise_for_status()
        payload = r.json()
        if isinstance(payload,dict) and payload.get("status") == "error":
            raise RuntimeError(f"TWELVE_API_ERROR:{payload.get('code')}:{payload.get('message')}")
        vals = payload.get("values") if isinstance(payload,dict) else None
        if not vals or len(vals) >= OUTPUTSIZE:
            raise RuntimeError(f"TWELVE_INVALID_CHUNK:{st.date()}:{en.date()}:{0 if not vals else len(vals)}")
        ph = hashlib.sha256(r.content).hexdigest()
        kept = 0
        for x in vals:
            ts = pd.to_datetime(x.get("datetime"), errors="coerce", utc=True)
            val = pd.to_numeric(x.get("close"), errors="coerce")
            if pd.isna(ts) or pd.isna(val):
                continue
            val = float(val)
            if not math.isfinite(val) or val <= 0 or not (st <= ts < en):
                continue
            rows.append((pd.Timestamp(ts), val, ph, fmt(st), fmt(en))); kept += 1
        print(f"FETCH_CHUNK={i} rows={kept} start={st.date()} end_exclusive={en.date()}")
        time.sleep(2)
    by_ts = {}
    for row in rows:
        old = by_ts.get(row[0])
        if old is not None and abs(old[1]-row[1]) > 1e-12:
            raise RuntimeError(f"DUPLICATE_CONFLICT:{row[0].isoformat()}")
        by_ts[row[0]] = row
    out = [by_ts[k] for k in sorted(by_ts)]
    if not out or {x[0].year for x in out} != {2022}:
        raise RuntimeError("YEAR_COVERAGE_MISMATCH")
    print(f"FETCH_COMPLETE rows={len(out)} first={out[0][0].isoformat()} last={out[-1][0].isoformat()} raw_market_values_logged=NO")
    return out


def persist(rows) -> None:
    db = secret("NEON_DATABASE_URL")
    retrieved = datetime.now(timezone.utc)
    run_id = str(uuid.uuid4())
    lineage = hashlib.sha256(f"{SERIES_ID}|{SOURCE}|{SYMBOL}".encode()).hexdigest()[:20]
    with psycopg.connect(db, autocommit=False) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                insert into source_registry
                (series_id,semantic_id,source_name,source_symbol,source_tier,frequency,unit,model_role,status,license_note,metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                on conflict (series_id) do update set
                  metadata=source_registry.metadata || excluded.metadata, updated_at=now()
            """, (SERIES_ID,"XAU_USD_SPOT_HOURLY_RESEARCH",SOURCE,SYMBOL,"RESEARCH_TIER_A","1h",UNIT,
                  "BOCPD intraday research input only","APPROVED_HISTORICAL_RESEARCH_ONLY_NOT_RUNTIME",
                  "Private internal research; raw vendor values must not be publicly redistributed.",
                  json.dumps({"years_requested":[2022,2023,2024],"evidence_class":"HISTORICAL_RESEARCH_BACKFILL","availability_policy":"first_retrieval_floor","historical_publication_timestamp_reconstruction":"NOT_PROVEN"})))
            cur.execute("""
                insert into retrieval_runs
                (run_id,started_at,finished_at,git_sha,pipeline_version,trigger_type,status,observations_read,observations_written,notes,metadata)
                values (%s,%s,%s,%s,%s,%s,'RUNNING',%s,0,%s,%s::jsonb)
            """, (run_id,retrieved,retrieved,os.environ.get("GITHUB_SHA"),PIPELINE_VERSION,
                  "manual_authorized_historical_backfill",len(rows),
                  "Authorized research-only XAU/USD hourly backfill for 2022",
                  json.dumps({"series_id":SERIES_ID,"availability_policy":"first_retrieval_floor","raw_market_values_logged":False})))
            cur.execute("select observation_ts,value,quality_status from canonical_latest where series_id=%s and observation_ts >= timestamptz '2022-01-01' and observation_ts < timestamptz '2023-01-01'", (SERIES_ID,))
            existing = {r[0]:(float(r[1]),str(r[2])) for r in cur.fetchall()}
            ins=[]
            for ts,val,ph,cs,ce in rows:
                tspy=ts.to_pydatetime(); prev=existing.get(tspy)
                if prev is not None:
                    if abs(prev[0]-val) <= 1e-12 and prev[1] == QUALITY_STATUS:
                        continue
                    raise RuntimeError(f"EXISTING_VALUE_CONFLICT:{ts.isoformat()}")
                ins.append((run_id,SERIES_ID,tspy,val,SOURCE,SYMBOL,None,retrieved,retrieved,retrieved,"1h",UNIT,"LEVEL",QUALITY_STATUS,lineage,ph,
                            json.dumps({"interval":"1h","request_timezone":"UTC","chunk_start":cs,"chunk_end":ce,"availability_policy":"first_retrieval_floor","historical_publication_timestamp_reconstruction":"NOT_PROVEN","evidence_class":"HISTORICAL_RESEARCH_BACKFILL","rights_policy":"PRIVATE_INTERNAL_NON_DISPLAY_NO_PUBLIC_RAW_REDISTRIBUTION"})))
            if ins:
                cur.executemany("""
                    insert into observations
                    (run_id,series_id,observation_ts,value,source,source_symbol,provider_as_of,available_as_of,first_seen_at,retrieved_at,frequency,unit,transform,quality_status,lineage_id,payload_hash,metadata)
                    values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                """, ins)
            cur.execute("update retrieval_runs set finished_at=now(),status='SUCCESS',observations_written=%s,metadata=metadata || %s::jsonb where run_id=%s",
                        (len(ins),json.dumps({"deduped_existing_rows":len(rows)-len(ins)}),run_id))
        conn.commit()
    print(f"PERSIST_COMPLETE run_id={run_id} read={len(rows)} written={len(ins)} deduped={len(rows)-len(ins)} lineage={lineage}")


def main():
    rows=fetch(); persist(rows); print("XAU_1H_RESEARCH_BACKFILL_2022_COMPLETE")

if __name__ == "__main__":
    main()
