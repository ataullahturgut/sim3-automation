from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AUDIT = ROOT / "audits" / "GOLD_CONTROL_LIVE_DB_INVENTORY.json"
OUT = ROOT.parent / "GOLD_CONTROL_DATA_INVENTORY.md"


def _s(value):
    return "—" if value in (None, "") else str(value)


def _short(value, limit=42):
    text = _s(value).replace("|", "/")
    return text if len(text) <= limit else text[: limit - 1] + "…"


def main() -> int:
    data = json.loads(AUDIT.read_text(encoding="utf-8"))
    rows = data.get("inventory", [])
    degraded = [r for r in rows if str(r.get("freshness_state", "")).startswith(("DEGRADED", "STALE"))]
    unresolved = [r for r in rows if "UNRESOLVED" in str(r.get("blocker_note", ""))]
    stage_status = "PASS_AUDIT_COMPLETE"
    if degraded or unresolved:
        stage_status = "PASS_AUDIT_COMPLETE_WITH_OPERATIONAL_BLOCKERS"

    lines = [
        "# GOLD CONTROL — DATA INVENTORY / HEALTH AUDIT",
        "",
        f"**Inventory version:** 2.0  ",
        f"**Generated at (UTC):** `{_s(data.get('generated_at_utc'))}`  ",
        "**Evidence:** direct read-only Neon query executed by protected GitHub Actions; transaction rolled back  ",
        f"**Stage 1 status:** `{stage_status}`  ",
        "",
        "---",
        "",
        "## 1. Audit contract",
        "",
        "This file is generated from the actual Neon data plane plus the database `source_registry`. It contains metadata only; observation values, provider payloads, secrets and quality-event messages are excluded.",
        "",
        "Historical reconstruction remains governed by `observations_as_of(origin_ts)` / immutable snapshots. Current-state views never prove what was knowable at an old forecast origin.",
        "",
        "## 2. Current database inventory",
        "",
        "| Series | Semantic | Tier | Contract source | Actual latest source | Role | Display | Model/status | First obs | Last obs | First retrieval | Last retrieval | Rows | Pipeline health | PIT / blocker |",
        "|---|---|---:|---|---|---|---|---|---|---|---|---|---:|---|---|",
    ]

    for r in rows:
        lines.append(
            "| " + " | ".join([
                f"`{_short(r.get('series_id'), 32)}`",
                _short(r.get("semantic_id"), 20),
                _short(r.get("source_tier"), 5),
                _short(r.get("contract_source"), 30),
                _short(r.get("actual_latest_source"), 28),
                _short(r.get("model_role"), 30),
                _short(r.get("display_policy"), 24),
                _short(r.get("model_use_status"), 34),
                _short(r.get("first_observation_ts"), 20),
                _short(r.get("last_observation_ts"), 20),
                _short(r.get("first_retrieval_ts"), 20),
                _short(r.get("last_retrieval_ts"), 20),
                _s(r.get("observation_count")),
                _short(r.get("freshness_state"), 28),
                _short("; ".join(x for x in [r.get("pit_note"), r.get("blocker_note")] if x), 54),
            ]) + " |"
        )

    lines += [
        "",
        "## 3. Operational findings",
        "",
        f"- Persisted/current series in `usable_observations`: **{sum(1 for r in rows if r.get('observation_count'))}**.",
        f"- Registered series with no current usable rows: **{sum(1 for r in rows if not r.get('observation_count'))}**.",
        f"- Degraded/stale mapped series: **{len(degraded)}**.",
        f"- Explicit unresolved lineage/blocker notes: **{len(unresolved)}**.",
        "- A provider failure is not repaired by silent substitution. A failed latest run remains visible as degraded health while unrelated provider jobs may continue independently.",
        "",
        "### Latest source-job states",
        "",
        "| Job | Status | Started | Finished | Read | Written |",
        "|---|---|---|---|---:|---:|",
    ]
    for name, run in sorted((data.get("latest_source_runs") or {}).items()):
        lines.append(
            f"| `{name}` | `{_s(run.get('status'))}` | {_s(run.get('started_at'))} | {_s(run.get('finished_at'))} | {_s(run.get('observations_read'))} | {_s(run.get('observations_written'))} |"
        )

    fs = data.get("forecast_store_audit") or {}
    lines += [
        "",
        "## 4. Forecast-state database audit",
        "",
        "This section is metadata-only and is included because Stage 2 depends on proving whether immutable forecast-state objects actually contain issued records.",
        "",
        "| Object | Exists | Row count | Columns / temporal evidence |",
        "|---|---|---:|---|",
    ]
    for name, meta in sorted(fs.items()):
        lines.append(
            f"| `{name}` | `{_s(meta.get('exists'))}` | {_s(meta.get('row_count'))} | {_short(', '.join(meta.get('columns') or []), 90)} |"
        )

    lines += [
        "",
        "## 5. Quality and point-in-time status",
        "",
        f"- Quality ERROR events recorded in the append-only ledger: **{_s((data.get('quality_event_summary') or {}).get('quality_error_events'))}**.",
        f"- Quality WARNING events: **{_s((data.get('quality_event_summary') or {}).get('quality_warning_events'))}**.",
        "- Historical backfills retain the first-retrieval floor unless historical publication/vintage timing is independently reconstructed.",
        "- `canonical_latest` and `usable_observations` are current-state surfaces only.",
        "- Licensed/vendor raw display restrictions remain binding even when the series is healthy in Neon.",
        "",
        "## 6. Stage 1 closure",
        "",
        f"**Decision:** `{stage_status}`",
        "",
        "Stage 1 is considered audit-complete because the required current inventory fields are now produced from an actual read-only Neon query. Operational source failures or lineage discrepancies remain explicit blockers; they do not invalidate the inventory itself and are not hidden by proxy substitution.",
        "",
        "The next roadmap work is Stage 2 reconciliation of the forecast-state store, followed only then by Stage 3 decision-state persistence.",
        "",
    ]

    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"RENDER_OK rows={len(rows)} status={stage_status} output={OUT.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
