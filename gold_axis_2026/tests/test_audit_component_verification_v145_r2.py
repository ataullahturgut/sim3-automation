from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "gold_axis_2026/tools/audit_component_verification_v145_r2.py"
spec = importlib.util.spec_from_file_location("cv_r2", PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def snapshot(engine: str):
    return {
        "runtime": [{
            "engine_id": engine,
            "engine_version": m.base.EXPECTED_VERSION[engine],
            "runtime_status": "ACTIVE",
        }],
        "sources": [{
            "series_id": "XAU_EOD_TWELVE_NY17",
            "source_name": "Twelve Data",
            "source_symbol": "XAU/USD",
        }],
    }


def test_enum_based_monthly_direction_is_not_false_failed(monkeypatch):
    monkeypatch.setattr(m.base, "ny17_bundle", lambda: (False, "pending"))
    r = m.verify_r4("MONTHLY_DIRECTION_3M", snapshot("MONTHLY_DIRECTION_3M"), True)
    assert r["dimensions"]["C2_IMPLEMENTATION_RULE"]["status"] == "PASS"
    assert r["dimensions"]["C5_ORIGIN_PIT"]["status"] == "PASS"
    assert r["dimensions"]["C6_FUTURE_INFORMATION"]["status"] == "PASS"
    assert r["component_verification_status"] == "BLOCKED"


def test_enum_based_emergency_reversal_is_not_false_failed(monkeypatch):
    monkeypatch.setattr(m.base, "ny17_bundle", lambda: (False, "pending"))
    r = m.verify_r4("EMERGENCY_REVERSAL", snapshot("EMERGENCY_REVERSAL"), True)
    assert r["dimensions"]["C2_IMPLEMENTATION_RULE"]["status"] == "PASS"
    assert r["dimensions"]["C5_ORIGIN_PIT"]["status"] == "PASS"
    assert r["dimensions"]["C6_FUTURE_INFORMATION"]["status"] == "PASS"
    assert r["component_verification_status"] == "BLOCKED"


def test_r2_is_a_verifier_correction_not_model_change():
    source = PATH.read_text(encoding="utf-8")
    assert 'out["model_or_contract_change"] = "NONE"' in source
    assert 'out["audit_id"] = "GOLD_CONTROL_COMPONENT_VERIFICATION_V145_R2"' in source
