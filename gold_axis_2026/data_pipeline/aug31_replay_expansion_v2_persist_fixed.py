from __future__ import annotations

import hashlib
import json
import os
import subprocess
import uuid
from datetime import datetime
from pathlib import Path

import psycopg
from psycopg.rows import dict_row

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE_PATH = ROOT / "stage4b" / "aug31_replay_expansion_v2_evidence.json"
CHANGE_CONTROL = ROOT / "GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_CHANGE_CONTROL_2026-09-04.md"
ENGINEERING = ROOT / "GOLD_CONTROL_AUG31_REPLAY_EXPANSION_V2_ENGINEERING_EVIDENCE_2026-09-04.md"
CONTRACT = CHANGE_CONTROL.name
TARGET = "2026-09"
STATE_AS_OF = "2026-08-31T21:00:00+00:00"
EXPECTED_DIGEST = "sha256:f90a38ba6239931b272a5cff9f631f9bc9bb3c04dbc5ff10ffbf5f4fc4bb9b20"
EXPECTED_DRY_SHA = "f255fbcc7f8e3513242fe9f99cfc380d234dc94e"
VERSION = "AUG31_REPLAY_EXPANSION_V2"

FEATURES = {
    "AUG31_REPLAY_CAUSAL_PATCH_SEPTEMBER_FORECAST": ("CAUSAL_PATCH", "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE", "MONTHLY_H1_EXPERT_REPLAY_REFERENCE"),
    "AUG31_REPLAY_CAUSAL_PATCH_PREDICTED_LOG_RETURN": ("CAUSAL_PATCH", "CAUSAL_PATCH_R1_REPRO_V1_6_COMPLETED_SESSION_DAILY_FEATURE_ORIGIN_SAFE", "MONTHLY_H1_EXPERT_REPLAY_REFERENCE"),
    "AUG31_REPLAY_EMERGENCY_LEVEL": ("EMERGENCY_LEVEL", "R4_1_EMERGENCY_LEVEL_REPLAY_V1", "EMERGENCY_CONTEXT_REPLAY"),
    "AUG31_REPLAY_EMERGENCY_REVERSAL": ("EMERGENCY_REVERSAL", "R4_1_EMERGENCY_REVERSAL_REPLAY_V1", "EMERGENCY_CONTEXT_REPLAY"),
    "AUG31_REPLAY_BOCPD_SUCCESSOR_STATE": ("BOCPD", "BOCPD_RETURN_SUCCESSOR_V1", "REGIME_BREAK_SUCCESSOR_REPLAY_CONTEXT"),
    "AUG31_REPLAY_BOCPD_SUCCESSOR_RESET_FRACTION": ("BOCPD", "BOCPD_RETURN_SUCCESSOR_V1", "REGIME_BREAK_SUCCESSOR_REPLAY_CONTEXT"),
}


def h(x) -> str:
    return hashlib.sha256(json.dumps(x, sort_keys=True, separators=(",", ":"), default=str).encode()).hexdigest()


def git_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()


def load_evidence():
    if "FROZEN_BEFORE_AUG31_EXPANSION_RESULT" not in CHANGE_CONTROL.read_text(encoding="utf-8"):
        raise RuntimeError("CHANGE_CONTROL_NOT_FROZEN")
    if "PASS_READ_ONLY_REPLAY_CONSTRUCTION" not in ENGINEERING.read_text(encoding="utf-8"):
        raise RuntimeError("ENGINEERING_EVIDENCE_NOT_FROZEN")
    d = json.loads(EVIDENCE_PATH.read_text(encoding="utf-8"))
    assert d["artifact_digest"] == EXPECTED_DIGEST
    assert d["dry_run_git_commit"] == EXPECTED_DRY_SHA
    assert d["dry_run_workflow_run"] == 33879414201
    assert d["dry_run_pass"] is True
    assert d["target_context"] == TARGET
    assert d["information_cutoff"] == STATE_AS_OF
    assert d["prospective_claim"] is False and d["canonical_authority"] is False
    assert d["patch"]["daily_max_date"] < "2026-08-31"
    assert d["emergency"]["level"] == "NEUTRAL" and d["emergency"]["reversal"] == "OFF"
    assert d["archived_bocpd"]["unchanged"] is True
    return d


def authority(cur):
    out = {}
    for t in ("monthly_forecast_contracts", "decision_signal_snapshots", "decision_runs", "decision_events"):
        cur.execute(f"select count(*)::int n from {t}")
        out[t] = int(cur.fetchone()["n"])
    return out


def runtime(cur):
    cur.execute("select runtime_status,count(*)::int n from latest_engine_runtime_state group by runtime_status")
    c = {str(r["runtime_status"]): int(r["n"]) for r in cur.fetchall()}
    cur.execute("select count(*)::int n from latest_engine_runtime_state where direction_vote_permitted")
    return {"counts": c, "direction_votes": int(cur.fetchone()["n"])}


def expected(d):
    common = {
        "contract": CONTRACT, "historical_replay": True, "prospective_claim": False,
        "current_runtime_authority": False, "canonical_authority": False,
        "auto_selector": "OFF", "auto_ensemble": "OFF", "position_mapping": "NOT_PROVEN_POSITION_MAPPING",
        "target_context": TARGET, "state_as_of": STATE_AS_OF, "replay_executed_at": d["replay_executed_at"],
        "retrieved_post_origin": True, "direction_vote_permitted": False,
        "decision_store_write": "NONE", "canonical_forecast_write": "NONE",
        "artifact_digest": d["artifact_digest"], "engineering_evidence": ENGINEERING.name,
    }
    patch_fp = d["patch"]["input_fingerprint"]
    patch_lin = {"input_fingerprint": patch_fp, "artifact_digest": d["artifact_digest"], "dry_run_git_commit": d["dry_run_git_commit"], "daily_max_date": d["patch"]["daily_max_date"], "source_meta": d["patch"]["source_meta"], "retrieved_post_origin": True}
    emergency_lin = {**patch_lin, "monthly_reference": d["emergency"]["monthly_reference"], "reference_identity": d["emergency"]["reference_identity"]}
    bocpd_fp = h({"context_identity": d["bocpd_successor"]["context_identity"], "source_series": d["bocpd_successor"]["source_series"], "august_daily_level": d["patch"]["august_daily_level"], "prior": d["bocpd_successor"]["prior"], "expected_run_length": 36})
    bocpd_lin = {"input_fingerprint": bocpd_fp, "artifact_digest": d["artifact_digest"], "context_identity": d["bocpd_successor"]["context_identity"], "successor_id": d["bocpd_successor"]["successor_id"], "source_series": d["bocpd_successor"]["source_series"], "source_bridge_used": True, "retrieved_post_origin": True}
    return {
        "AUG31_REPLAY_CAUSAL_PATCH_SEPTEMBER_FORECAST": (float(d["patch"]["forecast"]), None, patch_lin, {**common, "reference_kind": "HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE", "unit": "USD/oz", "forecast_origin": STATE_AS_OF}),
        "AUG31_REPLAY_CAUSAL_PATCH_PREDICTED_LOG_RETURN": (float(d["patch"]["predicted_return"]), None, patch_lin, {**common, "reference_kind": "HISTORICAL_REPLAY_DIAGNOSTIC", "unit": "log_return"}),
        "AUG31_REPLAY_EMERGENCY_LEVEL": (None, "NEUTRAL", emergency_lin, {**common, "reference_kind": "HISTORICAL_REPLAY_MONTH_OPEN_STATE", "reason": d["emergency"]["reason"], "monthly_reference": d["emergency"]["monthly_reference"]}),
        "AUG31_REPLAY_EMERGENCY_REVERSAL": (None, "OFF", emergency_lin, {**common, "reference_kind": "HISTORICAL_REPLAY_MONTH_OPEN_STATE", "reason": d["emergency"]["reason"], "monthly_reference": d["emergency"]["monthly_reference"]}),
        "AUG31_REPLAY_BOCPD_SUCCESSOR_STATE": (None, d["bocpd_successor"]["state"], bocpd_lin, {**common, "reference_kind": "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT", "successor_id": d["bocpd_successor"]["successor_id"], "context_identity": d["bocpd_successor"]["context_identity"], "archived_engine_status": d["archived_bocpd"]["status"], "validation_claim": False, "production_claim": False}),
        "AUG31_REPLAY_BOCPD_SUCCESSOR_RESET_FRACTION": (float(d["bocpd_successor"]["reset_fraction"]), None, bocpd_lin, {**common, "reference_kind": "HISTORICAL_REPLAY_SUCCESSOR_CONTEXT", "successor_id": d["bocpd_successor"]["successor_id"], "map_reset": d["bocpd_successor"]["map_reset"], "map_run": d["bocpd_successor"]["map_run"], "previous_map_run": d["bocpd_successor"]["previous_map_run"], "expected_run_length": 36, "log_return": d["bocpd_successor"]["log_return"], "validation_claim": False, "production_claim": False}),
    }


def existing(cur):
    cur.execute("select id,feature_name,value_num,value_text,input_lineage,metadata from derived_feature_snapshots where feature_name=any(%s) and metadata->>'contract'=%s and metadata->>'target_context'=%s and metadata->>'state_as_of'=%s order by feature_name,id", (list(FEATURES), CONTRACT, TARGET, STATE_AS_OF))
    out = {}
    for r in cur.fetchall():
        n = str(r["feature_name"])
        if n in out: raise RuntimeError(f"DUPLICATE_EXISTING:{n}")
        out[n] = dict(r)
    return out


def verify(rows, specs):
    if not rows: return
    if set(rows) != set(specs): raise RuntimeError(f"PARTIAL_EXISTING:{sorted(rows)}")
    for n,(num,text,lin,meta) in specs.items():
        r=rows[n]
        if r["value_text"] != text: raise RuntimeError(f"TEXT_CONFLICT:{n}")
        if num is None:
            if r["value_num"] is not None: raise RuntimeError(f"NUM_CONFLICT:{n}")
        elif r["value_num"] is None or abs(float(r["value_num"])-num)>1e-12: raise RuntimeError(f"NUM_CONFLICT:{n}")
        if (r["input_lineage"] or {}).get("input_fingerprint") != lin["input_fingerprint"]: raise RuntimeError(f"LINEAGE_CONFLICT:{n}")


def persist(cur, d, specs, sha):
    calc = datetime.fromisoformat(d["replay_executed_at"]); cutoff = datetime.fromisoformat(STATE_AS_OF)
    ids={}; grouped={}
    for n,(num,text,lin,meta) in specs.items():
        cur.execute("insert into derived_feature_snapshots(feature_name,feature_version,calculation_ts,input_cutoff,value_num,value_text,git_commit,input_lineage,quality_status,metadata) values(%s,%s,%s,%s,%s,%s,%s,%s::jsonb,'HISTORICAL_REPLAY',%s::jsonb) returning id", (n,VERSION,calc,cutoff,num,text,sha,json.dumps(lin,sort_keys=True),json.dumps(meta,sort_keys=True)))
        fid=int(cur.fetchone()["id"]); ids[n]=fid; grouped.setdefault(FEATURES[n][0],[]).append(fid)
    runs={}
    for engine,fids in grouped.items():
        names=[n for n,v in FEATURES.items() if v[0]==engine]; version=FEATURES[names[0]][1]; role=FEATURES[names[0]][2]
        fp=h({"engine":engine,"version":version,"feature_fingerprints":sorted(specs[n][2]["input_fingerprint"] for n in names),"state_as_of":STATE_AS_OF})
        if engine=='CAUSAL_PATCH':
            code='HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE_AVAILABLE'; extra={"reference_kind":"HISTORICAL_REPLAY_CURRENT_MONTH_REFERENCE","forecast_value":d["patch"]["forecast"],"unit":"USD/oz","forecast_origin":STATE_AS_OF}
        elif engine in {'EMERGENCY_LEVEL','EMERGENCY_REVERSAL'}:
            code='HISTORICAL_REPLAY_MONTH_OPEN_STATE_AVAILABLE'; extra={"reference_kind":"HISTORICAL_REPLAY_MONTH_OPEN_STATE","emergency_level":"NEUTRAL","emergency_reversal":"OFF","reason":d["emergency"]["reason"],"monthly_reference":d["emergency"]["monthly_reference"]}
        else:
            code='HISTORICAL_REPLAY_SUCCESSOR_CONTEXT_AVAILABLE'; extra={"reference_kind":"HISTORICAL_REPLAY_SUCCESSOR_CONTEXT","successor_id":d["bocpd_successor"]["successor_id"],"successor_state":d["bocpd_successor"]["state"],"context_identity":d["bocpd_successor"]["context_identity"],"archived_engine_status":d["archived_bocpd"]["status"],"validation_claim":False,"production_claim":False}
        md={"contract":CONTRACT,"historical_replay":True,"information_cutoff":STATE_AS_OF,"replay_executed_at":d["replay_executed_at"],"prospective_claim":False,"prospective_h1_claim":False,"current_runtime_authority":False,"canonical_authority":False,"direction_vote_permitted":False,"auto_selector":"OFF","auto_ensemble":"OFF","position_mapping":"NOT_PROVEN_POSITION_MAPPING","decision_store_write":"NONE","canonical_forecast_write":"NONE","artifact_digest":d["artifact_digest"],**extra}
        rid=str(uuid.uuid4())
        cur.execute("insert into engine_execution_runs(run_id,engine_id,engine_version,engine_role,as_of,target_context,evidence_class,runtime_status,status_code,direction_vote_permitted,git_commit,input_fingerprint,metadata) values(%s,%s,%s,%s,%s,%s,'HISTORICAL_REPLAY','ISSUED',%s,false,%s,%s,%s::jsonb)", (rid,engine,version,role,calc,TARGET,code,sha,fp,json.dumps(md,sort_keys=True)))
        for fid in fids: cur.execute("insert into engine_execution_derived_outputs(run_id,derived_feature_snapshot_id) values(%s,%s)",(rid,fid))
        runs[engine]=rid
    return ids,runs


def main():
    d=load_evidence(); specs=expected(d); url=os.environ.get('NEON_DATABASE_URL','').strip()
    if not url: raise RuntimeError('NEON_DATABASE_URL_NOT_SET')
    sha=git_sha()
    with psycopg.connect(url,autocommit=False,row_factory=dict_row) as c:
        with c.cursor() as cur:
            cur.execute("select count(distinct trigger_name)::int n from information_schema.triggers where event_object_schema='public' and event_object_table='derived_feature_snapshots' and trigger_name='trg_derived_feature_snapshots_immutable'")
            if int(cur.fetchone()['n'])!=1: raise RuntimeError('IMMUTABILITY_GUARD_MISSING')
            rb=runtime(cur); ab=authority(cur)
            if rb!={'counts':{'ACTIVE':4,'BLOCKED':3,'WAITING':5},'direction_votes':3}: raise RuntimeError(f'RUNTIME_PRECONDITION:{rb}')
            if any(ab.values()): raise RuntimeError(f'AUTHORITY_PRECONDITION:{ab}')
            ex=existing(cur); verify(ex,specs)
            if ex:
                c.rollback(); print('AUG31_REPLAY_EXPANSION_V2_ALREADY_PRESENT_PASS'); return 0
            ids,runs=persist(cur,d,specs,sha)
        c.commit()
    with psycopg.connect(url,autocommit=False,row_factory=dict_row) as c:
        with c.cursor() as cur:
            cur.execute('SET TRANSACTION READ ONLY'); ex=existing(cur); verify(ex,specs)
            cur.execute("select engine_id,count(*)::int n from engine_execution_runs where evidence_class='HISTORICAL_REPLAY' and metadata->>'contract'=%s and metadata->>'information_cutoff'=%s group by engine_id order by engine_id",(CONTRACT,STATE_AS_OF))
            rr={r['engine_id']:r['n'] for r in cur.fetchall()}
            if rr!={'BOCPD':1,'CAUSAL_PATCH':1,'EMERGENCY_LEVEL':1,'EMERGENCY_REVERSAL':1}: raise RuntimeError(f'RUN_LINK_FAIL:{rr}')
            ra=runtime(cur); aa=authority(cur)
            if ra!=rb: raise RuntimeError(f'OPERATIONAL_RUNTIME_CHANGED:{rb}:{ra}')
            if aa!=ab: raise RuntimeError(f'AUTHORITY_CHANGED:{ab}:{aa}')
        c.rollback()
    print(json.dumps({'status':'AUG31_REPLAY_EXPANSION_V2_PERSIST_PASS','feature_ids':ids,'run_ids':runs,'runtime':ra,'authority':aa},sort_keys=True)); return 0

if __name__=='__main__':
    raise SystemExit(main())
