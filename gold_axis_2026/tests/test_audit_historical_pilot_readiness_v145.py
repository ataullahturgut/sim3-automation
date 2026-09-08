from __future__ import annotations

import ast
import copy
import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
MODULE_PATH = ROOT / "gold_axis_2026/tools/audit_historical_pilot_readiness_v145.py"
SPEC = importlib.util.spec_from_file_location("historical_readiness_v145", MODULE_PATH)
assert SPEC and SPEC.loader
audit = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(audit)


def source(series_id: str, n: int = 126, max_ts: str = "2026-07-31T00:00:00+00:00") -> dict:
    return {"series_id": series_id, "n": n, "max_ts": max_ts, "null_available": 0, "lineage_n": 1}


def snapshot() -> dict:
    governed = sorted({s for spec in audit.ENGINE_SPECS for s in spec["required_sources"] if ":" not in s and not s.startswith(("FROZEN_", "IMMUTABLE_", "CORE5_"))})
    sources = [source(s, 126 if s.startswith("MACRO_") else 1000) for s in governed]
    return {"snapshot_at": "2026-09-08T22:00:00+00:00", "tx_snapshot": "1:1:", "sources": sources,
            "observations": [], "authority_counts": {t: 0 for t in audit.AUTHORITY_TABLES}}


def test_exact_inventory_and_axis_cardinality():
    report = audit.build_report(ROOT, snapshot())
    assert report["engine_count"] == 12
    assert report["target_month_count"] == 20
    assert report["matrix_row_count"] == 240
    assert len({r["engine_id"] for r in report["matrix"]}) == 12
    assert len({r["target_month"] for r in report["matrix"]}) == 20


def test_deterministic_rerun_same_snapshot():
    first = audit.build_report(ROOT, snapshot())
    second = audit.build_report(ROOT, copy.deepcopy(snapshot()))
    assert first["matrix_sha256"] == second["matrix_sha256"]
    assert first["matrix"] == second["matrix"]


def test_performance_values_cannot_change_readiness():
    base = snapshot()
    altered = copy.deepcopy(base)
    altered["performance"] = {"MAPE": 999999, "winner": "FORBIDDEN_SELECTOR"}
    assert audit.build_report(ROOT, base)["matrix_sha256"] == audit.build_report(ROOT, altered)["matrix_sha256"]


def test_auditor_sql_is_select_only_and_transaction_read_only():
    tree = ast.parse(MODULE_PATH.read_text(encoding="utf-8"))
    sql_literals = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "execute" and node.args:
            arg = node.args[0]
            if isinstance(arg, ast.Constant) and isinstance(arg.value, str): sql_literals.append(arg.value.strip().lower())
            elif isinstance(arg, ast.JoinedStr): sql_literals.append("select count(*)::bigint n from {table}")
    assert sql_literals
    assert any(s.startswith("set transaction") and "read only" in s for s in sql_literals)
    forbidden = ("insert ", "update ", "delete ", "merge ", "alter ", "drop ", "truncate ", "create ", "grant ", "revoke ")
    assert not any(any(token in sql for token in forbidden) for sql in sql_literals)
    assert all(sql.startswith(("select", "set transaction")) for sql in sql_literals)


def test_contractual_exclusion_remains_visible():
    rows = audit.build_report(ROOT, snapshot())["matrix"]
    row = next(r for r in rows if r["engine_id"] == "MACRO_EVENT_SUCCESSOR_V2" and r["target_month"] == "2025-10")
    assert row["readiness_status"] == "CONTRACTUAL_EXCLUSION"
    assert row["blocker_code"] == "FROZEN_COMPLETE_CASE_EXCLUSION_2025_10"


def test_bocpd_august_is_contract_blocked():
    rows = audit.build_report(ROOT, snapshot())["matrix"]
    row = next(r for r in rows if r["engine_id"] == "BOCPD_RETURN_SUCCESSOR_V1" and r["target_month"] == "2026-08")
    assert row["readiness_status"] == "BLOCKED_CONTRACT"


def test_every_row_has_required_public_fields_and_known_status():
    required = {"engine_id", "role", "target_month", "evaluation_clock", "required_sources", "required_history", "source_coverage", "source_binding", "lineage_status", "evidence_class", "PIT_status", "future_information_status", "reproducibility_status", "readiness_status", "blocker_code", "evidence_reference"}
    for row in audit.build_report(ROOT, snapshot())["matrix"]:
        assert required <= set(row)
        assert row["readiness_status"] in audit.READY_STATES


if __name__ == "__main__":
    tests = [(name, value) for name, value in globals().items() if name.startswith("test_") and callable(value)]
    for name, test in sorted(tests):
        test()
        print(f"PASS {name}")
    print(f"PASS total={len(tests)}")
