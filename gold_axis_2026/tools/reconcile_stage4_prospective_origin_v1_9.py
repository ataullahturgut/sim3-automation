from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
CANON = ROOT / "GOLD_CONTROL_FORECAST_CANONICALIZATION.md"
STAGE4 = ROOT / "GOLD_CONTROL_STAGE4_STATUS_2026-09-01.md"


def must_replace(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"MISSING_EXPECTED_TEXT:{label}")
    return text.replace(old, new, 1)


def main() -> int:
    manifest = MANIFEST.read_text()
    canon = CANON.read_text()
    stage4 = STAGE4.read_text()

    manifest = must_replace(
        manifest,
        "**Manifest version:** 1.8  ",
        "**Manifest version:** 1.9  ",
        "manifest_version",
    )

    ledger_anchor = "Status:\n\n`PROSPECTIVE_FORECAST_LEDGER_PROVEN_EMPTY`\n\nThis means model/contract canonicalization is complete, but no current Neon forecast row may be relabeled as `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION`. Historical closure/replay artifacts keep their original evidence class."
    ledger_replacement = ledger_anchor + "\n\n## 7.3 Prospective-origin cutoff — September 2026\n\nThe frozen H=1 contract requires the forecast origin to be the **end of the previous completed calendar month**. The current Neon forecast ledger was still empty after the `2026-08-31` origin had passed, and the first canonical NY17 production observation/backfill work occurred on `2026-09-01`.\n\nTherefore a forecast first created on `2026-09-01` must **not** be backdated to `2026-08-31` or described as a contract-compliant prospective September H=1 issuance.\n\nStatus: `SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED`.\n\nThe first target still eligible to become a fully contract-compliant prospective H=1 forecast under the frozen origin rule is **October 2026**, with origin at the end of **2026-09-30**, subject to all model/input/provenance blockers being resolved before issuance.\n\nA September monthly direction or R4.1 initialization computed now may only be stored as an explicitly labelled **late bootstrap/shadow context** using its true retrieval/calculation timestamp. Such a bootstrap context does not close the H=1 forecast issuance blocker and may not be presented as a 31-August prospective forecast."
    manifest = must_replace(manifest, ledger_anchor, ledger_replacement, "manifest_origin_cutoff")

    manifest = must_replace(
        manifest,
        "| 4 | `IN_PROGRESS_BLOCKED_FORECAST_AND_MONTHLY_CONTEXT` | Deterministic engine/bridge tests PASS and latest canonical NY17 ingestion PASS. Deeper audit proves current Patch issuer is only frozen through the August target, exact VW production runner remains `BLOCKED_NOT_PROVEN`, R4.1 monthly VW/direction inputs are not issued, forecast snapshot/contract tables are empty, and canonical NY17 history backfill is not yet successful |",
        "| 4 | `IN_PROGRESS_BLOCKED_FORECAST_AND_MONTHLY_CONTEXT` | Deterministic engine/bridge tests PASS and latest canonical NY17 ingestion PASS. September H=1 prospective origin was missed because the ledger was empty after 31-Aug; first fully contract-compliant prospective H=1 target is October 2026. Current Patch issuer is only frozen through August, exact VW production runner remains `BLOCKED_NOT_PROVEN`, R4.1 monthly VW/direction inputs are not issued, and canonical NY17 history backfill is still being completed |",
        "manifest_stage4_row",
    )

    blocker_anchor = "6. `CANONICAL_XAU_HISTORY_BACKFILL_NOT_YET_SUCCESS`\n   - one canonical NY17 production observation exists, but Fast/Slow and 3M monthly context require a longer same-lineage history. A PIT-safe backfill is being validated; historical rows retain current retrieval-time availability and are never relabelled as historically knowable."
    blocker_replacement = blocker_anchor + "\n\nTemporal boundary (not a recoverable data blocker):\n\n`SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED` — the frozen 31-August origin passed while the canonical forecast ledger was empty. No reconstruction performed on 1-September or later may be relabelled as a 31-August prospective issuance."
    manifest = must_replace(manifest, blocker_anchor, blocker_replacement, "manifest_temporal_boundary")

    required_old = "5. only after the chosen executable forecast path is proven, create the first genuine immutable input snapshot and matching monthly forecast contract with actual issuance timestamp and complete provenance;\n6. verify forecast/monthly-context rows in Neon before target outcome realization;\n7. only then build/schedule the canonical R4.1 EOD issuer; first forward decision state = `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`."
    required_new = "5. do not manufacture a September H=1 prospective row: its contractual 31-August origin has passed; the first fully contract-compliant prospective H=1 target is October 2026 with origin at end-September;\n6. before that October origin, prove/freeze the executable forecast path and required inputs so the immutable input snapshot + monthly forecast contract can be issued at the real origin timestamp;\n7. a September direction/R4.1 initialization, if operationally useful, may only be an explicitly labelled late bootstrap/shadow context using true retrieval/calculation timestamps and must not close the H=1 forecast blocker;\n8. verify every issued forecast/monthly-context row in Neon before the corresponding outcome realization;\n9. build/schedule the canonical R4.1 EOD issuer only when all mandatory `EngineSnapshot` inputs have valid evidence labels; first forward decision state = `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`."
    manifest = must_replace(manifest, required_old, required_new, "manifest_required_gates")

    canon = must_replace(
        canon,
        "**Canonicalization version:** 1.2  ",
        "**Canonicalization version:** 1.3  ",
        "canon_version",
    )
    canon_append = """

---

# 13. PROSPECTIVE ORIGIN CUT-OFF — 2026-09-01

The canonical H=1 contract defines the forecast origin as the **end of the previous completed calendar month**.

The Neon forecast-state reconciliation proves that the immutable forecast ledger remained empty after the `2026-08-31` origin had passed. Accordingly, a September 2026 forecast first computed or persisted on `2026-09-01` cannot be backdated or labelled as a contract-compliant prospective forecast from 31 August.

Status:

`SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED`

Consequences:

1. No reconstructed September forecast may be labelled `PROSPECTIVE_SHADOW` with a 31-August origin.
2. Any September initialization produced after this audit must use its true issuance/retrieval timestamp and an explicit late-bootstrap/shadow label.
3. Such a bootstrap does not satisfy the canonical H=1 prospective issuance requirement.
4. The first target still eligible for a fully contract-compliant prospective H=1 issuance is **October 2026**, with origin at the end of `2026-09-30`, assuming the executable model path, point-in-time inputs, immutable snapshot, and forecast contract are all ready by that origin.
5. This temporal boundary does not authorize a model substitution or relaxation of VW/Patch provenance blockers.
"""
    if "# 13. PROSPECTIVE ORIGIN CUT-OFF — 2026-09-01" not in canon:
        canon = canon.rstrip() + canon_append + "\n"

    stage4 = must_replace(
        stage4,
        "**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.8  ",
        "**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.9  ",
        "stage4_manifest_version",
    )
    stage4 = must_replace(
        stage4,
        "## 5. Active readiness blockers — manifest v1.8",
        "## 5. Active readiness blockers — manifest v1.9",
        "stage4_blocker_heading",
    )
    stage4_append = """

## 8. Prospective-origin cutoff

The canonical H=1 origin is the end of the previous completed calendar month. The forecast ledger remained empty after the 31-August-2026 origin had passed. Therefore:

`SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED`

This is a temporal evidence boundary, not a data value to reconstruct. A September forecast created now may not be backdated or labelled as a 31-August prospective issuance. The first fully contract-compliant prospective H=1 target remains **October 2026**, origin end-September, subject to the current issuer/VW/input blockers being closed by then.

A September 3M direction or R4.1 initialization may be created only as an explicitly labelled late bootstrap/shadow context with its true calculation and data-availability timestamps. It does not close the H=1 forecast issuance blocker.
"""
    if "## 8. Prospective-origin cutoff" not in stage4:
        stage4 = stage4.rstrip() + stage4_append + "\n"

    MANIFEST.write_text(manifest)
    CANON.write_text(canon)
    STAGE4.write_text(stage4)

    print("MANIFEST_VERSION=1.9")
    print("CANONICALIZATION_VERSION=1.3")
    print("SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED=TRUE")
    print("FIRST_FULLY_COMPLIANT_PROSPECTIVE_H1_TARGET=2026-10")
    print("FIRST_FULLY_COMPLIANT_PROSPECTIVE_H1_ORIGIN=2026-09-30_END_OF_MONTH")
    print("RECONCILE_STAGE4_PROSPECTIVE_ORIGIN_V1_9_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
