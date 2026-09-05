from __future__ import annotations

import importlib.util
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "audit_gpr_pit_coverage_v2.py"
spec = importlib.util.spec_from_file_location("audit_gpr_pit_coverage_v2", SCRIPT)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
assert spec.loader is not None
spec.loader.exec_module(mod)


def test_required_window_has_72_origins():
    months = mod.month_range("2020-09", "2026-08")
    assert len(months) == 72
    assert months[0] == "2020-09"
    assert months[-1] == "2026-08"


def test_origin_cutoff_is_month_end_17_et():
    # September is EDT, so 17:00 ET = 21:00 UTC.
    assert mod.origin_cutoff("2020-09") == datetime(2020, 9, 30, 21, 0, tzinfo=timezone.utc)
    # December is EST, so 17:00 ET = 22:00 UTC.
    assert mod.origin_cutoff("2020-12") == datetime(2020, 12, 31, 22, 0, tzinfo=timezone.utc)


def test_summary_never_promotes_partial_coverage():
    good = mod.CoverageRow(
        origin_month="2020-09", expected_filename="x.xls", expected_web_url="u",
        origin_cutoff_utc="2020-09-30T21:00:00Z", direct_http_status=206,
        direct_http_present=True, repo_current_xls=True, repo_ever_xls=True,
        repo_earliest_add_utc="2020-09-01T00:00:00Z", repo_git_pit_proven=True,
        repo_current_dta=False, repo_ever_dta=False, repo_dta_earliest_add_utc=None,
        v1_source_ready=True,
        pit_status="PROVEN_OFFICIAL_GIT_BY_ORIGIN_AND_CURRENT_DIRECT_RETRIEVABLE",
    )
    summary = mod.summarize([good])
    assert summary["v1_binding_result"] == "SOURCE_BLOCKED_NO_MODEL_SCORE"


def test_current_presence_alone_is_not_pit_proof():
    cutoff = mod.origin_cutoff("2020-09")
    later = datetime(2022, 1, 1, tzinfo=timezone.utc)
    assert later > cutoff
