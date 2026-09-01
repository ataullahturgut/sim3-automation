from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "GOLD_CONTROL_PROJECT_MANIFEST.md"
STATUS = ROOT / "GOLD_CONTROL_STAGE4_STATUS_2026-09-01.md"
CONTRACTS = ROOT / "data_pipeline" / "source_contracts.json"
LIVE = ROOT / "apps" / "live_sources.py"
APP = ROOT / "apps" / "gold_control.py"


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"{label}: expected 1 match, got {n}")
    return text.replace(old, new, 1)


def replace_between(text: str, start_marker: str, end_marker: str, replacement: str, label: str) -> str:
    start = text.find(start_marker)
    if start < 0:
        raise RuntimeError(f"{label}: start marker not found")
    end = text.find(end_marker, start)
    if end < 0:
        raise RuntimeError(f"{label}: end marker not found")
    return text[:start] + replacement + text[end:]


# --- Manifest v1.10 ---
manifest = MANIFEST.read_text(encoding="utf-8")
manifest = replace_once(manifest, "**Manifest version:** 1.9", "**Manifest version:** 1.10", "manifest version")

live_block = """### XAU live — primary `Piyasa` display monitoring

Series: `XAU_SPOT_GOLDAPI`  
Source: Gold API (`gold-api.com`)  
Role: **indicative live display / market monitoring only**  
Status: `APPROVED_INDICATIVE_PUBLIC_DISPLAY_NO_MODEL_USE`

Frozen provider contract:

- endpoint: `GET https://api.gold-api.com/price/XAU`;
- expected symbol/currency: `XAU` / `USD`;
- required fields: positive finite `price`, parseable `updatedAt`;
- provider asks clients to cache the current-price response for 30 seconds;
- UI must show source and freshness/stale state;
- provider-managed upstream fallback is opaque, therefore this series is **not** authority-grade and is prohibited from EOD, benchmark, H=1 forecast, VW reference, Fast/Slow source, or final-decision use;
- it is not equivalent to `XAU_EOD_TWELVE_NY17`, `XAU_SPOT_XAUS`, LBMA, CME/EBS, COMEX settlement, or Yahoo/GC=F.

Authority/licensing decision record:

`gold_axis_2026/GOLD_CONTROL_LIVE_MARKET_ROADMAP_CHANGE_CONTROL_2026-09-01.md`

Operational proof: GitHub Actions run `33518757788`, job `99892357951`, `SUCCESS`; HTTP/schema/freshness were validated without logging the raw market price and without database writes.

### XAU live — legacy / secondary indicative lineage

Series: `XAU_SPOT_XAUS`  
Contract source: XAUS public API  
Role: secondary monitoring / operational cross-check; Emergency candidate only under its separately frozen role  
Status: `APPROVED_INDICATIVE_NOT_SETTLEMENT; DEGRADED_UPSTREAM_HTTP_503`

The persisted-source-label discrepancy remains `UNRESOLVED_PERSISTED_SOURCE_LABEL_DIFFERS_FROM_XAUS_CONTRACT`. `XAU_SPOT_XAUS` and `XAU_SPOT_GOLDAPI` remain separate provider lineages and may never be silently merged or relabelled.

"""
manifest = replace_between(manifest, "### XAU live\n", "### XAU daily operational history", live_block, "live source section")

manifest = manifest.replace(
    "- Canonical Twelve NY17 XAU ingestion: protected `XAU/USD` 1-minute access and exact 16:59 ET bar mapping are proven by run `33510985399`; production Neon ingestion is still `TWELVE_XAU_NY17_PIPELINE_NOT_SUCCESS` until the canonical writer completes successfully",
    "- Canonical Twelve NY17 XAU ingestion: `APPROVED_CANONICAL_PIPELINE_SUCCESS`; single-day production ingestion and PIT-safe same-lineage history backfill are proven. Historical backfill preserves actual retrieval-time availability and is not retroactively knowable.",
)

ledger_block = """## 7.2 Current forecast-ledger state

The live Neon reconcile audit (run `33518909613`, job `99892866821`, `SUCCESS`) proves:

- `forecast_input_snapshots` = **0 rows**;
- `derived_feature_snapshots` = **1 row**;
- `monthly_forecast_contracts` = **0 rows**;
- append-only mutation guards cover all three forecast-state tables (3/3).

The single derived row is `MONTHLY_DIRECTION_3M`, version `R4_1_3M_SIMPLE_RETURN_V1`, quality `LATE_BOOTSTRAP_SHADOW_CONTEXT`. It was calculated and persisted on 2026-09-01 with its true timestamps. It is **not** a prospective H=1 forecast and does not close the forecast-input or forecast-contract blockers.

Status:

`FORECAST_LEDGER_NOT_ISSUED; MONTHLY_DIRECTION_BOOTSTRAP_CONTEXT_PRESENT`

Historical closure/replay artifacts keep their original evidence class. No forecast may be relabelled as `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` unless it was issued before outcome realization with an immutable input snapshot and contract.

"""
manifest = replace_between(manifest, "## 7.2 Current forecast-ledger state", "## 7.3 Prospective-origin cutoff", ledger_block, "forecast ledger section")

manifest = replace_once(
    manifest,
    "# 23. PROJECT ROADMAP — FROZEN EXECUTION ORDER",
    "# 23. PROJECT ROADMAP — FROZEN DEPENDENCY-GATED EXECUTION",
    "roadmap title",
)

roadmap_intro = """The project roadmap is dependency-gated rather than globally linear. Model/decision claims preserve strict causal gates, while the market-monitoring surface may progress once its own data/display contract is proven.

| Stage | Deliverable | Exit criterion / dependency |
|---|---|---|
| 0 | **Production Manifest** | Read-first governance contract active |
| 1 | **Neon Data Inventory / Health Audit** | Actual inventory, freshness, quality, lineage and display policy documented |
| 2 | **Forecast Canonicalization** | Forecast target/origin and model roles unambiguous; no false prospective history |
| 3 | **Decision State Store** | Append-only decision persistence/read path present; evidence isolation enforced |
| 4A | **Current-state data/context substrate** | Canonical NY17 history sufficient; monthly direction context and Fast/Slow calculable; immutable state infrastructure proven |
| 4B | **Forecast-dependent R4.1 issuer** | Current H=1 issuer + VW reference + immutable forecast snapshot/contract + complete EngineSnapshot; first forward decision may be `PROSPECTIVE_SHADOW` |
| 5 | **Piyasa Screen** | Real live/history data only; source/freshness visible; may progress in parallel with 4B because it does not create a forecast or decision |
| 6 | **Görünüm Screen** | Real display-eligible stored decision snapshot drives explanation; no fabricated action/confidence |
| 7 | **Tahmin Screen** | Real canonical issued forecast drives display |
| 8 | **Geçmiş Screen** | Real forecast/decision ledgers; replay/prospective/live separated |
| 9 | **System Health / Audit Screen** | Full lineage/provenance/blockers exposed technically |
| 10 | **Mobile QA** | Mobile-first UX validated |
| 11 | **Prospective Shadow Run** | New forecasts/decisions stored before outcomes, immutable ledger accumulating |
| 12 | **Production Graduation** | Predefined prospective acceptance gates satisfied |

Dependency rule frozen by manifest v1.10:

- Stage 5 may proceed independently of unresolved Stage-4B forecast/VW blockers because `Piyasa` is a monitoring surface and must not infer a decision from live spot.
- Stage 6 cannot be marked complete without a display-eligible stored Decision Store state.
- Stage 7 cannot be marked complete without a canonical issued H=1 forecast.
- Stage 8 must never mix historical replay with prospective/live evidence.
- No stage may use fabricated placeholders to satisfy its own exit criterion.

Change-control record: `gold_axis_2026/GOLD_CONTROL_LIVE_MARKET_ROADMAP_CHANGE_CONTROL_2026-09-01.md`.

"""
manifest = replace_between(manifest, "The project execution order remains:", "## 23.1 Current roadmap status", roadmap_intro, "roadmap dependency block")

roadmap_status = """## 23.1 Current roadmap status — 2026-09-01

| Stage | Current status | Evidence / blocker |
|---|---|---|
| 0 | `PASS` | Manifest read-first contract active |
| 1 | `PASS_AUDIT_COMPLETE_WITH_OPERATIONAL_BLOCKERS` | Data inventory/lineage audited; XAUS remains degraded but independent sources continue |
| 2 | `PASS_CONTRACT_CANONICALIZED; FORECAST_NOT_ISSUED` | Forecast roles frozen; no prospective H=1 row exists; one late-bootstrap monthly-direction context row exists |
| 3 | `PASS_DECISION_STORE_AND_READ_PATH` | Production append-only store/read path active; no fabricated current decision |
| 4A | `PASS_CURRENT_STATE_SUBSTRATE_FOR_SHADOW_CONTEXT` | NY17 backfill SUCCESS; monthly direction bootstrap issued; Fast/Slow rehearsal SUCCESS; forecast-state append-only guards 3/3 |
| 4B | `IN_PROGRESS_BLOCKED_FORECAST_ISSUER` | Current H=1 issuer and VW monthly reference remain unresolved; forecast input snapshot/contract not issued |
| 5 | `IN_PROGRESS_LIVE_SOURCE_PROVEN_NOT_UI_COMPLETE` | `XAU_SPOT_GOLDAPI` live-display probe SUCCESS; adapter/UI integration and full history/freshness QA remain |
| 6 | `BLOCKED_NO_DISPLAY_ELIGIBLE_DECISION_SNAPSHOT` | Component rehearsals exist, but no complete forward R4.1 decision row may be fabricated |
| 7 | `BLOCKED_FORECAST_NOT_ISSUED` | Canonical H=1 forecast ledger has no issued row |
| 8–12 | `NOT_STARTED / NOT_COMPLETE` | Their own dependency gates are not satisfied |

"""
manifest = replace_between(manifest, "## 23.1 Current roadmap status — 2026-09-01", "\n---\n\n# 24. IMMEDIATE NEXT WORK", roadmap_status, "roadmap status")

manifest = replace_once(
    manifest,
    "The next canonical task is now:\n\n## `STAGE 4 — DETERMINISTIC R4.1 ISSUER: CLOSE INPUT CONTRACT BLOCKERS BEFORE ANY PROSPECTIVE WRITE`",
    "The immediate product task is now:\n\n## `STAGE 5 — PIYASA LIVE MONITORING: ACTIVATE THE PROVEN DISPLAY SOURCE WITHOUT CHANGING DECISION LOGIC`\n\nStage 4B forecast-governance work continues in parallel and remains fail-closed until its four active blockers are resolved. Piyasa progress does not authorize a forecast, final decision, action mapping, or prospective evidence claim.",
    "immediate task",
)

active_start = "Confirmed active blockers after manifest v1.8 dependency audit:"
active_end = "Temporal boundary (not a recoverable data blocker):"
active_block = """Confirmed active Stage-4B forecast blockers after manifest v1.10 reconciliation:

1. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
2. `FORECAST_CONTRACT_NOT_ISSUED`
3. `PATCH_R1_CURRENT_ISSUER_NOT_PROVEN`
   - retained Patch code is proven only through its prior August horizon and may not be date-extended by assumption.
4. `VW_CURRENT_MONTHLY_REFERENCE_NOT_ISSUED`
   - `VW_EXECUTABLE_REPRODUCTION_BLOCKED_NOT_PROVEN`; the exact original VW-MIDAS-MSVR Adapt V2 runner/source chain is not retained.

Closed current-state/context gates:

- `CANONICAL_XAU_HISTORY_BACKFILL_NOT_YET_SUCCESS` → `CLOSED_BY_RUN_33515654716`;
- `MONTHLY_DIRECTION_CONTEXT_NOT_ISSUED` → closed for **late-bootstrap shadow context only** by run `33516396253`; this does not close H=1 forecast issuance;
- Fast/Slow calculability → rehearsal `SUCCESS` by run `33516790212` (`ROBUST_UP` / `ROBUST_UP`), read-only and not a prospective forecast claim;
- forecast-state DB immutability → production append-only migration `SUCCESS` by run `33516015898`; reconcile audit run `33518909613` confirms trigger coverage 3/3.

"""
manifest = replace_between(manifest, active_start, active_end, active_block, "active blockers")

req_start = "Required next gates, in order:"
req_end = "No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` decision row may be written while any active Stage-4 readiness blocker remains open."
req_block = """Required next gates by dependency:

**Piyasa / monitoring lane (may proceed now):**

1. activate `XAU_SPOT_GOLDAPI` in the transitional live adapter with explicit source/freshness metadata;
2. smoke-test the adapter without logging raw market values;
3. keep `XAU_SPOT_XAUS` as a distinct secondary/degraded lineage; never silently merge providers;
4. keep `Canlı spot ≠ son EOD karar` visible and show `KANONİK KARAR YOK` whenever the Decision Store has no display-eligible forward state;
5. complete the real-history/freshness UI contract before Stage 5 is marked PASS.

**Stage-4B forecast/decision lane (continues fail-closed):**

1. resolve/freeze the current monthly VW reference without silent model substitution;
2. resolve the current H=1 executable point issuer with leakage-safe change control rather than extending Patch constants;
3. before the real end-September origin, issue the immutable forecast input snapshot + monthly forecast contract;
4. build/schedule the canonical R4.1 issuer only when every mandatory EngineSnapshot field has valid evidence;
5. first forward Decision Store state remains `PROSPECTIVE_SHADOW`, never retroactive and not `LIVE_PRODUCTION`.

No `PROSPECTIVE_SHADOW` or `LIVE_PRODUCTION` **decision** row may be written while an active Stage-4B blocker prevents construction of the complete frozen EngineSnapshot. This does not block non-decision `Piyasa` monitoring.
"""
manifest = replace_between(manifest, req_start, req_end, req_block, "required gates")

old_adapter = """Current live adapter contract:

- XAU spot: indicative monitoring
- XAU history: 1-year daily history
- GVZ: Cboe daily history / latest close

Do not pretend the current adapter already provides full intraday history or unlimited historical range.
"""
new_adapter = """Current live adapter contract after manifest v1.10:

- XAU spot display primary: `XAU_SPOT_GOLDAPI` — indicative monitoring only, explicit source/freshness, never model/EOD/decision input;
- XAU spot legacy/secondary: `XAU_SPOT_XAUS` — separate degraded lineage, no silent provider merge;
- XAU history: current XAUS 1-year adapter remains transitional and must be independently healthy before Stage 5 is marked PASS;
- canonical decision EOD history: `XAU_EOD_TWELVE_NY17` remains separate from the live display source;
- GVZ: Cboe daily history / latest close.

Do not pretend the current adapter already provides full intraday history or unlimited historical range. Do not use Twelve raw vendor data in a public/external display path unless the applicable subscription/display rights are separately proven.
"""
manifest = replace_once(manifest, old_adapter, new_adapter, "current live adapter contract")

MANIFEST.write_text(manifest, encoding="utf-8")

# --- Source contract ---
contracts = json.loads(CONTRACTS.read_text(encoding="utf-8"))
contracts["version"] = "GOLD_DATA_R2_2026-09-01_LIVE_GOLDAPI_V1"
series = contracts["series"]
goldapi = {
    "semantic": "XAU_SPOT",
    "tier": "C",
    "source": "Gold API (gold-api.com)",
    "symbol": "XAU",
    "frequency": "live current-price endpoint; provider requests 30-second client cache",
    "unit": "USD/oz",
    "provider_endpoint": "https://api.gold-api.com/price/XAU",
    "role": "primary Gold Control Piyasa live display / monitoring only",
    "status": "APPROVED_INDICATIVE_PUBLIC_DISPLAY_NO_MODEL_USE",
    "required_fields": ["symbol", "currency", "price", "updatedAt"],
    "freshness_policy": "fresh when updatedAt age <=300s; otherwise display STALE and do not describe as current",
    "provider_upstream_lineage": "OPAQUE_PROVIDER_MANAGED_FALLBACK",
    "model_use_allowed": False,
    "eod_use_allowed": False,
    "decision_use_allowed": False,
    "fallback_policy": "NO_SILENT_PROVIDER_MERGE; source identity must remain visible",
    "display_basis": "Gold API official docs/terms state current-price API is free and website use is supported",
    "runtime_evidence": {
        "workflow_run_id": 33518757788,
        "job_id": 99892357951,
        "result": "SUCCESS",
        "raw_market_values_logged": False,
        "database_writes": "NONE"
    },
    "not_equivalent_to": [
        "XAU_EOD_TWELVE_NY17",
        "XAU_SPOT_XAUS",
        "LBMA Gold Price AM/PM",
        "CME/EBS spot session reference",
        "COMEX GC futures settlement or Yahoo GC=F"
    ]
}
series = {"XAU_SPOT_GOLDAPI": goldapi, **{k: v for k, v in series.items() if k != "XAU_SPOT_GOLDAPI"}}
contracts["series"] = series
CONTRACTS.write_text(json.dumps(contracts, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# --- Live adapter ---
live = LIVE.read_text(encoding="utf-8")
live = replace_once(
    live,
    'XAUS_SPOT_URL = "https://xaus.com/api/v1/spot"',
    'GOLDAPI_SPOT_URL = "https://api.gold-api.com/price/XAU"\nXAUS_SPOT_URL = "https://xaus.com/api/v1/spot"',
    "live URL constants",
)
start = live.find("def fetch_xau_spot(")
end = live.find("def fetch_xau_history", start)
if start < 0 or end < 0:
    raise RuntimeError("live spot function block markers not found")
legacy = live[start:end].replace("def fetch_xau_spot(", "def fetch_xau_spot_xaus(", 1)
legacy = legacy.replace(
    '"""Indicative XAU/USD spot with explicit freshness metadata.',
    '"""Legacy XAUS indicative XAU/USD spot with explicit freshness metadata.',
    1,
)
goldapi_func = '''def fetch_xau_spot(max_response_age_seconds: int = 300) -> dict[str, Any]:
    """Gold API indicative XAU/USD display price.

    This provider is frozen for Piyasa display/monitoring only. Its upstream
    fallback lineage is provider-managed/opaque, so this function must never be
    used as the R4.1 EOD close, forecast input, VW reference, or decision input.
    """
    r = _get(GOLDAPI_SPOT_URL)
    payload = r.json()
    symbol = str(payload.get("symbol") or "").upper()
    currency = str(payload.get("currency") or "").upper()
    if symbol != "XAU":
        raise ValueError(f"Gold API symbol mismatch: {symbol!r}")
    if currency != "USD":
        raise ValueError(f"Gold API currency mismatch: {currency!r}")
    price = payload.get("price")
    if price is None:
        raise ValueError("Gold API response has no price")
    price = float(price)
    if not pd.notna(price) or price <= 0:
        raise ValueError("Gold API price is not positive finite")
    updated_at = payload.get("updatedAt")
    age = _age_seconds(updated_at)
    stale = age is None or age > max_response_age_seconds
    return {
        "price": price,
        "status": "stale" if stale else "fresh",
        "as_of": updated_at,
        "updated_at": updated_at,
        "provider_age_seconds": age,
        "response_age_seconds": age,
        "price_age_seconds": age,
        "source": "Gold API",
        "source_series": "XAU_SPOT_GOLDAPI",
        "stale": stale,
        "provider_stale": stale,
        "cache_stale": stale,
        "endpoint": GOLDAPI_SPOT_URL,
        "use_role": "INDICATIVE_DISPLAY_ONLY_NO_MODEL_USE",
        "upstream_lineage": "OPAQUE_PROVIDER_MANAGED_FALLBACK",
    }


'''
live = live[:start] + goldapi_func + legacy + live[end:]
LIVE.write_text(live, encoding="utf-8")

# App live-cache follows Gold API's documented 30-second caching instruction.
app = APP.read_text(encoding="utf-8")
app = replace_once(app, "@st.cache_data(ttl=60, show_spinner=False)\ndef live_xau()", "@st.cache_data(ttl=30, show_spinner=False)\ndef live_xau()", "app XAU cache TTL")
APP.write_text(app, encoding="utf-8")

# --- Stage 4 status v1.10 ---
STATUS.write_text("""# GOLD CONTROL — STAGE 4 DETERMINISTIC R4.1 STATUS

**Status date:** 2026-09-01  
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.10  
**Stage:** 4A/4B — Current-State Substrate + Forecast-Dependent R4.1 Issuer  
**Current status:** `4A_PASS_CURRENT_STATE_SUBSTRATE; 4B_IN_PROGRESS_BLOCKED_FORECAST_ISSUER`

## 1. Stage 4A — verified current-state substrate

- Canonical XAU EOD decision-reference series: `XAU_EOD_TWELVE_NY17`.
- PIT-safe same-lineage history backfill: run `33515654716`, `SUCCESS`.
- September monthly direction read-only rehearsal: run `33516364318`, `SUCCESS`.
- Immutable late-bootstrap monthly-direction context issuance: run `33516396253`, `SUCCESS`; evidence class `LATE_BOOTSTRAP_SHADOW_CONTEXT`; not a prospective H=1 forecast.
- Fast/Slow rehearsal: run `33516790212`, `SUCCESS`; `Fast=ROBUST_UP`, `Slow=ROBUST_UP`; read-only and not a prospective forecast/decision claim.
- Forecast-state append-only production migration: run `33516015898`, `SUCCESS`.
- Reconcile audit: run `33518909613`, job `99892866821`, `SUCCESS`: `forecast_input_snapshots=0`, `derived_feature_snapshots=1`, `monthly_forecast_contracts=0`, append-only trigger coverage 3/3.

Status: `PASS_CURRENT_STATE_SUBSTRATE_FOR_SHADOW_CONTEXT`.

## 2. Stage 4B — active forecast/issuer blockers

1. `IMMUTABLE_FORECAST_INPUT_SNAPSHOT_NOT_ISSUED`
2. `FORECAST_CONTRACT_NOT_ISSUED`
3. `PATCH_R1_CURRENT_ISSUER_NOT_PROVEN`
4. `VW_CURRENT_MONTHLY_REFERENCE_NOT_ISSUED` / `VW_EXECUTABLE_REPRODUCTION_BLOCKED_NOT_PROVEN`

No complete frozen `EngineSnapshot` may be emitted as a forward R4.1 decision while these blockers prevent construction of the required monthly forecast/reference fields.

## 3. Prospective-origin boundary

`SEPTEMBER_2026_H1_PROSPECTIVE_ORIGIN_MISSED` remains binding. No 1-September reconstruction may be backdated to 31-August. The first fully contract-compliant prospective H=1 target remains October 2026 with end-September origin, provided Stage-4B forecast blockers are closed before issuance.

## 4. Piyasa lane unlocked by manifest v1.10

Live market monitoring is not a forecast or decision claim and may proceed independently of Stage 4B.

Primary Piyasa live-display source:

`XAU_SPOT_GOLDAPI`

Gold API probe run `33518757788`, job `99892357951`: `SUCCESS`; schema/freshness validated, no raw price logged, no DB write.

Rules:

- indicative display/monitoring only;
- source/freshness must be visible;
- provider-managed upstream fallback is opaque, therefore no model/EOD/decision use;
- `XAU_SPOT_XAUS` remains a separate degraded legacy lineage;
- `Canlı spot ≠ son EOD karar` remains explicit;
- no display-eligible Decision Store row => UI must show `KANONİK KARAR YOK`.

## 5. Immediate next work

1. activate `XAU_SPOT_GOLDAPI` in the transitional live adapter and run a no-raw-value app/source smoke;
2. continue Stage-4B VW/H=1 issuer change-control in parallel;
3. do not mark `Görünüm` complete until a display-eligible stored forward decision exists;
4. do not mark `Tahmin` complete until a canonical issued H=1 forecast exists;
5. first complete forward Decision Store state remains `PROSPECTIVE_SHADOW`; `LIVE_PRODUCTION` stays disabled and `action_state` stays NULL under `NOT_PROVEN_POSITION_MAPPING`.

Change-control: `gold_axis_2026/GOLD_CONTROL_LIVE_MARKET_ROADMAP_CHANGE_CONTROL_2026-09-01.md`.
""", encoding="utf-8")

print("MANIFEST_V1_10_LIVE_MARKET_APPLY_PASS")
