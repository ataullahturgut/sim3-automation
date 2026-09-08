from __future__ import annotations

import hashlib
import json
import math
import os
import re
import statistics
import time
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import psycopg
import requests
from bs4 import BeautifulSoup
from psycopg.rows import dict_row

ENGINE = "MACRO_EVENT_SUCCESSOR_V3"
PIPELINE_VERSION = "MACRO_EVENT_SUCCESSOR_V3_E2E_R1_2026-09-08"
OUT = Path("macro_event_successor_v3_result.json")
FRED_URL = "https://api.stlouisfed.org/fred/series/observations"
INVESTING_BASE = "https://www.investing.com/economic-calendar/"
INVESTING_FILTERED = INVESTING_BASE + "Service/getCalendarFilteredData"
ET = ZoneInfo("America/New_York")
UTC = timezone.utc
START_YEAR = 2016
MIN_PRIOR = 24
MAD_NORMAL_SCALE = 1.4826
IQR_NORMAL_DENOM = 1.3489795003921634
STRONG_THRESHOLD = 1.0

EMPLOYMENT_IDS = {
    "nfp_actual": "MACRO_NFP_ACTUAL_FIRST_PRINT",
    "nfp_consensus": "MACRO_NFP_CONSENSUS_PIT",
    "unemp_actual": "MACRO_UNEMP_ACTUAL_FIRST_PRINT",
    "unemp_consensus": "MACRO_UNEMP_CONSENSUS_PIT",
    "ahe_actual": "MACRO_AHE_ACTUAL_FIRST_PRINT",
    "ahe_consensus": "MACRO_AHE_CONSENSUS_PIT",
}
INFLATION_IDS = {
    "cpi_actual": "MACRO_CPI_ACTUAL_FIRST_PRINT",
    "cpi_consensus": "MACRO_CPI_CONSENSUS_PIT",
    "core_actual": "MACRO_CORE_CPI_ACTUAL_FIRST_PRINT",
    "core_consensus": "MACRO_CORE_CPI_CONSENSUS_PIT",
}
SCORE_IDS = {
    "EMPLOYMENT": "MACRO_EVENT_V3_EMPLOYMENT_SCORE",
    "INFLATION": "MACRO_EVENT_V3_INFLATION_SCORE",
}
ALFRED_LEVELS = {"cpi": "CPIAUCSL", "core": "CPILFESL"}
INVESTING_IDS = {"CPI (MoM)": "69", "Core CPI (MoM)": "56"}
MONTH_SUFFIX = re.compile(r"\s+\((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\)$")
REF_RE = re.compile(r"Consumer Price Index for ([A-Za-z]+) (\d{4})", re.I)


def utcnow() -> datetime:
    return datetime.now(UTC)


def require_env(name: str) -> str:
    value = os.environ.get(name, "").strip()
    if not value:
        raise RuntimeError(f"{name}_NOT_SET")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json_hash(value: dict) -> str:
    return sha256_bytes(json.dumps(value, sort_keys=True, separators=(",", ":")).encode())


def robust_scale(values: list[float]) -> tuple[float | None, str | None]:
    if len(values) < MIN_PRIOR:
        return None, None
    med = statistics.median(values)
    mad = statistics.median(abs(float(x) - med) for x in values)
    scale = MAD_NORMAL_SCALE * mad
    if math.isfinite(scale) and scale > 0:
        return scale, "MAD"
    xs = sorted(float(x) for x in values)
    def quantile(p: float) -> float:
        pos = (len(xs) - 1) * p
        j = int(math.floor(pos))
        g = pos - j
        return xs[-1] if j >= len(xs) - 1 else xs[j] + g * (xs[j + 1] - xs[j])
    scale = (quantile(.75) - quantile(.25)) / IQR_NORMAL_DENOM
    if math.isfinite(scale) and scale > 0:
        return scale, "IQR"
    return None, None


def state_from_score(score: float, oriented: list[float]) -> str:
    if score <= -STRONG_THRESHOLD and all(x < 0 for x in oriented):
        return "GOLD_ADVERSE_MACRO_SHOCK"
    if score >= STRONG_THRESHOLD and all(x > 0 for x in oriented):
        return "GOLD_SUPPORTIVE_MACRO_SHOCK"
    return "MACRO_MIXED_OR_SMALL"


def source_registry_specs() -> dict[str, dict]:
    return {
        "MACRO_CPI_ACTUAL_FIRST_PRINT": dict(semantic="US CPI headline MoM first print", source="BLS + ALFRED", symbol="CPIAUCSL", tier="AUTHORITY_PUBLIC", frequency="event_monthly", unit="percent_mom", role="MACRO_EVENT_V3_INFLATION_INPUT", status="APPROVED_HISTORICAL_FIRST_PRINT_RECONSTRUCTION_RESEARCH"),
        "MACRO_CORE_CPI_ACTUAL_FIRST_PRINT": dict(semantic="US Core CPI MoM first print", source="BLS + ALFRED", symbol="CPILFESL", tier="AUTHORITY_PUBLIC", frequency="event_monthly", unit="percent_mom", role="MACRO_EVENT_V3_INFLATION_INPUT", status="APPROVED_HISTORICAL_FIRST_PRINT_RECONSTRUCTION_RESEARCH"),
        "MACRO_CPI_CONSENSUS_PIT": dict(semantic="US CPI headline MoM consensus", source="Investing.com Economic Calendar", symbol="event_attr_id=69", tier="RESEARCH_ONLY_DOCTORAL_INTERNAL", frequency="event_monthly", unit="percent_mom", role="MACRO_EVENT_V3_INFLATION_INPUT", status="HISTORICAL_RECONSTRUCTION_NOT_PIT_PROVEN_PROSPECTIVE_CAPTURE_ENABLED"),
        "MACRO_CORE_CPI_CONSENSUS_PIT": dict(semantic="US Core CPI MoM consensus", source="Investing.com Economic Calendar", symbol="event_attr_id=56", tier="RESEARCH_ONLY_DOCTORAL_INTERNAL", frequency="event_monthly", unit="percent_mom", role="MACRO_EVENT_V3_INFLATION_INPUT", status="HISTORICAL_RECONSTRUCTION_NOT_PIT_PROVEN_PROSPECTIVE_CAPTURE_ENABLED"),
        "MACRO_EVENT_V3_EMPLOYMENT_SCORE": dict(semantic="Macro Event V3 Employment gold-context score", source="Derived from governed Macro Event raw observations", symbol=None, tier="DERIVED_RESEARCH", frequency="event_monthly", unit="robust_z", role="MACRO_EVENT_V3_CONTEXT", status="RESEARCH_CONTEXT_ONLY"),
        "MACRO_EVENT_V3_INFLATION_SCORE": dict(semantic="Macro Event V3 Inflation gold-context score", source="Derived from governed Macro Event raw observations", symbol=None, tier="DERIVED_RESEARCH", frequency="event_monthly", unit="robust_z", role="MACRO_EVENT_V3_CONTEXT", status="RESEARCH_CONTEXT_ONLY"),
    }


def upsert_registry(conn) -> None:
    with conn.cursor() as cur:
        for sid, spec in source_registry_specs().items():
            meta = {"engine": ENGINE, "research_only": True, "production_authority": False}
            cur.execute("""
                insert into source_registry
                (series_id,semantic_id,source_name,source_symbol,source_tier,frequency,unit,model_role,status,license_note,metadata)
                values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)
                on conflict(series_id) do update set
                  semantic_id=excluded.semantic_id, source_name=excluded.source_name,
                  source_symbol=excluded.source_symbol, source_tier=excluded.source_tier,
                  frequency=excluded.frequency, unit=excluded.unit, model_role=excluded.model_role,
                  status=excluded.status, metadata=excluded.metadata, updated_at=now()
            """, (sid,spec["semantic"],spec["source"],spec["symbol"],spec["tier"],spec["frequency"],spec["unit"],spec["role"],spec["status"],"research/internal use; no redistribution of provider consensus",json.dumps(meta)))


def get(url: str, **kwargs) -> requests.Response:
    headers = kwargs.pop("headers", {})
    headers.setdefault("User-Agent", "Gold-Control-Macro-Event-V3/1.0")
    last = None
    for i in range(5):
        try:
            r = requests.get(url, headers=headers, timeout=(10, 60), **kwargs)
            if r.status_code == 429:
                time.sleep(3 * (i + 1)); continue
            r.raise_for_status(); return r
        except Exception as exc:
            last = exc
            if i < 4: time.sleep(2 ** i)
    raise RuntimeError(f"HTTP_GET_FAILED:{url}:{type(last).__name__}")


def post(url: str, **kwargs) -> requests.Response:
    last = None
    for i in range(5):
        try:
            r = requests.post(url, timeout=(10, 60), **kwargs)
            if r.status_code == 429:
                time.sleep(3 * (i + 1)); continue
            r.raise_for_status(); return r
        except Exception as exc:
            last = exc
            if i < 4: time.sleep(2 ** i)
    raise RuntimeError(f"HTTP_POST_FAILED:{url}:{type(last).__name__}")


def parse_reference_month(name: str, year: int) -> datetime:
    return datetime.strptime(f"{name} {year}", "%B %Y").replace(day=1, tzinfo=UTC)


def previous_month(dt: datetime) -> datetime:
    y, m = dt.year, dt.month
    return datetime(y - (m == 1), 12 if m == 1 else m - 1, 1, tzinfo=UTC)


def bls_cpi_schedule(start_year: int, end_year: int) -> list[dict]:
    events: dict[str, dict] = {}
    for year in range(start_year, end_year + 1):
        r = get(f"https://www.bls.gov/schedule/{year}/")
        soup = BeautifulSoup(r.text, "html.parser")
        for tr in soup.find_all("tr"):
            cells = [" ".join(td.get_text(" ", strip=True).split()) for td in tr.find_all(["td","th"])]
            joined = " | ".join(cells)
            m = REF_RE.search(joined)
            if not m or len(cells) < 3:
                continue
            date_text = next((x for x in cells if re.search(r"[A-Za-z]+, [A-Za-z]+ \d{1,2}, \d{4}", x)), None)
            time_text = next((x for x in cells if re.fullmatch(r"\d{1,2}:\d{2} (?:AM|PM)", x, re.I)), None)
            if not date_text or not time_text:
                continue
            date_match = re.search(r"([A-Za-z]+, [A-Za-z]+ \d{1,2}, \d{4})", date_text)
            d = datetime.strptime(date_match.group(1), "%A, %B %d, %Y")
            t = datetime.strptime(time_text.upper(), "%I:%M %p")
            release_local = datetime(d.year,d.month,d.day,t.hour,t.minute,tzinfo=ET)
            ref = parse_reference_month(m.group(1), int(m.group(2)))
            key = ref.strftime("%Y-%m")
            events[key] = {"reference_month": key, "release_at": release_local.astimezone(UTC), "release_date": release_local.date().isoformat(), "authority_url": f"https://www.bls.gov/schedule/{year}/"}
        time.sleep(.1)
    return [events[k] for k in sorted(events)]


def fred_asof_level(series_id: str, asof_date: str, start: str, end: str) -> tuple[dict[str,float], str]:
    params = {"series_id":series_id,"api_key":require_env("FRED_API_KEY"),"file_type":"json","realtime_start":asof_date,"realtime_end":asof_date,"observation_start":start,"observation_end":end,"sort_order":"asc","limit":100}
    r = get(FRED_URL, params=params)
    body = r.json(); out = {}
    for row in body.get("observations",[]):
        raw = str(row.get("value","."))
        if raw not in {".","","nan","None"}: out[str(row["date"])] = float(raw)
    return out, sha256_bytes(r.content)


def inflation_actuals(event: dict) -> tuple[dict[str,float], dict[str,str]]:
    ref = datetime.strptime(event["reference_month"]+"-01", "%Y-%m-%d").replace(tzinfo=UTC)
    prev = previous_month(ref)
    s, e = prev.date().isoformat(), ref.date().isoformat()
    vals, hashes = {}, {}
    for name, sid in ALFRED_LEVELS.items():
        d,h = fred_asof_level(sid,event["release_date"],s,e)
        if s not in d or e not in d: raise RuntimeError(f"ALFRED_MISSING:{sid}:{event['reference_month']}")
        vals[name] = round((d[e]/d[s]-1.0)*100.0,1); hashes[name]=h
    return vals, hashes


def inv_headers() -> dict[str,str]:
    return {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/131 Safari/537.36","Accept-Language":"en-US,en;q=0.9","X-Requested-With":"XMLHttpRequest","Referer":INVESTING_BASE,"Origin":"https://www.investing.com"}


def normalize_event_name(text: str) -> str:
    return MONTH_SUFFIX.sub("", " ".join(text.split())).strip()


def parse_provider_number(text: str) -> float | None:
    s = text.strip().replace(",","")
    if not s or s in {"-","--","N/A"}: return None
    if s.endswith("%"): s=s[:-1]
    try: return float(s)
    except ValueError: return None


def investing_defaults(session: requests.Session) -> tuple[str,str]:
    r=session.get(INVESTING_BASE,headers=inv_headers(),timeout=(10,60)); r.raise_for_status()
    soup=BeautifulSoup(r.text,"html.parser"); tz="55"; tf="timeRemain"
    sel=soup.find("select",{"id":"timeZone"})
    if sel:
        opt=sel.find("option",selected=True)
        if opt and opt.get("value"): tz=str(opt["value"])
    chk=soup.find("input",{"name":"timeFilter","checked":True})
    if chk and chk.get("value"): tf=str(chk["value"])
    return tz,tf


def historical_cpi_consensus(release_date: str) -> tuple[dict[str,float], str]:
    session=requests.Session(); tz,tf=investing_defaults(session)
    payload=[("dateFrom",release_date),("dateTo",release_date),("timeZone",tz),("timeFilter",tf),("currentTab","custom"),("submitFilters","1"),("limit_from","0")]
    r=post(INVESTING_FILTERED,data=payload,headers=inv_headers()); body=r.json(); html=str(body.get("data") or "")
    if not html: raise RuntimeError(f"INVESTING_NO_DATA:{release_date}")
    soup=BeautifulSoup(f"<table>{html}</table>","html.parser"); found={}
    for tr in soup.find_all("tr"):
        cell=tr.select_one("td.event")
        if not cell: continue
        name=normalize_event_name(cell.get_text(" ",strip=True))
        if name not in INVESTING_IDS: continue
        attr=str(tr.get("event_attr_id") or tr.get("event_attr_ID") or "")
        if attr != INVESTING_IDS[name]: continue
        fore=tr.select_one("td.fore"); value=parse_provider_number(fore.get_text(" ",strip=True) if fore else "")
        if value is not None: found[name]=value
    if set(found) != set(INVESTING_IDS): raise RuntimeError(f"INVESTING_CPI_INCOMPLETE:{release_date}:{sorted(found)}")
    return found, sha256_bytes(html.encode())


def fetch_existing(conn, series_ids: list[str]) -> list[dict]:
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""select series_id,observation_ts,value,available_as_of,quality_status,lineage_id,payload_hash,metadata from canonical_latest where series_id=any(%s) order by observation_ts,series_id""",(series_ids,))
        return [dict(x) for x in cur.fetchall()]


def build_panel(rows: list[dict], mapping: dict[str,str]) -> list[dict]:
    by={}
    reverse={v:k for k,v in mapping.items()}
    for r in rows:
        k=reverse.get(r["series_id"])
        if k: by.setdefault(r["observation_ts"],{})[k]=float(r["value"])
    need=set(mapping)
    return [{"observation_ts":ts,**v} for ts,v in sorted(by.items()) if set(v)>=need]


def score_employment(panel: list[dict]) -> list[dict]:
    prior={"nfp":[],"unemp":[],"ahe":[]}; out=[]
    for r in panel:
        e={"nfp":r["nfp_actual"]-r["nfp_consensus"],"unemp":r["unemp_actual"]-r["unemp_consensus"],"ahe":r["ahe_actual"]-r["ahe_consensus"]}
        scales={k:robust_scale(prior[k]) for k in prior}
        if all(scales[k][0] is not None for k in prior):
            z={k:e[k]/scales[k][0] for k in prior}; oriented=[-z["nfp"],z["unemp"],-z["ahe"]]; score=sum(oriented)/3
            adverse=sum(x<0 for x in oriented); supportive=sum(x>0 for x in oriented)
            state="GOLD_ADVERSE_MACRO_SHOCK" if score<=-1 and adverse>=2 else "GOLD_SUPPORTIVE_MACRO_SHOCK" if score>=1 and supportive>=2 else "MACRO_MIXED_OR_SMALL"
            out.append({"observation_ts":r["observation_ts"],"score":score,"state":state,"components":oriented,"surprises":e,"scale_methods":{k:scales[k][1] for k in prior},"scale_values":{k:scales[k][0] for k in prior}})
        for k in prior: prior[k].append(e[k])
    return out


def score_inflation(panel: list[dict]) -> list[dict]:
    prior={"cpi":[],"core":[]}; out=[]
    for r in panel:
        e={"cpi":r["cpi_actual"]-r["cpi_consensus"],"core":r["core_actual"]-r["core_consensus"]}
        scales={k:robust_scale(prior[k]) for k in prior}
        if all(scales[k][0] is not None for k in prior):
            z={k:e[k]/scales[k][0] for k in prior}; oriented=[-z["cpi"],-z["core"]]; score=sum(oriented)/2
            out.append({"observation_ts":r["observation_ts"],"score":score,"state":state_from_score(score,oriented),"components":oriented,"surprises":e,"scale_methods":{k:scales[k][1] for k in prior},"scale_values":{k:scales[k][0] for k in prior}})
        for k in prior: prior[k].append(e[k])
    return out


def obs_dict(series_id: str, ts: datetime, value: float, source: str, symbol: str | None, available: datetime, retrieved: datetime, unit: str, quality: str, lineage: str, payload_hash: str, metadata: dict) -> dict:
    return {"series_id":series_id,"observation_ts":ts,"value":value,"source":source,"source_symbol":symbol,"provider_as_of":available,"available_as_of":available,"first_seen_at":retrieved,"retrieved_at":retrieved,"frequency":"event_monthly","unit":unit,"transform":"LEVEL" if "SCORE" not in series_id else "ROBUST_EVENT_SURPRISE_SCORE","quality_status":quality,"lineage_id":lineage,"payload_hash":payload_hash,"metadata":metadata}


def persist_observations(conn, run_id: str, observations: list[dict]) -> tuple[int,int]:
    written=0; skipped=0
    with conn.cursor(row_factory=dict_row) as cur:
        for o in observations:
            cur.execute("""select value,quality_status from canonical_latest where series_id=%s and observation_ts=%s and lineage_id=%s limit 1""",(o["series_id"],o["observation_ts"],o["lineage_id"]))
            prev=cur.fetchone()
            if prev and abs(float(prev["value"])-float(o["value"]))<1e-12 and str(prev["quality_status"])==o["quality_status"]:
                skipped+=1; continue
            cur.execute("""insert into observations(run_id,series_id,observation_ts,value,source,source_symbol,provider_as_of,available_as_of,first_seen_at,retrieved_at,frequency,unit,transform,quality_status,lineage_id,payload_hash,metadata) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb)""",(run_id,o["series_id"],o["observation_ts"],o["value"],o["source"],o["source_symbol"],o["provider_as_of"],o["available_as_of"],o["first_seen_at"],o["retrieved_at"],o["frequency"],o["unit"],o["transform"],o["quality_status"],o["lineage_id"],o["payload_hash"],json.dumps(o["metadata"])))
            written+=1
    return written,skipped


def main() -> int:
    retrieved=utcnow(); run_id=str(uuid.uuid4()); conn=psycopg.connect(require_env("NEON_DATABASE_URL"),autocommit=False)
    result={"engine_id":ENGINE,"pipeline_version":PIPELINE_VERSION,"generated_at":retrieved.isoformat(),"production_authority":False,"market_shock_threshold_changed":False,"raw_market_shock_episode_changed":False}
    try:
        upsert_registry(conn)
        with conn.cursor() as cur:
            cur.execute("""insert into retrieval_runs(run_id,started_at,git_sha,pipeline_version,trigger_type,status,observations_read,observations_written,notes,metadata) values(%s,%s,%s,%s,%s,%s,0,0,%s,%s::jsonb)""",(run_id,retrieved,os.environ.get("GITHUB_SHA"),PIPELINE_VERSION,"macro_event_v3_research_e2e","RUNNING","Employment reuse + Inflation historical reconstruction; research evidence spine only",json.dumps({"engine":ENGINE,"production_write":False})))

        emp_rows=fetch_existing(conn,list(EMPLOYMENT_IDS.values())); emp_panel=build_panel(emp_rows,EMPLOYMENT_IDS); emp_scores=score_employment(emp_panel)
        result["employment"]={"raw_events":len(emp_panel),"scored_events":len(emp_scores),"latest":emp_scores[-1] if emp_scores else None,"historical_consensus_pit":"NOT_PROVEN_PROVIDER_UPDATE_TIMESTAMP","evidence_class":"HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN"}

        schedule=[e for e in bls_cpi_schedule(START_YEAR,retrieved.year) if e["release_at"]<=retrieved]
        inflation_obs=[]; inflation_panel=[]; failures=[]
        for idx,event in enumerate(schedule):
            try:
                actual,ah=inflation_actuals(event); consensus,ch=historical_cpi_consensus(event["release_date"])
                ts=event["release_at"]; base_meta={"engine":ENGINE,"family":"INFLATION","reference_month":event["reference_month"],"official_release_at":ts.isoformat(),"official_schedule_authority":event["authority_url"],"historical_reconstruction_not_original_retrieval":True,"production_authority":False}
                inflation_panel.append({"observation_ts":ts,"cpi_actual":actual["cpi"],"cpi_consensus":consensus["CPI (MoM)"],"core_actual":actual["core"],"core_consensus":consensus["Core CPI (MoM)"]})
                inflation_obs += [
                    obs_dict(INFLATION_IDS["cpi_actual"],ts,actual["cpi"],"Federal Reserve Bank of St. Louis ALFRED / BLS","CPIAUCSL",ts,retrieved,"percent_mom","APPROVED_HISTORICAL_FIRST_PRINT_RECONSTRUCTION_RESEARCH","MACRO_V3_CPI_ACTUAL_ALFRED_BLS_R1",ah["cpi"],{**base_meta,"evidence_class":"HISTORICAL_REPLAY_RECONSTRUCTION","construction_method":"ALFRED_ASOF_OFFICIAL_BLS_RELEASE_DATE_LEVELS_TO_MOM_1DP"}),
                    obs_dict(INFLATION_IDS["core_actual"],ts,actual["core"],"Federal Reserve Bank of St. Louis ALFRED / BLS","CPILFESL",ts,retrieved,"percent_mom","APPROVED_HISTORICAL_FIRST_PRINT_RECONSTRUCTION_RESEARCH","MACRO_V3_CORE_CPI_ACTUAL_ALFRED_BLS_R1",ah["core"],{**base_meta,"evidence_class":"HISTORICAL_REPLAY_RECONSTRUCTION","construction_method":"ALFRED_ASOF_OFFICIAL_BLS_RELEASE_DATE_LEVELS_TO_MOM_1DP"}),
                    obs_dict(INFLATION_IDS["cpi_consensus"],ts,consensus["CPI (MoM)"],"Investing.com Economic Calendar","event_attr_id=69",retrieved,retrieved,"percent_mom","HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN","MACRO_V3_CPI_CONSENSUS_HIST_R1",ch,{**base_meta,"evidence_class":"HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN","provider_field":"Forecast","provider_exact_pre_release_update_timestamp_proven":False,"availability_not_backdated":True}),
                    obs_dict(INFLATION_IDS["core_consensus"],ts,consensus["Core CPI (MoM)"],"Investing.com Economic Calendar","event_attr_id=56",retrieved,retrieved,"percent_mom","HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN","MACRO_V3_CORE_CPI_CONSENSUS_HIST_R1",ch,{**base_meta,"evidence_class":"HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN","provider_field":"Forecast","provider_exact_pre_release_update_timestamp_proven":False,"availability_not_backdated":True}),
                ]
            except Exception as exc:
                failures.append({"reference_month":event["reference_month"],"release_date":event["release_date"],"error":f"{type(exc).__name__}:{exc}"})
            time.sleep(.15)
        inflation_panel.sort(key=lambda x:x["observation_ts"]); inf_scores=score_inflation(inflation_panel)
        for s in inf_scores:
            inflation_obs.append(obs_dict(SCORE_IDS["INFLATION"],s["observation_ts"],s["score"],"Derived Macro Event V3","CPI+CORE_CPI",retrieved,retrieved,"robust_z","HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN","MACRO_V3_INFLATION_SCORE_R1",canonical_json_hash({"ts":s["observation_ts"].isoformat(),"score":s["score"],"state":s["state"]}),{"engine":ENGINE,"family":"INFLATION","state":s["state"],"components":s["components"],"surprises":s["surprises"],"scale_values":s["scale_values"],"scale_methods":s["scale_methods"],"evidence_class":"HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN","macro_confirmed_authority":False,"production_authority":False}))

        emp_score_obs=[]
        for s in emp_scores:
            emp_score_obs.append(obs_dict(SCORE_IDS["EMPLOYMENT"],s["observation_ts"],s["score"],"Derived Macro Event V3","NFP+UNEMP+AHE",retrieved,retrieved,"robust_z","HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN","MACRO_V3_EMPLOYMENT_SCORE_R1",canonical_json_hash({"ts":s["observation_ts"].isoformat(),"score":s["score"],"state":s["state"]}),{"engine":ENGINE,"family":"EMPLOYMENT","state":s["state"],"components":s["components"],"surprises":s["surprises"],"scale_values":s["scale_values"],"scale_methods":s["scale_methods"],"evidence_class":"HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN","macro_confirmed_authority":False,"production_authority":False}))

        w1,s1=persist_observations(conn,run_id,inflation_obs); w2,s2=persist_observations(conn,run_id,emp_score_obs)
        result["inflation"]={"scheduled_past_events":len(schedule),"complete_events":len(inflation_panel),"failed_events":len(failures),"failures":failures[:20],"scored_events":len(inf_scores),"latest":inf_scores[-1] if inf_scores else None,"historical_consensus_pit":"NOT_PROVEN_PROVIDER_UPDATE_TIMESTAMP","evidence_class":"HISTORICAL_REPLAY_RECONSTRUCTION_NOT_PIT_PROVEN"}
        result["fomc"]={"status":"BLOCKED_CME_FEDWATCH_API_NOT_CONFIGURED" if not all(os.environ.get(x) for x in ("CME_FEDWATCH_API_URL","CME_FEDWATCH_API_KEY","CME_FEDWATCH_SCHEMA_VERSION")) else "SOURCE_CONFIGURED_REQUIRES_SEPARATE_TARGET_PATH_INGEST","proxy_substitution":False}
        result["writes"]={"observations_written":w1+w2,"observations_skipped_exact":s1+s2}
        result["run_id"]=run_id
        result["status"]="PASS_EMPLOYMENT_INFLATION_E2E_FOMC_BLOCKED_EXTERNAL_SOURCE" if inflation_panel and emp_scores else "FAIL_E2E"
        with conn.cursor() as cur:
            cur.execute("update retrieval_runs set finished_at=%s,status=%s,observations_read=%s,observations_written=%s,notes=%s,metadata=%s::jsonb where run_id=%s",(utcnow(),"SUCCESS" if result["status"].startswith("PASS") else "FAIL",len(emp_rows)+4*len(inflation_panel),w1+w2,result["status"],json.dumps(result,default=str),run_id))
        conn.commit()
        OUT.write_text(json.dumps(result,indent=2,sort_keys=True,default=str),encoding="utf-8")
        print(json.dumps(result,indent=2,sort_keys=True,default=str))
        return 0 if result["status"].startswith("PASS") else 1
    except Exception as exc:
        conn.rollback(); result["status"]="FAIL_PIPELINE"; result["error"]=f"{type(exc).__name__}:{exc}"; OUT.write_text(json.dumps(result,indent=2,sort_keys=True,default=str),encoding="utf-8"); print(json.dumps(result,indent=2,sort_keys=True,default=str)); return 1
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
