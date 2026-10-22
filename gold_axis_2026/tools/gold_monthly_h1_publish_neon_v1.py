from __future__ import annotations
"""Explicit append-only Neon writer for independently validated new H=1 forecasts.

On conflict, compare frozen values and source hashes; never silently revise.
Requires GOLD_MONTHLY_DATABASE_URL GitHub Actions SECRET. No GitHub token/DB
password is printed or stored in output artifacts.
"""
import argparse,hashlib,json,os,math,statistics
from datetime import date,datetime,timezone
from pathlib import Path

MODEL_IDS={"CHHHO":"ChHHO_ANFIS","DE_ABC":"RBFNN_DE_ABC"}
SCIENTIFIC_SHA="6abcccf12f8c7d495e259fcf9e781a13df493b55"

def canonical_sha(d):
    return hashlib.sha256(json.dumps(d,sort_keys=True,separators=(",",":"),allow_nan=False).encode()).hexdigest()

def git_blob_bytes(raw):
    return hashlib.sha1(b"blob "+str(len(raw)).encode()+b"\0"+raw).hexdigest()

def monthdate(ym):return date.fromisoformat(ym+"-01")

def certify(bundle_path,forecast_paths):
    b=json.loads(Path(bundle_path).read_text())
    a=dict(b);signed=a.pop("payload_sha256")
    if canonical_sha(a)!=signed:raise RuntimeError("SOURCE_BUNDLE_SHA_CHANGED")
    o=[json.loads(Path(p).read_text()) for p in forecast_paths]
    if sorted(x["model"] for x in o)!=sorted(MODEL_IDS):
        raise RuntimeError("TWO_MAIN_MODEL_RECORDS_REQUIRED")
    for x in o:
        if x["schema"]!="GOLD_MONTHLY_H1_FROZEN_FORWARD_V1":raise RuntimeError("FORWARD_SCHEMA_INVALID")
        if x["target"]!=b["target"] or x["origin"]!=b["origin"]:
            raise RuntimeError("FORECAST_MONTH_MISMATCH")
        if x["target_actual"] is not None:raise RuntimeError("LOOKAHEAD_TARGET_ACTUAL")
        if x["source_bundle_sha256"]!=signed:raise RuntimeError("FORECAST_BUNDLE_SHA_MISMATCH")
        if x["reference_authority"]!="STAKTRAKR_PROVISIONAL":
            raise RuntimeError("ORIGIN_REFERENCE_NOT_SAFE")
        if x["official_gpr_xls_sha256"]!=b["gpr_meta"][b["origin"]]["source_xls_sha256"]:
            raise RuntimeError("GPR_FILE_SHA_DIFFERENCE")
        if not x["source_data_first_provenance"]["origin_daily_commit_by_cutoff"]:
            raise RuntimeError("ORIGIN_SOURCE_NOT_PROVEN")
        if x["source_data_first_provenance"]["target_month_actual_used"]:
            raise RuntimeError("TARGET_INFORMATION_LEAKAGE")
        if not (x["forecast"]>0 and math.isfinite(x["forecast"]) and x["train_rows"]>=24):
            raise RuntimeError("INVALID_PRICE_OR_TRAINING")
        if canonical_sha(x["input_feature_vector"])!=x["input_feature_sha256"]:
            raise RuntimeError("FEATURE_VECTOR_SHA_CHANGED")
    if o[0]["input_feature_sha256"]!=o[1]["input_feature_sha256"]:
        raise RuntimeError("TWO_MODELS_DIFFERENT_DATA")
    if abs(o[0]["origin_reference"]-o[1]["origin_reference"])>1e-9:
        raise RuntimeError("TWO_MODELS_DIFFERENT_ORIGIN_REFERENCE")
    if len(b["daily_extension_rows"])<250:raise RuntimeError("SOURCE_EXTENSION_TOO_SHORT")
    return b,o

def assert_same(cur,table,key,valcol,expected):
    # Value parity after ON CONFLICT DO NOTHING is mandatory.
    cur.execute(f"SELECT {valcol} FROM gold_monthly_h1.{table} WHERE {key}=%s",(expected[0],))
    row=cur.fetchone()
    if row is None or row[0]!=expected[1]:
        raise RuntimeError(f"DUPLICATE_OR_MUTATED_SOURCE_{table}_{expected[0]}")

def publish(bundle,forecasts):
    db=os.environ.get("GOLD_MONTHLY_DATABASE_URL")
    if not db:raise RuntimeError("SECRET_GOLD_MONTHLY_DATABASE_URL_REQUIRED")
    import psycopg
    from psycopg.types.json import Jsonb
    origin=bundle["origin"];target=bundle["target"]
    g=bundle["gpr_meta"][origin]
    target_day=monthdate(target);origin_day=monthdate(origin)
    lagday=monthdate(g["lag_month"])
    bymetal={m:[] for m in ("Gold","Silver","Platinum","Palladium")}
    for r in bundle["daily_extension_rows"]:
        if r["date"].startswith(origin):
            for metal in bymetal:bymetal[metal].append(float(r[metal]))
    if any(len(v)<18 for v in bymetal.values()):raise RuntimeError("NO_COMPLETE_METAL_MONTH")
    pg_models={"Gold":"AU","Silver":"AG","Platinum":"PT","Palladium":"PD"}
    bhash=bundle["payload_sha256"]
    source_blob=git_blob_bytes(Path(bundle["authority"].get("local_bundle_path","")).read_bytes()) if False else g["source_commit_sha"]
    produced=max(datetime.fromisoformat(x["produced_on_utc"]) for x in forecasts)
    with psycopg.connect(db,connect_timeout=15) as conn:
      with conn.transaction():
       with conn.cursor() as cur:
        cur.execute("SELECT model_id,scientific_commit FROM gold_monthly_h1.model_registry WHERE model_id=ANY(%s)",(list(MODEL_IDS.values()),))
        models=dict(cur.fetchall())
        if models!={mid:SCIENTIFIC_SHA for mid in MODEL_IDS.values()}:
            raise RuntimeError("MODEL_SCIENTIFIC_IDENTITY_CHANGED")
        cur.execute("""INSERT INTO gold_monthly_h1.gpr_pit_vintages
          (target_month,origin_month,required_observation_month,official_commit_sha,
           official_committed_at,forecast_cutoff_at,official_xls_sha256,gpr_lag_value,
           gpr_normalized,official_source_uri,source_presence_verified,numeric_source_verified,
           model_input_hash_verified,imported_source_blob,provenance)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,true,true,false,%s,%s)
           ON CONFLICT (target_month) DO NOTHING""",(
          target_day,origin_day,lagday,g["source_commit_sha"],g["source_committed_at_utc"],
          bundle["origin_cutoff_utc"],g["source_xls_sha256"],g["lag_value"],g["gpr_z"],
          g["official_source_url"],g["source_commit_sha"],
          Jsonb({"bundleSHA256":bhash,"runInputHashVerified":True,
                 "gprHistoricalModelHashProven":False,"originSafe":True})))
        cur.execute("SELECT official_xls_sha256,gpr_lag_value FROM gold_monthly_h1.gpr_pit_vintages WHERE target_month=%s",(target_day,))
        gs=cur.fetchone()
        if gs is None or gs[0]!=g["source_xls_sha256"] or abs(float(gs[1])-g["lag_value"])>1e-10:
            raise RuntimeError("GPR_PIT_ARCHIVE_DRIFT")
        for metal,prices in bymetal.items():
            oid=f"STAK_FWD/{pg_models[metal]}/{origin}/v1"
            val=statistics.mean(prices)
            cur.execute("""INSERT INTO gold_monthly_h1.monthly_metal_observations
              (observation_id,metal,observed_month,monthly_average,price_unit,source_id,
               price_authority,official_as_of,source_sha256,revision,source_metadata)
               VALUES (%s,%s,%s,%s,'USD/oz','STAKTRAKR_PINNED_ORIGIN_FORWARD',
               'STAKTRAKR_PROVISIONAL',%s,%s,1,%s)
               ON CONFLICT (observation_id) DO NOTHING""",(
              oid,pg_models[metal],origin_day,val,bundle["origin_cutoff_utc"],bhash,
              Jsonb({"sourceCommits":bundle["source_commits"],
              "target":target,"sourceAvailableAtOrigin":True,"monthlyDailyRows":len(prices)})))
            cur.execute("SELECT monthly_average,source_sha256 FROM gold_monthly_h1.monthly_metal_observations WHERE observation_id=%s",(oid,))
            x=cur.fetchone()
            if x is None or abs(float(x[0])-val)>1e-8 or x[1]!=bhash:
                raise RuntimeError("METAL_ORIGIN_SOURCE_DRIFT")
        feature_id=f"CURRENT8_ORIGIN_FWD/{target}"
        feature=forecasts[0]["input_feature_vector"]
        feature_sha=forecasts[0]["input_feature_sha256"]
        cur.execute("""INSERT INTO gold_monthly_h1.feature_snapshots
          (feature_id,target_month,origin_month,feature_contract,feature_values,feature_vector_sha256,
           provenance_status,source_commit,input_as_of)
          VALUES(%s,%s,%s,'CURRENT8_MR_VW_GPR_PIT',%s,%s,'MODEL_INPUT_CONFIRMED',%s,%s)
          ON CONFLICT (feature_id) DO NOTHING""",(
         feature_id,target_day,origin_day,Jsonb(feature),feature_sha,SCIENTIFIC_SHA,
         bundle["origin_cutoff_utc"]))
        cur.execute("SELECT feature_vector_sha256,provenance_status FROM gold_monthly_h1.feature_snapshots WHERE feature_id=%s",(feature_id,))
        fr=cur.fetchone()
        if fr!=(feature_sha,"MODEL_INPUT_CONFIRMED"):
            raise RuntimeError("FROZEN_INPUT_VECTOR_DRIFT")
        for x in forecasts:
            mid=MODEL_IDS[x["model"]]
            record_id=f"CURRENT8/{mid}/{target}/PROSPECTIVE_FORWARD/v1"
            cur.execute("""INSERT INTO gold_monthly_h1.forecast_records
              (record_id,model_id,target_month,origin_month,evidence_class,revision,
              forecast_usd_oz,actual_usd_oz,origin_reference_usd_oz,reference_authority,
              produced_on,training_rows,source_commit,source_blob,source_report_uri,
              feature_id,model_input_proven,record_status,input_provenance)
              VALUES(%s,%s,%s,%s,'PROSPECTIVE_FORWARD',1,%s,NULL,%s,'STAKTRAKR_PROVISIONAL',
              %s,%s,%s,%s,%s,%s,'FORWARD_ORIGIN_FEATURE_SHA256_VERIFIED',
              'PENDING_VALIDATION',%s)
              ON CONFLICT (record_id) DO NOTHING""",(
             record_id,mid,target_day,origin_day,x["forecast"],x["origin_reference"],
             datetime.fromisoformat(x["produced_on_utc"]).date(),x["train_rows"],
             SCIENTIFIC_SHA,source_blob,
             "https://github.com/ataullahturgut/sim3-automation/tree/gold-midas-headswap-v1-20260925/gold_axis_2026",
             feature_id,Jsonb({"gprVintage":origin,"source_bundle_sha256":bhash,
             "feature_vector_sha256":feature_sha,"pred_log_return_gold":x["pred_log_return_gold"],
             "publishedAt":x["produced_on_utc"],"originCutoffUtc":x["origin_cutoff_utc"],
             "sourceHistoricalPITFullyVerified":False})))
            cur.execute("SELECT forecast_usd_oz,actual_usd_oz,reference_authority,feature_id FROM gold_monthly_h1.forecast_records WHERE record_id=%s",(record_id,))
            check=cur.fetchone()
            if check is None or abs(float(check[0])-x["forecast"])>1e-8 or check[1] is not None or check[2]!="STAKTRAKR_PROVISIONAL" or check[3]!=feature_id:
                raise RuntimeError("PREDICTION_APPEND_ONLY_CONFLICT")
        batch=f"GOLD_MONTHLY_H1_PROSPECTIVE_{target}_V1"
        digest=canonical_sha({"bundle":bhash,"predictions":[{"model":x["model"],"value":x["forecast"],"feature":x["input_feature_sha256"]} for x in sorted(forecasts,key=lambda v:v["model"])]})
        cur.execute("""INSERT INTO gold_monthly_h1.ingestion_batches
          (batch_id,payload_sha256,archive_schema,source_commit,model_rows,gpr_rows,status,evidence)
          VALUES (%s,%s,'GOLD_MONTHLY_H1_FROZEN_FORWARD_V1',%s,2,1,'VALIDATED_IMPORT',%s)
          ON CONFLICT (batch_id) DO NOTHING""",(batch,digest,SCIENTIFIC_SHA,
             Jsonb({"source_bundle_sha256":bhash,"feature_sha256":feature_sha,
                    "mode":"MONTHLY_PROSPECTIVE_FORWARD", "target":target,
                    "verifiedModelForecasts":2,"originActualUsed":False})))
        cur.execute("SELECT payload_sha256 FROM gold_monthly_h1.ingestion_batches WHERE batch_id=%s",(batch,))
        z=cur.fetchone()
        if z is None or z[0]!=digest:raise RuntimeError("BATCH_REPLAY_CHANGED")
    return {"target":target,"batchId":batch,"forecast_count":2,"gpr_rows":1,
            "feature_sha256":feature_sha,"source_bundle_sha256":bhash}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--bundle",required=True)
    p.add_argument("--chhho",required=True)
    p.add_argument("--de-abc",required=True)
    p.add_argument("--verify-only",action="store_true")
    a=p.parse_args()
    b,ff=certify(a.bundle,[a.chhho,a.de_abc])
    print("GOLD_MONTHLY_TWO_MODEL_PAIR_PARITY_PASS",
          json.dumps({"target":b["target"],"forecast_models":[x["model"] for x in ff],
                      "input_sha256":ff[0]["input_feature_sha256"]}))
    if not a.verify_only:
        print("GOLD_MONTHLY_NEON_PUBLISH_PASS",json.dumps(publish(b,ff),sort_keys=True))

if __name__=="__main__":main()
