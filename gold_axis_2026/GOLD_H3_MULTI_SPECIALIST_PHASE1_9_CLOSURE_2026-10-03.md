# GOLD H3 — MULTI-SPECIALIST REVERSAL DISCOVERY PHASES 1–9 CLOSURE

**Date:** 2026-10-03  
**Research objective:** reduce HELIOS V5-DCE residual error by expanding reversal candidate recall without 2026 threshold tuning.  
**Final batch status:** **NO ADMISSIBLE V6 EXPANSION**

## Binding baseline

HELIOS V5-DCE remains the clean retrospective champion:
- 2026: 121/191 correct = 63.35%
- balanced accuracy: 63.76%
- Brier: 0.2425
- 2025-2026 accuracy: 65.15%

Residual anatomy motivating this batch:
- 70 V5 errors in clean 2026
- 58 missed reversals
- 55/58 missed reversals had no OPAL candidate

The batch therefore targeted candidate generation rather than further V5 router tuning.

## Phase-by-phase result

| Phase | Component | Result | Promotion |
|---:|---|---|---|
| 1 | FLOW-H3 Volume+OI | BLOCKED_EXTERNAL_HISTORICAL_OI_ACCESS | NO |
| 1A | FLOW-VOL ablation | NO_ELIGIBLE_FLOW_VOL_THRESHOLD | NO |
| 2 | SKEW-H3 / Gold CVOL directional skew | BLOCKED_EXTERNAL_CVOL_ENTITLEMENT | NO |
| 3 | HAZARD-H3 | NO_ELIGIBLE_HAZARD_THRESHOLD | NO |
| 4 | DIVERGE-H3 exact | SOURCE_BLOCKED | NO |
| 4A | DIVERGE-PROXY-H3 | NO_ELIGIBLE_DIVERGE_THRESHOLD | NO |
| 5 | Recall-first candidate union | NO_ADMISSIBLE_EXPANSION | NO |
| 6 | Vintage / overlap evidence accounting | ENTRY GATE CLOSED — no new multi-specialist evidence | NO NEW FIT |
| 7 | HELIOS V6 router | NO_ADMISSIBLE_V6_ROUTER_INPUT | NOT FIT |
| 8 | Sequential evidence gate | DEFERRED_NO_V6_EVENT_STREAM | NOT FIT |
| 9 | UP/DOWN/ABSTAIN selective action | DEFERRED_NO_PROMOTED_V6_SIGNAL | NOT FIT |

## Phase 1 — FLOW

Full FLOW contract was correctly separated from a volume-only ablation.

Full FLOW:
- official COMEX GC FINAL daily Volume+Open Interest identity and origin-safe clock frozen;
- historical official OI unavailable in current environment;
- full model not fit.

FLOW-VOL ablation:
- source: Yahoo GC=F volume proxy, strict prior-trade-date only;
- DEV 2023-2024;
- no threshold satisfied precision >=45% and candidate-rate <=35%;
- 2025 and 2026 were not opened.

This rejects volume-only fallback under the preregistered contract, not the untested Volume+OI mechanism.

## Phase 2 — SKEW

Gold CVOL directional authority frozen:
- GCVL
- GCUP
- GCDN
- GCSK
- GCAM
- GCCV

Historical directional CVOL entitlement was absent. No GVZ pseudo-skew or unrelated proxy was silently substituted. SKEW-H3 remains externally blocked.

## Phase 3 — HAZARD

Duration-dependent trend termination was implemented from the frozen intraday path:
- trend age / nonlinear age
- recent momentum switches
- nonlinear trend strength
- exhaustion/adverse-path state
- duration interactions

DEV result:
- lower thresholds produced recall but excessive candidates / weak precision;
- no threshold reached the frozen selectivity gate;
- status NO_ELIGIBLE_HAZARD_THRESHOLD;
- 2025/2026 remained unopened.

## Phase 4 — DIVERGE

Exact-source DIVERGE was preregistered with Gold/Silver, Fed H.10 broad USD, H.15 10Y, NDX and VIX under strict prior-date alignment.

Exact transport remained source-blocked.

A separately named proxy mechanism test used:
- DXY proxy
- TNX proxy
- NDX
- VIX
- frozen Gold/Silver

It also failed the DEV selectivity gate. No formal 2025/2026 opening occurred.

## Phase 5 — Candidate union

Admission was based on each specialist's own preregistered result, not retrospective union performance.

No new specialist was admissible.

Therefore OPAL union empty-set = OPAL.

A renamed OPAL-only universe is not HELIOS V6. V6 was not fit or scored.

## Phases 6–9

Because no candidate expansion occurred:
- there was no new multi-specialist evidence set for correlation/vintage accounting;
- there was no legitimate V6 router input;
- there was no V6 event stream for sequential gating;
- there was no promoted V6 signal for a selective action overlay.

Each entry gate was evaluated separately and frozen; no stage was silently skipped.

## Scientific conclusion

The initial diagnosis was not disproven: candidate-generation remains the dominant structural bottleneck.

What this batch establishes is narrower and important:

1. **Volume alone is insufficient** under the frozen selectivity criterion.
2. **Duration/path hazard features alone are insufficient** under the same criterion.
3. **The tested cross-asset divergence representation is insufficient** under the same criterion.
4. The two most information-novel channels — **official daily GC Open Interest** and **directional Gold options CVOL components** — were **not actually tested**, because their historical entitled data were unavailable.
5. Therefore it is not scientifically valid to conclude that FLOW or SKEW mechanisms fail.
6. It is also not valid to manufacture a V6 by lowering gates after observing outcomes.

## Binding project state after this batch

- HELIOS V5-DCE remains binding.
- Clean Prospective V1 remains untouched.
- No new 2026 performance claim is created.
- No failed threshold is relaxed.
- No blocked source is replaced under the same identity.
- The next R&D batch must add genuinely new reversal information or a new target formulation; another generic router pass over the same OPAL universe is not justified.

## Evidence files

FLOW:
- GOLD_H3_FLOW_V1_AUTHORITY_2026-10-03.md
- GOLD_H3_FLOW_STAGE1A_CLOSURE_2026-10-03.md
- GOLD_H3_FLOW_VOL_V1_RESULT_2026-10-03.md

SKEW:
- GOLD_H3_SKEW_V1_AUTHORITY_2026-10-03.md

HAZARD:
- GOLD_H3_HAZARD_V1_PREREG_2026-10-03.md
- GOLD_H3_HAZARD_V1_RESULT_2026-10-03.md

DIVERGE:
- GOLD_H3_DIVERGE_V1_PREREG_2026-10-03.md
- GOLD_H3_DIVERGE_V1_RESULT_2026-10-03.md
- GOLD_H3_DIVERGE_PROXY_V1_RESULT_2026-10-03.md

Closure:
- GOLD_H3_HELIOS_V6_ADMISSIBILITY_RESULT_2026-10-03.md
- GOLD_H3_PHASE6_VINTAGE_OVERLAP_GATE_2026-10-03.md
- GOLD_H3_PHASE7_HELIOS_V6_ROUTER_GATE_2026-10-03.md
- GOLD_H3_PHASE8_SEQUENTIAL_EVIDENCE_GATE_2026-10-03.md
- GOLD_H3_PHASE9_SELECTIVE_ACTION_GATE_2026-10-03.md
