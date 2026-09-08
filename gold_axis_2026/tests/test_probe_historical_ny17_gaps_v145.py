from __future__ import annotations

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / "gold_axis_2026/tools/probe_historical_ny17_gaps_v145.py"
SPEC = importlib.util.spec_from_file_location("ny17_probe_v145", PATH)
assert SPEC and SPEC.loader
probe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe)


def test_unique_exact_bar_and_ohlc_gate():
    result = probe.classify_payload({"values": [{"datetime": "2025-01-02 16:59:00", "open": "2600", "high": "2602", "low": "2599", "close": "2601"}]})
    assert result["acquisition_status"] == "VALID_EXACT_BAR"
    assert result["close"] == 2601.0


def test_missing_exact_bar_is_provider_no_bar():
    result = probe.classify_payload({"values": [{"datetime": "2025-01-02 16:58:00", "open": "1", "high": "1", "low": "1", "close": "1"}]})
    assert result["acquisition_status"] == "PROVIDER_NO_BAR"


def test_quota_and_entitlement_fail_closed():
    assert probe.classify_error(429, "API credits exhausted") == "ENTITLEMENT_BLOCKED"
    assert probe.classify_error(403, "plan access required") == "ENTITLEMENT_BLOCKED"


def test_malformed_range_is_rejected():
    result = probe.classify_payload({"values": [{"datetime": "2025-01-02 16:59:00", "open": "2600", "high": "2590", "low": "2599", "close": "2601"}]})
    assert result["acquisition_status"] == "MALFORMED_BAR"


if __name__ == "__main__":
    tests = [(name, value) for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for name, test in sorted(tests):
        test(); print(f"PASS {name}")
    print(f"PASS total={len(tests)}")
