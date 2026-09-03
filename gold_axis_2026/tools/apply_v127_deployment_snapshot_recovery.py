from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / "apps"


def replace_once(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"EXPECTED_EXACTLY_ONE_MATCH:{path}:{count}:{old[:80]}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def patch_decision_source() -> None:
    path = APPS / "decision_source.py"
    replace_once(
        path,
        "from psycopg.rows import dict_row\n\n\nGOLD_ROOT",
        "from psycopg.rows import dict_row\n\nfrom production_display_snapshot import (\n"
        "    SNAPSHOT_CONTRACT,\n"
        "    SNAPSHOT_SOURCE_MODE,\n"
        "    load_production_display_snapshot,\n"
        "    snapshot_feature_rows,\n"
        ")\n\n\nGOLD_ROOT",
    )
    marker = "\ndef fetch_current_decision_state(database_url: str) -> dict[str, Any] | None:\n"
    helper = '''\ndef _read_snapshot_shadow_direction_context() -> dict[str, Any] | None:\n    snapshot = load_production_display_snapshot()\n    context = _shape_shadow_direction_context(snapshot_feature_rows(snapshot))\n    if context is None:\n        raise RuntimeError("PRODUCTION_DISPLAY_SNAPSHOT_CONTEXT_EMPTY")\n    context["source_mode"] = SNAPSHOT_SOURCE_MODE\n    context["snapshot_contract"] = SNAPSHOT_CONTRACT\n    context["snapshot_source_state_at"] = snapshot.get("source_state_at")\n    context["snapshot_payload_sha256"] = snapshot.get("payload_sha256")\n    return context\n\n\ndef _read_db_current_decision_state(url: str) -> dict[str, Any] | None:\n    with psycopg.connect(url, autocommit=False) as conn:\n        with conn.cursor() as cur:\n            cur.execute("SET TRANSACTION READ ONLY")\n        for evidence_class in DISPLAY_EVIDENCE_ORDER:\n            row = read_latest_decision(conn, evidence_class)\n            if row is None:\n                continue\n            if row.get("action_state") is not None:\n                raise RuntimeError("NOT_PROVEN_POSITION_MAPPING_VIOLATION")\n            result = _to_transitional_app_shape(row)\n            if result.get("evidence_class") != evidence_class:\n                raise RuntimeError("DECISION_EVIDENCE_CLASS_MISMATCH")\n            result["source_mode"] = "NEON_DB_READ_ONLY"\n            conn.rollback()\n            return result\n        context = _read_shadow_direction_context(conn)\n        if context is not None:\n            context["source_mode"] = "NEON_DB_READ_ONLY"\n        conn.rollback()\n        return context\n\n'''
    text = path.read_text(encoding="utf-8")
    if helper.strip() in text:
        raise RuntimeError("DECISION_SNAPSHOT_HELPER_ALREADY_PRESENT")
    if marker not in text:
        raise RuntimeError("DECISION_FETCH_MARKER_NOT_FOUND")
    text = text.replace(marker, helper + marker, 1)
    old_start = '''def fetch_current_decision_state(database_url: str) -> dict[str, Any] | None:\n    """Read current display state without inventing a final decision.\n\n    Priority is the governed Decision Store: LIVE_PRODUCTION, then\n    PROSPECTIVE_SHADOW. When neither exists, the function may return already\n    persisted Stage-4A direction/tactical/GVZ component context with\n    ``context_only=True``. Missing one component never suppresses other\n    available components. Emergency, BOCPD and Macro remain explicit blockers\n    until their own governed forward contracts are satisfied.\n    """\n    url = str(database_url or "").strip()\n    if not url:\n        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")\n\n    with psycopg.connect(url, autocommit=False) as conn:\n        with conn.cursor() as cur:\n            cur.execute("SET TRANSACTION READ ONLY")\n        for evidence_class in DISPLAY_EVIDENCE_ORDER:\n            row = read_latest_decision(conn, evidence_class)\n            if row is None:\n                continue\n            if row.get("action_state") is not None:\n                raise RuntimeError("NOT_PROVEN_POSITION_MAPPING_VIOLATION")\n            result = _to_transitional_app_shape(row)\n            if result.get("evidence_class") != evidence_class:\n                raise RuntimeError("DECISION_EVIDENCE_CLASS_MISMATCH")\n            conn.rollback()\n            return result\n        context = _read_shadow_direction_context(conn)\n        conn.rollback()\n        return context\n'''
    new_start = '''def fetch_current_decision_state(database_url: str) -> dict[str, Any] | None:\n    """Read current governed display state with a validated deployment fallback.\n\n    Neon remains primary. A missing URL or operational connectivity failure may\n    use the frozen production display snapshot. Governance/schema violations are\n    never converted into fallback data.\n    """\n    url = str(database_url or "").strip()\n    if not url:\n        return _read_snapshot_shadow_direction_context()\n    try:\n        return _read_db_current_decision_state(url)\n    except psycopg.OperationalError:\n        return _read_snapshot_shadow_direction_context()\n'''
    count = text.count(old_start)
    if count != 1:
        raise RuntimeError(f"DECISION_FETCH_BLOCK_MATCH_COUNT:{count}")
    path.write_text(text.replace(old_start, new_start, 1), encoding="utf-8")


def patch_runtime_source() -> None:
    path = APPS / "runtime_source.py"
    text = path.read_text(encoding="utf-8")
    text = text.replace(
        "from psycopg.rows import dict_row\n\n\nRUNTIME_SOURCE_CONTRACT",
        "from psycopg.rows import dict_row\n\nfrom production_display_snapshot import (\n"
        "    load_production_display_snapshot,\n"
        "    snapshot_runtime_observability,\n"
        ")\n\n\nRUNTIME_SOURCE_CONTRACT",
        1,
    )
    if "snapshot_runtime_observability" not in text:
        raise RuntimeError("RUNTIME_SNAPSHOT_IMPORT_PATCH_FAILED")
    old = '''def fetch_runtime_observability(database_url: str) -> dict[str, Any]:\n    """Read Data Evidence Spine runtime/health state without recomputation.\n\n    This source is observability-only. It cannot create forecasts, direction values,\n    selector weights, decisions, or actions. Component values continue to come from\n    their governed immutable output ledgers.\n    """\n    url = str(database_url or "").strip()\n    if not url:\n        raise RuntimeError("NEON_DATABASE_URL_NOT_CONFIGURED")\n\n    with psycopg.connect(url, autocommit=False, row_factory=dict_row) as conn:\n'''
    new = '''def fetch_runtime_observability(database_url: str) -> dict[str, Any]:\n    """Read runtime/health without recomputation; Neon primary, snapshot fallback."""\n    url = str(database_url or "").strip()\n    if not url:\n        return snapshot_runtime_observability(load_production_display_snapshot())\n\n    try:\n        conn_ctx = psycopg.connect(url, autocommit=False, row_factory=dict_row)\n    except psycopg.OperationalError:\n        return snapshot_runtime_observability(load_production_display_snapshot())\n\n    with conn_ctx as conn:\n'''
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"RUNTIME_FETCH_HEADER_MATCH_COUNT:{count}")
    text = text.replace(old, new, 1)
    old_return = '''        "database_writes": "NONE",\n    }\n'''
    new_return = '''        "database_writes": "NONE",\n        "source_mode": "NEON_DB_READ_ONLY",\n        "snapshot_contract": None,\n        "snapshot_source_state_at": None,\n        "snapshot_payload_sha256": None,\n    }\n'''
    # Replace only the final return, not the earlier schema-block return.
    index = text.rfind(old_return)
    if index < 0:
        raise RuntimeError("RUNTIME_FINAL_RETURN_NOT_FOUND")
    text = text[:index] + new_return + text[index + len(old_return):]
    path.write_text(text, encoding="utf-8")


def patch_mobile_app() -> None:
    path = APPS / "gold_control_mobile_v1.py"
    text = path.read_text(encoding="utf-8")
    old = '''url=db_url()\ndecision=safe_call(lambda:fetch_current_decision_state(url),None) if url else None\ndecision_rows=safe_call(lambda:fetch_decision_history(url),[]) if url else []\nruntime_obs=safe_call(lambda:fetch_runtime_observability(url),None) if url else None\nforecast=safe_call(lambda:fetch_current_forecast(url),None) if url else None\n'''
    new = '''url=db_url()\ndecision=safe_call(lambda:fetch_current_decision_state(url),None)\ndecision_rows=safe_call(lambda:fetch_decision_history(url),[]) if url else []\nruntime_obs=safe_call(lambda:fetch_runtime_observability(url),None)\nforecast=safe_call(lambda:fetch_current_forecast(url),None) if url else None\n'''
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"MOBILE_CORE_SOURCE_MATCH_COUNT:{count}")
    text = text.replace(old, new, 1)
    old_spine = '''    if runtime_obs:\n        spine_ok=runtime_obs.get("status")=="DATA_EVIDENCE_SPINE_RUNTIME_HEALTH_PASS"\n        spine_summary=(\n            f"DB Evidence Spine: runtime {runtime_obs.get('runtime_engine_count',0)}/12 · "\n            f"context link {runtime_obs.get('context_exactly_one_link',0)}/{runtime_obs.get('context_expected',7)} · "\n            f"integrity {'PASS' if spine_ok else 'BLOCKED'}"\n        )\n    else:\n        spine_summary="DB Evidence Spine: KULLANILAMIYOR"\n'''
    new_spine = '''    if runtime_obs:\n        spine_ok=runtime_obs.get("status")=="DATA_EVIDENCE_SPINE_RUNTIME_HEALTH_PASS"\n        source_mode=display_state(runtime_obs.get("source_mode"),"UNKNOWN_SOURCE")\n        source_label="DB Evidence Spine" if source_mode=="NEON_DB_READ_ONLY" else "Production Evidence Snapshot · FALLBACK"\n        spine_summary=(\n            f"{source_label}: runtime {runtime_obs.get('runtime_engine_count',0)}/12 · "\n            f"context link {runtime_obs.get('context_exactly_one_link',0)}/{runtime_obs.get('context_expected',7)} · "\n            f"integrity {'PASS' if spine_ok else 'BLOCKED'}"\n        )\n        if source_mode=="PRODUCTION_SNAPSHOT_FALLBACK" and runtime_obs.get("snapshot_source_state_at"):\n            spine_summary += f" · state {fmt_time(runtime_obs.get('snapshot_source_state_at'))}"\n    else:\n        spine_summary="Production Evidence: BLOCKED · DB ve doğrulanmış snapshot kullanılamıyor"\n'''
    count = text.count(old_spine)
    if count != 1:
        raise RuntimeError(f"MOBILE_SPINE_SUMMARY_MATCH_COUNT:{count}")
    text = text.replace(old_spine, new_spine, 1)
    path.write_text(text, encoding="utf-8")


def patch_entrypoint() -> None:
    path = APPS / "gold_control.py"
    old = '''_load_exact_module(\n    "decision_source",\n    APP_DIR / "decision_source.py",\n    required_exports=("fetch_current_decision_state", "fetch_decision_history"),\n)\n'''
    new = '''_load_exact_module(\n    "production_display_snapshot",\n    APP_DIR / "production_display_snapshot.py",\n    required_exports=(\n        "load_production_display_snapshot",\n        "snapshot_feature_rows",\n        "snapshot_runtime_observability",\n    ),\n)\n_load_exact_module(\n    "decision_source",\n    APP_DIR / "decision_source.py",\n    required_exports=("fetch_current_decision_state", "fetch_decision_history"),\n)\n'''
    replace_once(path, old, new)


def patch_manifest() -> None:
    path = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
    text = path.read_text(encoding="utf-8")
    if "FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V1" in text:
        raise RuntimeError("MANIFEST_V127_ALREADY_PRESENT")
    if text.count("**Manifest version:** 1.26") != 1:
        raise RuntimeError("MANIFEST_V126_HEADER_NOT_UNIQUE")
    text = text.replace("**Manifest version:** 1.26", "**Manifest version:** 1.27", 1)
    text += '''\n\n## v1.27 — Deployment Display Snapshot Recovery\n\n- Frozen contract: `FROZEN_PRODUCTION_DISPLAY_SNAPSHOT_V1`.\n- Neon remains the primary immutable state/evidence authority and is read with `SET TRANSACTION READ ONLY`.\n- `apps/production_display_snapshot.json` is a fingerprint-validated display-only replica for a hosting environment where `NEON_DATABASE_URL` is absent or operationally unreachable.\n- The snapshot is restricted to 12 governed runtime states, seven persisted display context features and evidence-spine health counters; it carries no credentials, selector weights, canonical forecast, final classification or action mapping.\n- Snapshot fallback is explicitly labelled `PRODUCTION_SNAPSHOT_FALLBACK`; it may not masquerade as a direct DB read.\n- A DB/schema/governance violation remains fail-closed and is not hidden by fallback.\n- Deployment regression requires the no-DB-URL browser path to show the persisted Monthly/FAST/SLOW/GVZ context instead of falsely reporting `NO_CURRENT_EVIDENCE`.\n- Locks retained: `NOT_PROVEN_EXPERT_SELECTION_RULE`, `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, `NOT_PROVEN_POSITION_MAPPING`.\n'''
    path.write_text(text, encoding="utf-8")


def main() -> int:
    patch_decision_source()
    patch_runtime_source()
    patch_mobile_app()
    patch_entrypoint()
    patch_manifest()
    print("V127_DEPLOYMENT_SNAPSHOT_RECOVERY_PATCH_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
