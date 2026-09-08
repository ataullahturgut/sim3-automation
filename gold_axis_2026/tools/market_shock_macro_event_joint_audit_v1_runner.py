from __future__ import annotations

import pandas as pd

import market_shock_macro_event_joint_audit_v1 as audit


def verify_cache_lineage_fixed(conn) -> dict:
    q = """
    SELECT batch_id, series_id, interval, first_ts, last_ts, retrieved_at,
           provider, symbol, evidence_class, purpose, row_count, inserted_count,
           payload_sha256, code_sha, status
    FROM xau_intraday_research_cache_batches
    WHERE interval='5min'
    ORDER BY batch_id DESC
    LIMIT 1
    """
    d = audit.fetch_df(conn, q)
    if len(d) != 1:
        raise RuntimeError("XAU_5M_CACHE_BATCH_NOT_FOUND")
    r = d.iloc[0].to_dict()
    first_ts = pd.to_datetime(r["first_ts"], utc=True)
    last_ts = pd.to_datetime(r["last_ts"], utc=True)
    checks = {
        "provider": r["provider"] == "Twelve Data",
        "symbol": r["symbol"] == "XAU/USD",
        "interval": r["interval"] == "5min",
        "evidence_class": r["evidence_class"] == "HISTORICAL_RESEARCH_RETRIEVAL",
        "status": r["status"] == "COMPLETE",
        "coverage_start": first_ts <= pd.Timestamp("2020-04-06", tz="UTC"),
        "coverage_end": last_ts >= pd.Timestamp("2025-12-31 23:00", tz="UTC"),
    }
    if not all(checks.values()):
        raise RuntimeError(f"XAU_5M_CACHE_LINEAGE_FAIL:{checks}")
    out = {k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in r.items()}
    out["checks"] = checks
    return out


audit.verify_cache_lineage = verify_cache_lineage_fixed

if __name__ == "__main__":
    raise SystemExit(audit.main())
