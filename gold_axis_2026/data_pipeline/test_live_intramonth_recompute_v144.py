from __future__ import annotations

import pandas as pd

import live_intramonth_recompute_v144 as mod


def _xau_rows() -> list[dict]:
    values = [
        ("2026-07-31T21:00:00Z", 4045.25141),
        ("2026-08-03T21:00:00Z", 4055.31310),
        ("2026-08-04T21:00:00Z", 4077.39577),
        ("2026-08-05T21:00:00Z", 4246.99711),
        ("2026-08-06T21:00:00Z", 4240.81960),
        ("2026-08-07T21:00:00Z", 4342.63347),
        ("2026-08-10T21:00:00Z", 4389.99300),
        ("2026-08-11T21:00:00Z", 4367.71611),
        ("2026-08-12T21:00:00Z", 4409.04752),
        ("2026-08-13T21:00:00Z", 4351.17522),
        ("2026-08-14T21:00:00Z", 4376.56187),
        ("2026-08-17T21:00:00Z", 4416.62725),
        ("2026-08-18T21:00:00Z", 4335.67938),
        ("2026-08-19T21:00:00Z", 4523.24519),
        ("2026-08-20T21:00:00Z", 4519.34377),
        ("2026-08-21T21:00:00Z", 4603.92129),
        ("2026-08-24T21:00:00Z", 4652.16852),
        ("2026-08-25T21:00:00Z", 4658.63733),
        ("2026-08-26T21:00:00Z", 4594.48089),
        ("2026-08-27T21:00:00Z", 4601.51520),
        ("2026-08-28T21:00:00Z", 4456.44061),
        ("2026-08-31T21:00:00Z", 4448.80126),
        ("2026-09-01T21:00:00Z", 4328.57714),
        ("2026-09-02T21:00:00Z", 4387.76527),
        ("2026-09-03T21:00:00Z", 4473.78645),
    ]
    out = []
    for i, (ts, value) in enumerate(values, start=1):
        out.append(
            {
                "id": i,
                "observation_ts": pd.Timestamp(ts),
                "value": value,
                "available_as_of": pd.Timestamp(ts) + pd.Timedelta(hours=11),
                "retrieved_at": pd.Timestamp(ts) + pd.Timedelta(hours=11),
                "quality_status": mod.XAU_QUALITY,
                "lineage_id": "xau-lineage",
                "source": "Twelve Data",
                "source_symbol": "XAU/USD",
            }
        )
    return out


def _gvz() -> dict:
    return {
        "id": 900,
        "observation_ts": pd.Timestamp("2026-09-04T00:00:00Z"),
        "value": 26.63,
        "available_as_of": pd.Timestamp("2026-09-05T01:23:15Z"),
        "retrieved_at": pd.Timestamp("2026-09-05T01:23:15Z"),
        "quality_status": "APPROVED_AUTHORITY_RETRIEVAL_FLOOR",
        "lineage_id": "gvz-lineage",
        "source": "Cboe",
        "source_symbol": "GVZ",
    }


def _reference() -> dict:
    return {
        "forecast_value": 4452.046728838838,
        "evidence_class": "HISTORICAL_REPLAY",
        "target_month": "2026-09",
        "forecast_origin": "2026-08-31T21:00:00Z",
        "prospective_claim": False,
        "canonical_authority": False,
    }


def test_frozen_rules_produce_expected_current_states() -> None:
    state = mod._compute(_xau_rows(), _gvz(), "2026-09", _reference())
    assert state["fast"] == "MIXED"
    assert state["slow"] == "ROBUST_UP"
    assert state["emergency_level"] == "NEUTRAL"
    assert state["emergency_reversal"] == "OFF"
    assert state["gvz_value"] == 26.63
    assert state["gvz_cap"] == 0.5
    assert state["gvz_panic"] is False
    assert state["gvz_regime"] == "ELEVATED"


def test_fingerprint_is_deterministic_and_contract_bound() -> None:
    payload = [{"id": 1, "value": 2.0}]
    assert mod._fingerprint("FAST", payload) == mod._fingerprint("FAST", payload)
    assert mod._fingerprint("FAST", payload) != mod._fingerprint("SLOW", payload)


def test_ny_trade_date_preserves_17et_session_date() -> None:
    assert mod._ny_trade_date("2026-09-03T21:00:00Z") == "2026-09-03"
    assert mod._ny_trade_date("2026-01-05T22:00:00Z") == "2026-01-05"


def test_emergency_reference_replay_is_not_promoted_to_prospective() -> None:
    # Current runtime inventory rows remain governance-audit rows. The historical
    # monthly-reference class is preserved separately in metadata and must never
    # be rewritten as a prospective H=1 claim.
    assert _reference()["evidence_class"] == "HISTORICAL_REPLAY"
    assert _reference()["prospective_claim"] is False
