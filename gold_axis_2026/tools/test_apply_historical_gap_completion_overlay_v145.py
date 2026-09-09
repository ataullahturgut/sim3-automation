from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "gold_axis_2026/tools/apply_historical_gap_completion_overlay_v145.py"
SPEC = importlib.util.spec_from_file_location("post_gap_overlay_v145", MODULE_PATH)
assert SPEC and SPEC.loader
overlay = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(overlay)


def inputs():
    audits = ROOT / "gold_axis_2026/data_pipeline/audits"
    rows = overlay.load_csv(audits / "historical_pilot_readiness_v145.csv")
    bundle = json.loads((audits / "historical_reconstruction_bundle_v145/historical_reconstruction_bundle_v145.json").read_text())
    return rows, bundle


def test_overlay_is_deterministic_and_exactly_240_cells():
    rows, bundle = inputs()
    first, counts = overlay.apply_overlay(rows, bundle)
    second, counts2 = overlay.apply_overlay(copy.deepcopy(rows), copy.deepcopy(bundle))
    assert first == second
    assert counts == counts2
    assert len(first) == 240
    assert len({r["engine_id"] for r in first}) == 12
    assert len({r["target_month"] for r in first}) == 20


def test_data_completion_never_promotes_to_ready_proven():
    rows, bundle = inputs()
    updated, _ = overlay.apply_overlay(rows, bundle)
    for before, after in zip(rows, updated, strict=True):
        if before["readiness_status"] != after["readiness_status"]:
            assert after["readiness_status"] == "READY_TO_REPLAY"


def test_ny17_and_gvz_gaps_are_only_promoted_to_replay():
    rows, bundle = inputs()
    updated, counts = overlay.apply_overlay(rows, bundle)
    assert counts == {
        "BLOCKED_CONTRACT": 1,
        "CONTRACTUAL_EXCLUSION": 1,
        "READY_PROVEN": 114,
        "READY_TO_REPLAY": 124,
    }
    for row in updated:
        if row["engine_id"] in overlay.NY17_ENGINES or row["engine_id"] == "GVZ_RISK":
            assert row["readiness_status"] == "READY_TO_REPLAY"


def test_bundle_fingerprint_mismatch_fails_closed():
    rows, bundle = inputs()
    bundle["outputs"]["gvz_valid"]["sha256"] = "0" * 64
    try:
        overlay.apply_overlay(rows, bundle)
    except ValueError as exc:
        assert str(exc) == "BUNDLE_OUTPUT_IDENTITY_MISMATCH:gvz_valid"
    else:
        raise AssertionError("tampered bundle accepted")


if __name__ == "__main__":
    tests = [(name, value) for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for name, test in sorted(tests):
        test()
        print(f"PASS {name}")
    print(f"PASS total={len(tests)}")
