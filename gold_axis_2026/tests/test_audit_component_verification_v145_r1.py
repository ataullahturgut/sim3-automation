from __future__ import annotations

import ast
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "gold_axis_2026/tools/audit_component_verification_v145_r1.py"

spec = importlib.util.spec_from_file_location("component_verifier_r1", MODULE_PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def _all(status: str):
    return {name: m.dim(status, None) for name in m.DIMS}


def test_exact_governed_inventory():
    assert len(m.ENGINE_ORDER) == 12
    assert len(set(m.ENGINE_ORDER)) == 12
    assert set(m.EXPECTED_VERSION) == set(m.ENGINE_ORDER)


def test_final_status_precedence():
    assert m.final_status(_all("PASS")) == "PASS"
    x = _all("PASS"); x[m.DIMS[0]] = m.dim("NOT_PROVEN", None); assert m.final_status(x) == "NOT_PROVEN"
    x[m.DIMS[1]] = m.dim("BLOCKED", None); assert m.final_status(x) == "BLOCKED"
    x[m.DIMS[2]] = m.dim("FAIL", None); assert m.final_status(x) == "FAIL"


def test_ny17_bundle_is_fail_closed_when_absent_or_incomplete(monkeypatch, tmp_path):
    monkeypatch.setattr(m, "AUDITS", tmp_path)
    monkeypatch.setattr(m, "ROOT", tmp_path)
    ok, _ = m.ny17_bundle(); assert ok is False
    p = tmp_path / "historical_reconstruction_bundle_v145"
    p.mkdir()
    (p / "historical_reconstruction_bundle_v145.json").write_text('{"status":"BLOCKED","production_database_write":"NONE","prospective_claim":false}', encoding="utf-8")
    ok, _ = m.ny17_bundle(); assert ok is False


def test_performance_metrics_are_not_consumed_by_status_logic():
    source = MODULE_PATH.read_text(encoding="utf-8")
    forbidden = ["mape", "mae", "rmse", "accuracy", "win_rate", "economic_value"]
    lowered = source.lower()
    for token in forbidden:
        assert token not in lowered
    assert '"performance_fields_consumed":False' in source.replace(" ", "")


def test_sql_is_read_only_static_audit():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    strings = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            strings.append(node.value.lower())
    sqlish = "\n".join(strings)
    for token in ("insert into", "update ", "delete from", "truncate ", "drop table", "alter table"):
        assert token not in sqlish
    assert "set transaction isolation level repeatable read, read only" in sqlish


def test_correct_r4_frozen_tokens_are_bound():
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "m3 = sum(completed_month_returns[-3:]) / 3.0" in source
    assert "level_threshold_abs: float = 0.04" in source
    assert "reversal_threshold_abs: float = 0.04" in source
    assert 'resample(\\"W-FRI\\")' in source or 'resample("W-FRI")' in source


def test_result_carries_no_performance_payload():
    r = m.result("X", _all("PASS"), "e")
    assert r["component_verification_status"] == "PASS"
    assert r["performance_fields_consumed"] is False
    assert set(r) == {"engine_id", "component_verification_status", "dimensions", "evidence_reference", "performance_fields_consumed"}
