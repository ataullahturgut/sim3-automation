from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row

import stage4b_patch_v7_first_shadow_issuer as legacy
from multi_expert_forecast import (
    AUTO_ENSEMBLE,
    AUTO_SELECTOR,
    EXPERT_REGISTRY,
    PATCH_EXPERT,
    SELECTOR_STATUS,
    TRACK_MONTH_END,
    ExpertForecastRecord,
)
from multi_expert_forecast_store import insert_expert_forecast, table_exists


EXPERT = EXPERT_REGISTRY[PATCH_EXPERT]
EVIDENCE_CLASS = "PROSPECTIVE_SHADOW"
TARGET_PERIOD = "2026-10"


def expert_ledger_state(url: str) -> dict:
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute("SET TRANSACTION READ ONLY")
            exists = table_exists(cur)
            if not exists:
                conn.rollback()
                return {"table_exists": False, "duplicate": 0, "rows": 0}
            cur.execute("select count(*) as n from monthly_expert_forecasts")
            rows = int(cur.fetchone()["n"])
            cur.execute(
                """
                select count(*) as n from monthly_expert_forecasts
                where target_month=%s and forecast_track=%s and expert_id=%s and model_version=%s
                """,
                (legacy.FIRST_TARGET.date(), TRACK_MONTH_END, PATCH_EXPERT, EXPERT.model_version),
            )
            duplicate = int(cur.fetchone()["n"])
        conn.rollback()
    return {"table_exists": True, "duplicate": duplicate, "rows": rows}


def persist_atomic(url: str, issued_at: datetime, result: dict, sha: str) -> dict:
    """Persist exact Patch inputs + derived feature + individual expert row atomically."""
    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        try:
            with conn.cursor() as cur:
                if not table_exists(cur):
                    raise RuntimeError("BLOCKED_MULTI_EXPERT_LEDGER_SCHEMA_NOT_APPLIED")
                cur.execute(
                    """
                    select id from monthly_expert_forecasts
                    where target_month=%s and forecast_track=%s and expert_id=%s and model_version=%s
                    order by id desc limit 1
                    """,
                    (legacy.FIRST_TARGET.date(), TRACK_MONTH_END, PATCH_EXPERT, EXPERT.model_version),
                )
                existing = cur.fetchone()
                if existing:
                    conn.rollback()
                    return {"duplicate": True, "expert_id": int(existing["id"])}

                ids: list[int] = []
                common = {
                    "expert_id": PATCH_EXPERT,
                    "forecast_track": TRACK_MONTH_END,
                    "evidence_class": EVIDENCE_CLASS,
                    "selector_status": SELECTOR_STATUS,
                    "auto_selector": AUTO_SELECTOR,
                    "auto_ensemble": AUTO_ENSEMBLE,
                    "canonical_authority": False,
                }
                ids.append(legacy.insert_snapshot(
                    cur, issued_at=issued_at, target_period=TARGET_PERIOD, sha=sha,
                    series_id="PATCH_V7_TRAINING_TENSOR", semantic_id="MODEL_TRAINING_TENSOR",
                    observation_ts=issued_at, value=len(result["training"]),
                    transform="NPZ_COMPRESSED_EXACT_TRAINING_TENSOR_V1", lineage=EXPERT.model_version,
                    metadata={"encoding":"npz_compressed_base64","payload_b64":result["training_payload"],"sha256":result["training_sha"],"training_sample_count":len(result["training"]),"train_valid_cut":result["training_cut"],**common},
                ))
                ids.append(legacy.insert_snapshot(
                    cur, issued_at=issued_at, target_period=TARGET_PERIOD, sha=sha,
                    series_id="PATCH_V7_TEST_X_TENSOR", semantic_id="MODEL_TEST_X_TENSOR",
                    observation_ts=issued_at, value=252,
                    transform="NPZ_COMPRESSED_EXACT_252X2_TEST_TENSOR_V1", lineage=EXPERT.model_version,
                    metadata={"encoding":"npz_compressed_base64","payload_b64":result["test_payload"],"sha256":result["test_sha"],"shape":[252,2],"daily_feature_max_date":result["daily_max_date"],"same_origin_date_use":False,**common},
                ))
                macro_specs = [
                    ("DFF_FRED","FEDFUNDS",result["test_macro"][0],"MONTHLY_MEAN_DFF_ASOF_2026_09_30",result["source_meta"]["fedfunds"]),
                    ("NASDAQCOM_COMPLETED_MONTH_RETURN_MARKET_CLOSE_V3","NASDAQ_RETURN",result["test_macro"][1],"LOG_COMPLETED_MONTH_MEAN_RETURN_AUG_OVER_JUL_V3",{"months":["2026-08","2026-07"]}),
                    ("DEXCHUS_FRED","USDCNY_RETURN",result["test_macro"][2],"LOG_MONTHLY_MEAN_RETURN_SEP_OVER_AUG_OWN_MONTHEND_VINTAGES",{"sep":result["source_meta"]["fx_sep"],"aug":result["source_meta"]["fx_aug"]}),
                    ("GPR_OFFICIAL","GPR_LOG1P_LAG2",result["test_macro"][3],"LOG1P_GPR_2026_08_LAG2",result["source_meta"]["gpr"]),
                    ("GPR_OFFICIAL","GPR_MINMAX_Z_LAG2",result["test_macro"][4],"MINMAX_Z_GPR_2026_08_LAG2_FROZEN_CORE_PLUS_CURRENT",result["source_meta"]["gpr"]),
                ]
                for series_id, semantic_id, value, transform, meta in macro_specs:
                    ids.append(legacy.insert_snapshot(
                        cur, issued_at=issued_at, target_period=TARGET_PERIOD, sha=sha,
                        series_id=series_id, semantic_id=semantic_id, observation_ts=issued_at,
                        value=value, transform=transform, lineage=series_id,
                        metadata={"source_meta":meta,**common},
                    ))
                ids.append(legacy.insert_snapshot(
                    cur, issued_at=issued_at, target_period=TARGET_PERIOD, sha=sha,
                    series_id="PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V6_ANCHOR",
                    semantic_id="MONTHLY_REFERENCE_ANCHOR", observation_ts=issued_at,
                    value=result["anchor"], transform="MONTHLY_MEAN_17ET_HOURLY_CLOSE_2026_09",
                    lineage="PATCH_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V6_ANCHOR",
                    metadata={"source_meta":result["source_meta"]["anchor"],**common},
                ))

                cur.execute(
                    """
                    insert into derived_feature_snapshots
                      (feature_name,feature_version,calculation_ts,input_cutoff,value_num,
                       git_commit,input_lineage,quality_status,metadata)
                    values (%s,%s,%s,%s,%s,%s,%s::jsonb,%s,%s::jsonb)
                    returning id
                    """,
                    (
                        "PATCH_V7_PREDICTED_LOG_RETURN", EXPERT.model_version, issued_at, issued_at,
                        result["predicted_return"], sha,
                        json.dumps({"forecast_input_snapshot_ids":ids,"input_fingerprint":result["input_fingerprint"]}),
                        EVIDENCE_CLASS,
                        json.dumps({"target_month":TARGET_PERIOD,"prospective_claim":True,**common}),
                    ),
                )
                derived_id = int(cur.fetchone()["id"])

                record = ExpertForecastRecord(
                    target_month=TARGET_PERIOD,
                    forecast_origin=issued_at,
                    as_of=issued_at,
                    forecast_track=TRACK_MONTH_END,
                    expert_id=PATCH_EXPERT,
                    model_name=EXPERT.model_name,
                    model_version=EXPERT.model_version,
                    expert_role=EXPERT.expert_role,
                    forecast_value=float(result["forecast"]),
                    unit="USD/oz",
                    evidence_class=EVIDENCE_CLASS,
                    git_commit=sha,
                    input_snapshot_ids=tuple(ids),
                    input_fingerprint=result["input_fingerprint"],
                    provenance={
                        **common,
                        "derived_feature_snapshot_id": derived_id,
                        "model_impact_parent": "PATCH_R1_V7_COMPLETED_SESSION_DAILY_FEATURE_MODEL_IMPACT_PASS",
                        "writer_rehearsal_parent": "PATCH_V7_FORECAST_WRITER_REHEARSAL_PASS",
                        "decision_store_write": "NONE",
                        "canonical_forecast_contract_write": "NONE",
                        "manifest_version": "1.22",
                    },
                )
                stored = insert_expert_forecast(cur, record, verify_snapshots=True)
                if stored.get("duplicate"):
                    raise RuntimeError("UNEXPECTED_PATCH_EXPERT_DUPLICATE_DURING_ATOMIC_ISSUANCE")
                expert_id = int(stored["id"])
            conn.commit()
        except Exception:
            conn.rollback()
            raise

    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                select id,selector_status,auto_selector,auto_ensemble,canonical_authority,input_snapshot_ids
                from monthly_expert_forecasts where id=%s
                """,
                (expert_id,),
            )
            row = cur.fetchone()
        conn.rollback()
    if not row or row["selector_status"] != SELECTOR_STATUS or row["auto_selector"] != "OFF" or row["auto_ensemble"] != "OFF" or row["canonical_authority"] is not False:
        raise RuntimeError("PATCH_MULTI_EXPERT_POST_COMMIT_VERIFY_FAILED")
    if len(row["input_snapshot_ids"] or []) != len(ids):
        raise RuntimeError("PATCH_MULTI_EXPERT_SNAPSHOT_BINDING_VERIFY_FAILED")
    return {"duplicate": False, "expert_id": expert_id, "snapshot_ids": ids, "derived_id": derived_id}


def preflight(now_utc: datetime) -> int:
    legacy.static_gates()
    url = legacy.env("NEON_DATABASE_URL")
    state = expert_ledger_state(url)
    eligible, reason = legacy.eligibility(now_utc)
    passed = bool(state["table_exists"] and state["duplicate"] == 0)
    print(f"MULTI_EXPERT_PATCH_PREFLIGHT_PASS={str(passed).lower()}")
    print(f"ELIGIBILITY_STATE={reason}")
    print(f"EXPERT_ID={PATCH_EXPERT}")
    print(f"FORECAST_TRACK={TRACK_MONTH_END}")
    print(f"SELECTOR_STATUS={SELECTOR_STATUS}")
    print(f"AUTO_SELECTOR={AUTO_SELECTOR}")
    print(f"AUTO_ENSEMBLE={AUTO_ENSEMBLE}")
    print("CANONICAL_FORECAST_CONTRACT_WRITE=NONE")
    print("DATABASE_WRITES=NONE")
    return 0 if passed else 3


def issue_if_eligible(now_utc: datetime) -> int:
    legacy.static_gates()
    url = legacy.env("NEON_DATABASE_URL")
    eligible, reason = legacy.eligibility(now_utc)
    if not eligible:
        print(f"MULTI_EXPERT_PATCH_ISSUER_STATE={reason}")
        print("DATABASE_WRITES=NONE")
        return 0
    state = expert_ledger_state(url)
    if not state["table_exists"]:
        raise RuntimeError("BLOCKED_MULTI_EXPERT_LEDGER_SCHEMA_NOT_APPLIED")
    if state["duplicate"]:
        print("MULTI_EXPERT_PATCH_ISSUER_STATE=SKIP_ALREADY_ISSUED")
        print("DATABASE_WRITES=NONE")
        return 0

    result = legacy.build_forecast(now_utc)
    sha = legacy.git_sha()
    persisted = persist_atomic(url, now_utc, result, sha)
    print("MULTI_EXPERT_PATCH_ISSUER_STATE=MONTH_END_EXPERT_ISSUED_VERIFIED")
    print(f"TARGET_MONTH={TARGET_PERIOD}")
    print(f"EXPERT_ID={PATCH_EXPERT}")
    print(f"EXPERT_LEDGER_ID={persisted['expert_id']}")
    print(f"FORECAST_INPUT_SNAPSHOT_COUNT={len(persisted['snapshot_ids'])}")
    print(f"DERIVED_FEATURE_SNAPSHOT_ID={persisted['derived_id']}")
    print(f"SELECTOR_STATUS={SELECTOR_STATUS}")
    print("FORECAST_VALUE_LOGGED=NO")
    print("CANONICAL_FORECAST_CONTRACT_WRITE=NONE")
    print("DECISION_STORE_WRITE=NONE")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["preflight", "issue-if-eligible"], required=True)
    args = parser.parse_args()
    now_utc = datetime.now(timezone.utc)
    return preflight(now_utc) if args.mode == "preflight" else issue_if_eligible(now_utc)


if __name__ == "__main__":
    raise SystemExit(main())
