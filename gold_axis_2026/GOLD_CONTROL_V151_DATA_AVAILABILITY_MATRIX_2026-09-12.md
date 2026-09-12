# Gold Control V1.51 — Data Availability and Evidence Matrix

**Snapshot date:** 2026-09-12  
**Purpose:** Phase-A inventory for the V1.51 Master Orchestrator  
**Evidence:** current Neon inventory queried on 2026-09-12 + canonical manifest role/source contracts  
**Production authority:** none

## 1. Core market clocks

| Source | Rows / coverage observed | First timestamp | Last timestamp | V1.51 use |
|---|---:|---|---|---|
| `xau_intraday_research_cache_1m` | 1,330,943 rows | 2023-01-02 23:00Z | 2026-06-30 23:59Z | historical event/general research; not sufficient alone for post-June 2026 prospective 1m event targets |
| `xau_intraday_research_cache_5m` | 482,734 rows | 2020-04-06 00:00Z | 2026-08-31 23:55Z | Market Shock / intraday research through Aug-2026 |
| `XAU_EOD_TWELVE_NY17` | 55 persisted observations in current table | 2026-05-29 21:00Z | 2026-09-11 21:00Z | canonical tactical current XAU reference; earlier history may exist via governed reconstruction lanes rather than this current persisted slice |

**Rule:** absence of a current persisted row is not permission to synthesize or forward-fill a governed XAU reference.

## 2. PIT macro-financial series

| Series | N | First | Last | Availability interpretation |
|---|---:|---|---|---|
| `DGS10_ALFRED_PIT_ME` | 128 | 2016-01-31 | 2026-08-31 | eligible PIT monthly rates input |
| `DFF_ALFRED_PIT_ME` | 128 | 2016-01-31 | 2026-08-31 | eligible PIT policy-rate input |
| `DEXCHUS_ALFRED_PIT_ME` | 128 | 2016-01-31 | 2026-08-31 | eligible PIT FX input |

These are preferred over late-starting direct series for historical V1.51 rate/FX reconstruction.

## 3. Equity / cross-market series

| Series | N | Economic-date first | Economic-date last | Retrieval/lineage caveat |
|---|---:|---|---|---|
| `NASDAQ100_FRED` | 10,254 | 1986-01-02 | 2026-09-11 | historical economic dates long; current database retrieval is recent, so old economic dates are not automatically prospective PIT proof |
| `SP500_FRED` | 2,523 | 2016-08-29 | 2026-09-11 | same lineage caveat |
| `DJIA_FRED` | 2,523 | 2016-08-29 | 2026-09-11 | same lineage caveat |

V1.51 may use these as historical-research reconstruction only under explicit evidence labeling unless origin-time availability is independently proven.

## 4. Precious-metal cross-market series

| Series | N | Economic-date first | Economic-date last | Retrieval caveat |
|---|---:|---|---|---|
| `XAG_STAKTRAKR_RESEARCH_DAILY_R1` | 4,230 | 2010-01-04 | 2026-07-31 | research backfill retrieved in Sep-2026; historical economic date != historical prospective availability |
| `XPT_STAKTRAKR_RESEARCH_DAILY_R1` | 4,229 | 2010-01-04 | 2026-07-31 | same |
| `XPD_STAKTRAKR_RESEARCH_DAILY_R1` | 4,229 | 2010-01-04 | 2026-07-31 | same |

## 5. Volatility / risk series

| Series | N | First | Last | V1.51 role |
|---|---:|---|---|---|
| `GVZ_CBOE` | 249 | 2026-03-10 | 2026-09-11 | live/current risk context only for dates where actually available; not backfilled into 2025 or early-2026 validation origins |
| `VIX_CBOE` | 250 | 2026-03-13 | 2026-09-11 | current volatility context where applicable; not a fabricated historical feature |

The canonical manifest defines `GVZ_RISK` as risk context only, never a gold-direction vote.

## 6. Macro Event series

| Series | N | First event | Last event in current inventory | V1.51 use |
|---|---:|---|---|---|
| `MACRO_EVENT_V3_EMPLOYMENT_SCORE` | 102 | 2018-02-02 13:30Z | 2026-09-04 12:30Z | event specialist research / future frozen event shadow |
| `MACRO_EVENT_V3_INFLATION_SCORE` | 101 | 2018-02-14 13:30Z | 2026-08-12 12:30Z | event specialist research / future frozen event shadow |
| `MACRO_EVENT_V3_FOMC_SCORE` | 91 | 2016-01-27 19:00Z | 2026-07-29 18:00Z | historical research only unless release-time availability semantics are independently satisfied; current inventory shows late common availability metadata for historical FOMC score rows |

The event specialist must preserve release/vintage semantics and may not backdate reconstructed score availability.

## 7. Current governed engine state inventory relevant to V1.51

Current runtime surface queried on 2026-09-12 shows these relevant governed identities present:

- `VW_MIDAS_MSVR_SUCCESSOR_V1` — ACTIVE historical-replay current-month reference; prospective source readiness remains a separate gate.
- `MONTHLY_DIRECTION_3M` — ACTIVE strategic direction context.
- `FAST` — ACTIVE tactical context.
- `SLOW` — ACTIVE tactical context.
- `MACRO_EVENT_SUCCESSOR_V2` — ACTIVE event-risk context; no automatic action.
- `BOCPD_RETURN_SUCCESSOR_V1` — ACTIVE regime-break context; no direction vote.
- `EMERGENCY_LEVEL` — ACTIVE emergency context.
- `EMERGENCY_REVERSAL` — ACTIVE emergency context.
- `GVZ_RISK` — ACTIVE risk-only context.

The archived predecessor identities `BOCPD` and `MACRO_EVENT` remain blocked/replaced and must not be accidentally reactivated by the Master Orchestrator.

## 8. Availability policy for 2025 validation / 2026 locked test

For each origin `t`:

```text
IF source_or_engine_is_legitimate_at(t):
    eligible = TRUE
ELSE:
    eligible = FALSE
    contribution = NOT_APPLICABLE or BLOCKED
```

Missing data is never encoded as a neutral directional vote.

Examples:

- GVZ is absent from 2025 validation and from 2026 origins before its legitimate series start.
- Macro Event contributes only on eligible event origins.
- Market Shock contributes only after enough intraday bars exist to observe the shock state; it cannot be back-propagated to release time.
- Cross-market historical backfills may be used for labelled retrospective research if allowed by the frozen contract, but cannot be relabelled as genuine old-origin prospective evidence.
- MIDAS/MSVR may be displayed as historical-replay/reference evidence while its prospective four-metal/GPR source gates remain explicit.

## 9. Phase-A decision

**PASS_WITH_EXPLICIT_GAPS.** There is enough information to implement a correct V1.51 Master Orchestrator now, provided the orchestrator carries evidence/availability state per engine and does not silently use unavailable historical channels.

Remaining engineering/data gates before genuine prospective authority:

1. live immutable 1-minute event ingestion beyond the current 1m research-cache end;
2. prospective MIDAS/MSVR four-metal + GPR/vintage source readiness;
3. explicit historical/prospective availability treatment for backfilled cross-market series;
4. continued event-vintage clock audits, especially FOMC reconstructed score lineage;
5. future prospective shadow evidence after the V1.51 specification is frozen.
