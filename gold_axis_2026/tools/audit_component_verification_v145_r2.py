from __future__ import annotations

import importlib.util
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE / "audit_component_verification_v145_r1.py"
spec = importlib.util.spec_from_file_location("component_verifier_v145_r1_base", BASE_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("COMPONENT_VERIFIER_R1_IMPORT_FAILED")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)


def verify_r4(engine: str, snap: dict[str, Any], tests_pass: bool) -> dict[str, Any]:
    """R2 correction: bind static checks to the actual frozen enum-based R4 implementation.

    No model mathematics, source, threshold, timing or readiness rule changes here.
    The R1 draft compared two enum-valued implementations against string-valued
    source tokens and could therefore emit false implementation FAILs.
    """
    dims = base.base(engine, snap)
    paths = {
        "MONTHLY_DIRECTION_3M": "r4_1/src/gold_r4/monthly.py",
        "FAST": "r4_1/src/gold_r4/tactical.py",
        "SLOW": "r4_1/src/gold_r4/tactical.py",
        "EMERGENCY_LEVEL": "r4_1/src/gold_r4/emergency.py",
        "EMERGENCY_REVERSAL": "r4_1/src/gold_r4/emergency.py",
    }
    tokens = {
        "MONTHLY_DIRECTION_3M": [
            "m3 = sum(completed_month_returns[-3:]) / 3.0",
            "return Direction.UP",
            "return Direction.DOWN",
            "return Direction.NEUTRAL",
        ],
        "FAST": ["sma_days: int = 20", "persistence_days: int = 2"],
        "SLOW": ["sma_weeks: int = 4", "persistence_weeks: int = 2", 'resample("W-FRI")'],
        "EMERGENCY_LEVEL": [
            "level_threshold_abs: float = 0.04",
            "displacement = close / monthly_vw_forecast - 1.0",
            "level = Direction.UP",
            "level = Direction.DOWN",
            "level = Direction.NEUTRAL",
        ],
        "EMERGENCY_REVERSAL": [
            "reversal_threshold_abs: float = 0.04",
            "alert = ReversalAlert.DOWN_ALERT",
            "alert = ReversalAlert.UP_ALERT",
            "self._reset_month(month_key)",
        ],
    }
    text = (base.GC / paths[engine]).read_text(encoding="utf-8")
    rule_ok = all(token in text for token in tokens[engine])
    dims["C2_IMPLEMENTATION_RULE"] = base.dim(
        "PASS" if rule_ok and tests_pass else ("FAIL" if not rule_ok else "NOT_PROVEN"),
        {"code": paths[engine], "frozen_tests_pass": tests_pass, "static_tokens": tokens[engine]},
    )

    src = {r["series_id"]: r for r in snap["sources"]}.get("XAU_EOD_TWELVE_NY17")
    src_ok = bool(src and src.get("source_name") == "Twelve Data" and src.get("source_symbol") == "XAU/USD")
    dims["C3_SOURCE_BINDING"] = base.dim("PASS" if src_ok else "FAIL", src)

    complete, evidence = base.ny17_bundle()
    dims["C4_HISTORICAL_COVERAGE"] = base.dim("PASS" if complete else "BLOCKED", evidence)
    dims["C5_ORIGIN_PIT"] = base.dim("PASS" if rule_ok else "FAIL", "frozen chronological/completed-period rule")
    dims["C6_FUTURE_INFORMATION"] = base.dim("PASS" if rule_ok else "FAIL", "chronological replay; no performance input")
    dims["C7_RECONSTRUCTION_VINTAGE"] = base.dim("PASS" if complete else "BLOCKED", evidence)
    dims["C8_DETERMINISM_REPRODUCIBILITY"] = base.dim("PASS" if tests_pass else "NOT_PROVEN", "R4.1 frozen tests")
    dims["C9_PILOT_CELL_EXECUTION"] = base.dim(
        "NOT_PROVEN" if complete else "BLOCKED",
        "historical role replay follows NY17 bundle completion",
    )
    return base.result(engine, dims, paths[engine])


base.verify_r4 = verify_r4
_original_build = base.build


def build(*args, **kwargs):
    out = _original_build(*args, **kwargs)
    out["audit_id"] = "GOLD_CONTROL_COMPONENT_VERIFICATION_V145_R2"
    out["auditor_revision"] = "R2_ENUM_AWARE_STATIC_BINDING_CORRECTION"
    out["r1_false_fail_semantics_changed"] = False
    out["model_or_contract_change"] = "NONE"
    return out


base.build = build

if __name__ == "__main__":
    raise SystemExit(base.main())
