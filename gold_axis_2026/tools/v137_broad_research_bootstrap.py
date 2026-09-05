from __future__ import annotations

import json
import os
import subprocess
import sys
from argparse import Namespace
from pathlib import Path

import psycopg

ROOT = Path(__file__).resolve().parents[2]
GOLD = ROOT / "gold_axis_2026"
MANIFEST = GOLD / "GOLD_CONTROL_PROJECT_MANIFEST.md"
SOURCE_PREFLIGHT_SHA = "a0a06bbce8249f8e7ac4cc0f482f1f68c711657b"
TESTED_WRITER_SHA = "671ca6ef84dcc4ffbbf6a6f216b8352897a1ff95"
FEATURE_EVIDENCE_SHA = "e35bc951e7d49f29add2bf5b737b16200709d1a7"
EXPECTED_WRITER_BLOB = "3bb80b42961e0a16fbbf40eb14ab5340d169e797"
EXPECTED_CORE5_BLOB = "bd7c1df860cc2975f123e300be597e9dec42e5c3"
AUTH_TOKEN = "MANIFEST_V1_37_BROAD_RESEARCH_DATA_SPINE_R1"
EXPECTED = {
    "CORE5_FEDFUNDS_RESEARCH_R1": 390,
    "CORE5_GOLD_USD_OZ_RESEARCH_R1": 390,
    "CORE5_GPR_ROUNDED_RESEARCH_R1": 390,
    "CORE5_NASDAQ_AVG_RESEARCH_R1": 390,
    "CORE5_USDCNY_AVG_RESEARCH_R1": 390,
    "GPRA_OFFICIAL_GIT_PIT": 25515,
    "GPRT_OFFICIAL_GIT_PIT": 25515,
    "XAG_STAKTRAKR_RESEARCH_DAILY_R1": 4230,
    "XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1": 1177,
    "XAU_STAKTRAKR_RESEARCH_DAILY_R1": 4230,
    "XPD_STAKTRAKR_RESEARCH_DAILY_R1": 4229,
    "XPT_STAKTRAKR_RESEARCH_DAILY_R1": 4229,
}


def sh(*args: str, capture: bool = False, cwd: Path = ROOT) -> str:
    p = subprocess.run(args, cwd=cwd, check=True, text=True, capture_output=capture)
    return p.stdout.strip() if capture else ""


def git_show(sha: str, path: str) -> bytes:
    p = subprocess.run(["git", "show", f"{sha}:{path}"], cwd=ROOT, check=True, capture_output=True)
    return p.stdout


def require_env() -> None:
    required = ["NEON_DATABASE_URL", "TWELVE_DATA_API_KEY", "GITHUB_REF_NAME"]
    for name in required:
        if not os.environ.get(name):
            raise RuntimeError(f"MISSING_ENV:{name}")
    if os.environ["GITHUB_REF_NAME"] != "gold-r4-direction-engine":
        raise RuntimeError("CANONICAL_BRANCH_REQUIRED")


def stage_frozen_files() -> None:
    sh("git", "fetch", "--no-tags", "origin", "gold-control-broad-research-data-spine-r1")
    writer_blob = sh("git", "rev-parse", f"{TESTED_WRITER_SHA}:gold_axis_2026/data_pipeline/broad_research_data_spine_r1_ingest.py", capture=True)
    core5_blob = sh("git", "rev-parse", f"{SOURCE_PREFLIGHT_SHA}:gold_axis_2026/core5_monthly.csv.gz.b64", capture=True)
    if writer_blob != EXPECTED_WRITER_BLOB or core5_blob != EXPECTED_CORE5_BLOB:
        raise RuntimeError("FROZEN_BLOB_IDENTITY_MISMATCH")
    copies = {
        "gold_axis_2026/core5_monthly.csv.gz.b64": (SOURCE_PREFLIGHT_SHA, "gold_axis_2026/core5_monthly.csv.gz.b64"),
        "gold_axis_2026/data_pipeline/source_contracts_research_broad.json": (SOURCE_PREFLIGHT_SHA, "gold_axis_2026/data_pipeline/source_contracts_research_broad.json"),
        "gold_axis_2026/tools/audit_broad_research_data_spine_r1.py": (SOURCE_PREFLIGHT_SHA, "gold_axis_2026/tools/audit_broad_research_data_spine_r1.py"),
        "gold_axis_2026/GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_CHANGE_CONTROL_2026-09-05.md": (SOURCE_PREFLIGHT_SHA, "gold_axis_2026/GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_CHANGE_CONTROL_2026-09-05.md"),
        "gold_axis_2026/data_pipeline/broad_research_data_spine_r1_ingest.py": (TESTED_WRITER_SHA, "gold_axis_2026/data_pipeline/broad_research_data_spine_r1_ingest.py"),
        "gold_axis_2026/GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_R1_NEON_INGESTION_CHANGE_CONTROL_2026-09-05.md": (FEATURE_EVIDENCE_SHA, "gold_axis_2026/GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_R1_NEON_INGESTION_CHANGE_CONTROL_2026-09-05.md"),
        "gold_axis_2026/GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_R1_NEON_INGESTION_ENGINEERING_EVIDENCE_2026-09-05.md": (FEATURE_EVIDENCE_SHA, "gold_axis_2026/GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_R1_NEON_INGESTION_ENGINEERING_EVIDENCE_2026-09-05.md"),
    }
    for dst, (sha, src) in copies.items():
        (ROOT / dst).write_bytes(git_show(sha, src))
    if sh("git", "hash-object", "gold_axis_2026/data_pipeline/broad_research_data_spine_r1_ingest.py", capture=True) != EXPECTED_WRITER_BLOB:
        raise RuntimeError("WRITER_BLOB_CHANGED")
    if sh("git", "hash-object", "gold_axis_2026/core5_monthly.csv.gz.b64", capture=True) != EXPECTED_CORE5_BLOB:
        raise RuntimeError("CORE5_BLOB_CHANGED")


def amend_manifest() -> None:
    s = MANIFEST.read_text(encoding="utf-8")
    if "**Manifest version:** 1.36" not in s or AUTH_TOKEN in s:
        raise RuntimeError("MANIFEST_PRECONDITION_FAILED")
    s = s.replace("**Manifest version:** 1.36", "**Manifest version:** 1.37", 1)
    s = s.replace("**Freeze / issue date:** 2026-09-05", "**Freeze / issue date:** 2026-09-06", 1)
    s = s.replace("this v1.36 manifest governs", "this v1.37 manifest governs", 1)
    s = s.replace("# 11. CURRENT PRODUCTION RUNTIME AUTHORITY — v1.36", "# 11. CURRENT PRODUCTION RUNTIME AUTHORITY — v1.37", 1)
    s = s.replace("Under v1.36, the current governed application inventory is:", "Under v1.37, the current governed application inventory is:", 1)
    s = s.replace("# 13. UI CONTRACT — v1.36", "# 13. UI CONTRACT — v1.37", 1)
    s = s.replace("this v1.34 manifest controls current product/runtime behavior", "this v1.37 manifest controls current product/runtime behavior", 1)
    section = f'''## 14.2 v1.37 Broad Research Data Spine R1 production source-data authorization

Binding authorization token:

`{AUTH_TOKEN}`

This is strictly a research source-data/audit-plane authorization. It grants no model score, forecast issuance, decision write, runtime mutation, selector/ensemble role, or action/position mapping.

Frozen source preflight: head `{SOURCE_PREFLIGHT_SHA}`, run `33989608218`, artifact digest `sha256:ba4300d3501211ce7deaeea61627042f066ec45e679f672deb1741e26e102f1a`, result `SUCCESS`.

Frozen ingestion engineering: writer commit `{TESTED_WRITER_SHA}`, writer blob `{EXPECTED_WRITER_BLOB}`, run `33991644883`, artifact digest `sha256:b1ae7a83d321372061d950c5f1cc8fad8262b570215f9a09ae22a4452fa355b5`, corrected CORE5 blob `{EXPECTED_CORE5_BLOB}`, result `ENGINEERING_PREFLIGHT_PASS`.

The first production persistence is authorized only after canonical execution re-proves, before persistence: exactly 12 research series; 71,075 observations; 126 source-vintage rows; zero quality events; CORE5 390 rows per series; StakTrakr XAU/XAG/XPT/XPD 4,230/4,230/4,229/4,229; Twelve-derived XAU 1,177 rows across 54/54 months with minimum 15 selected days; GPRT/GPRA 25,515/25,515 rows with 54/54 origins; empty reserved Broad R1 registry/observation/vintage namespace; all four forecast/decision authority stores equal zero; runtime exactly ACTIVE=6 / WAITING=5 / BLOCKED=1.

Authorized production tables are only `source_registry`, `retrieval_runs`, `observations`, `source_vintages`, and `quality_events`. Writes to `monthly_forecast_contracts`, `decision_signal_snapshots`, `decision_runs`, `decision_events`, engine runtime authority, model promotion/validation state, selector/ensemble state, and action/position mappings are forbidden.

Evidence semantics remain frozen: CORE5 is not historical PIT; StakTrakr makes no origin-PIT claim; Twelve Data 1h/16:00 America/New_York is historical research retrieval and is not canonical `XAU_EOD_TWELVE_NY17`; GPRT/GPRA are separate official-Git vintage reconstruction identities; retrieval/first-seen timestamps are never backdated; silent provider substitution is forbidden; raw vendor values are not emitted to CI evidence.

`AUTO_SELECTOR=OFF` and `AUTO_ENSEMBLE=OFF` remain binding.'''
    anchor = "\n---\n\n# 15. CURRENT EVIDENCE FILES REFERENCED BY THIS MANIFEST"
    if anchor not in s:
        raise RuntimeError("MANIFEST_SECTION15_ANCHOR_MISSING")
    s = s.replace(anchor, "\n\n" + section + anchor, 1)
    ev = "- `GOLD_CONTROL_GPR_PIT_DATA_PLANE_CHANGE_CONTROL_2026-09-05.md`"
    s = s.replace(ev, ev + "\n- `GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_CHANGE_CONTROL_2026-09-05.md`\n- `GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_R1_NEON_INGESTION_CHANGE_CONTROL_2026-09-05.md`\n- `GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_R1_NEON_INGESTION_ENGINEERING_EVIDENCE_2026-09-05.md`", 1)
    final = "The v1.33 `GPR_OFFICIAL_GIT_PIT` source-data authorization remains valid independently."
    s = s.replace(final, final + "\n\nv1.37 additionally authorizes the frozen Broad Research Data Spine R1 first production persistence under section 14.2 and only under its exact source-data/audit-plane gates.", 1)
    if s.count(AUTH_TOKEN) != 1:
        raise RuntimeError("MANIFEST_AUTH_TOKEN_COUNT_INVALID")
    MANIFEST.write_text(s, encoding="utf-8")


def commit_authority() -> str:
    sh("git", "config", "user.name", "gold-control-governance-bot")
    sh("git", "config", "user.email", "gold-control-governance-bot@users.noreply.github.com")
    paths = [
        "gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md",
        "gold_axis_2026/core5_monthly.csv.gz.b64",
        "gold_axis_2026/data_pipeline/broad_research_data_spine_r1_ingest.py",
        "gold_axis_2026/data_pipeline/source_contracts_research_broad.json",
        "gold_axis_2026/tools/audit_broad_research_data_spine_r1.py",
        "gold_axis_2026/GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_CHANGE_CONTROL_2026-09-05.md",
        "gold_axis_2026/GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_R1_NEON_INGESTION_CHANGE_CONTROL_2026-09-05.md",
        "gold_axis_2026/GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_R1_NEON_INGESTION_ENGINEERING_EVIDENCE_2026-09-05.md",
    ]
    sh("git", "add", *paths)
    sh("git", "commit", "-m", "Gold Control: authorize Broad Research R1 production data plane v1.37")
    sha = sh("git", "rev-parse", "HEAD", capture=True)
    sh("git", "push", "origin", "HEAD:gold-r4-direction-engine")
    return sha


def build_and_persist(code_sha: str) -> dict:
    gpr_repo = Path("/tmp/iacoviel-gpr")
    if gpr_repo.exists():
        subprocess.run(["rm", "-rf", str(gpr_repo)], check=True)
    sh("git", "clone", "--quiet", "https://github.com/iacoviel/iacoviel.github.io.git", str(gpr_repo))
    coverage = ROOT / "gpr_pit_coverage_v137.json"
    sh(sys.executable, "gold_axis_2026/tools/audit_gpr_pit_coverage_v2.py", "--upstream-repo", str(gpr_repo), "--start", "2022-03", "--end", "2026-08", "--skip-http", "--json-out", str(coverage), "--md-out", str(ROOT / "gpr_pit_coverage_v137.md"))
    d = json.loads(coverage.read_text(encoding="utf-8"))
    if len(d["rows"]) != 54 or not all(r["repo_git_pit_proven"] for r in d["rows"]):
        raise RuntimeError("GPR_54_ORIGIN_GATE_FAILED")
    sys.path.insert(0, str(GOLD / "data_pipeline"))
    import broad_research_data_spine_r1_ingest as m
    os.environ["BROAD_RESEARCH_PRODUCTION_WRITE_AUTHORIZED"] = AUTH_TOKEN
    os.environ["GOLD_CONTROL_MANIFEST_VERSION"] = "1.37"
    os.environ["BROAD_RESEARCH_PREFLIGHT_HEAD_SHA"] = SOURCE_PREFLIGHT_SHA
    os.environ["BROAD_RESEARCH_PREFLIGHT_ARTIFACT_DIGEST"] = "sha256:ba4300d3501211ce7deaeea61627042f066ec45e679f672deb1741e26e102f1a"
    os.environ["GOLD_CODE_SHA"] = code_sha
    m.require_production_authority()
    bundle, summary = m.build_all(Namespace(gpr_upstream_repo=gpr_repo, gpr_coverage_json=coverage, twelve_pacing=0.0))
    if summary["series_row_counts"] != EXPECTED or summary["total_observation_rows_built"] != 71075 or summary["source_vintage_rows_built"] != 126 or summary["quality_events"] != 0:
        raise RuntimeError("FROZEN_BUNDLE_SHAPE_MISMATCH")
    if summary["sources"]["twelve_xau_hourly"]["months"] != 54 or summary["sources"]["twelve_xau_hourly"]["selected_daily_rows"] != 1177 or summary["sources"]["twelve_xau_hourly"]["min_days_per_month"] < 15:
        raise RuntimeError("TWELVE_FROZEN_GATE_FAILED")
    if summary["sources"]["gpr_companions"]["vintages"] != 54 or summary["sources"]["gpr_companions"]["origins_by_series"] != {"GPRT_OFFICIAL_GIT_PIT": 54, "GPRA_OFFICIAL_GIT_PIT": 54}:
        raise RuntimeError("GPR_COMPANION_FROZEN_GATE_FAILED")
    pre = m.verify_neon_read_only()
    if pre["decision_counts"] != {"monthly_forecast_contracts": 0, "decision_signal_snapshots": 0, "decision_runs": 0, "decision_events": 0} or pre["runtime_counts"] != {"ACTIVE": 6, "BLOCKED": 1, "WAITING": 5}:
        raise RuntimeError("PRODUCTION_PREWRITE_INVARIANT_FAILED")
    ids = sorted(EXPECTED)
    vintages = sorted({v["source_id"] for v in bundle["vintages"]})
    if len(vintages) != 126:
        raise RuntimeError("VINTAGE_ID_SET_MISMATCH")
    with psycopg.connect(m.db_url()) as conn, conn.cursor() as cur:
        cur.execute("select count(*)::bigint from observations where series_id=any(%s)", (ids,))
        obs_before = int(cur.fetchone()[0])
        cur.execute("select count(*)::bigint from source_registry where series_id=any(%s)", (ids,))
        reg_before = int(cur.fetchone()[0])
        cur.execute("select count(*)::bigint from source_vintages where source_id=any(%s)", (vintages,))
        vint_before = int(cur.fetchone()[0])
    if (obs_before, reg_before, vint_before) != (0, 0, 0):
        raise RuntimeError(f"BROAD_NAMESPACE_NOT_EMPTY:{obs_before}:{reg_before}:{vint_before}")
    result = m.persist_bundle(bundle)
    if result["observations_written"] != 71075 or result["revised_observations"] != 0 or result["registry_rows_inserted"] != 12:
        raise RuntimeError("PRODUCTION_PERSIST_COUNT_MISMATCH")
    post = m.verify_neon_read_only()
    if post != pre:
        raise RuntimeError("POSTWRITE_AUTHORITY_OR_RUNTIME_CHANGED")
    with psycopg.connect(m.db_url()) as conn, conn.cursor() as cur:
        cur.execute("select series_id,count(*)::bigint from observations where series_id=any(%s) group by series_id order by series_id", (ids,))
        counts = {sid: int(n) for sid, n in cur.fetchall()}
        cur.execute("select count(*)::bigint from source_registry where series_id=any(%s)", (ids,))
        registry_n = int(cur.fetchone()[0])
        cur.execute("select count(*)::bigint from source_vintages where source_id=any(%s)", (vintages,))
        vintage_n = int(cur.fetchone()[0])
    if counts != EXPECTED or registry_n != 12 or vintage_n != 126:
        raise RuntimeError("POSTWRITE_SOURCE_DATA_VERIFICATION_FAILED")
    return {"status": "SUCCESS", "canonical_code_sha": code_sha, "production_retrieval_run_id": result["run_id"], "series_row_counts": EXPECTED, "total_observations_written": 71075, "source_vintages_present": 126, "source_registry_rows_present": 12, "decision_counts_after": post["decision_counts"], "runtime_counts_after": post["runtime_counts"]}


def freeze_evidence(e: dict) -> None:
    p = GOLD / "GOLD_CONTROL_BROAD_RESEARCH_DATA_SPINE_R1_PRODUCTION_INGESTION_EVIDENCE_2026-09-06.md"
    lines = ["# Gold Control — Broad Research Data Spine R1 Production Ingestion Evidence", "", "**Evidence date:** 2026-09-06  ", "**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.37  ", f"**Canonical ingestion code SHA:** `{e['canonical_code_sha']}`  ", "**Binding result:** `SUCCESS_BROAD_RESEARCH_R1_PRODUCTION_SOURCE_DATA_INGESTION`", "", f"- production retrieval run: `{e['production_retrieval_run_id']}`", "- observations written: `71,075`", "- source-vintage rows: `126`", "- source-registry rows: `12`", "- revised observations: `0`", "", "## Per-series rows"]
    for sid, n in sorted(EXPECTED.items()):
        lines.append(f"- `{sid}`: `{n:,}`")
    lines += ["", "## Invariants", "- `monthly_forecast_contracts = 0`", "- `decision_signal_snapshots = 0`", "- `decision_runs = 0`", "- `decision_events = 0`", "- runtime remained `ACTIVE=6 / WAITING=5 / BLOCKED=1`", "- `AUTO_SELECTOR=OFF`", "- `AUTO_ENSEMBLE=OFF`", ""]
    p.write_text("\n".join(lines), encoding="utf-8")
    sh("git", "pull", "--ff-only", "origin", "gold-r4-direction-engine")
    sh("git", "add", str(p.relative_to(ROOT)))
    sh("git", "commit", "-m", "Freeze Broad Research R1 production ingestion evidence")
    sh("git", "push", "origin", "HEAD:gold-r4-direction-engine")


def main() -> int:
    require_env()
    stage_frozen_files()
    amend_manifest()
    code_sha = commit_authority()
    evidence = build_and_persist(code_sha)
    (ROOT / "broad_research_v137_production_ingestion_result.json").write_text(json.dumps(evidence, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    freeze_evidence(evidence)
    print(json.dumps({"status": evidence["status"], "production_retrieval_run_id": evidence["production_retrieval_run_id"], "total_observations_written": evidence["total_observations_written"], "decision_counts_after": evidence["decision_counts_after"], "runtime_counts_after": evidence["runtime_counts_after"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
