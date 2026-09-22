# GOLD CONTROL — UP EXPERT ROUTER V2 LEGACY-CONTEXT RESULT

**Date:** 2026-09-22  
**Identity:** `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Preregistration:** `f97dd635664db4506d6f8a622ced762249d3cdfc`  
**Status:** `PROMISING_LEGACY_CONTEXT_ROUTER_V2_PRE2025_GATE_PASSED`  
**Runtime authority:** NONE

## 1. What changed

Router V1 used only the newer same-clock daily UP experts. V2 keeps those direct experts but reintroduces the original Gold Control legacy direction layer as **context for competence**:

- FAST ROBUST_UP;
- SLOW ROBUST_UP;
- MONTHLY_DIRECTION_3M UP.

They are not converted into equal votes.

The three legacy states create two causal contexts:
- `CONSENSUS_UP`: at least 2 of 3 legacy states are UP;
- `NON_CONSENSUS_UP`: fewer than 2 are UP.

Each modern UP expert is judged from its matured historical record in the current context bucket, with a preregistered fallback to global history if bucket support is below 30 UP calls.

Other original engines remain in their proper roles: monthly H1 priors, event specialist, GVZ risk context, benchmark, or blocked/not-proven lanes.

## 2. Frozen 2024 validation

| Metric | Router V2 legacy-context | Router V1 | Fixed RM_LOGIT |
|---|---:|---:|---:|
| UP outputs | 42 | 135 | 149 |
| Coverage | **20.49%** | 65.85% | 72.68% |
| True UP / false UP | **26 / 16** | 77 / 58 | 84 / 65 |
| **UP precision** | **61.90%** | 57.04% | 56.38% |
| **False-UP FPR** | **18.60%** | 67.44% | 75.58% |
| Actual-UP recall | 21.85% | 64.71% | 70.59% |

Relative to Router V1:
- UP precision improves by **+4.87 percentage points**;
- false-UP FPR falls by **48.84 percentage points**;
- coverage falls by **45.37 percentage points**.

Selected direct experts in 2024:
- RM_LOGIT: 37;
- TTSM-S2: 4;
- AR1_RM_LOGIT: 1.

All 42 emitted UP signals occurred in `NON_CONSENSUS_UP` legacy context. The causal competence rules emitted no UP signal in the legacy `CONSENSUS_UP` bucket.

All frozen 2024 promising-gate conditions passed.

## 3. Locked 2025 transport

No rule changed.

| Metric | Router V2 legacy-context | Router V1 |
|---|---:|---:|
| UP outputs | 37 | 137 |
| Coverage | **15.61%** | 57.81% |
| True UP / false UP | **27 / 10** | 87 / 50 |
| **UP precision** | **72.97%** | 63.50% |
| **False-UP FPR** | **10.31%** | 51.55% |
| Actual-UP recall | 19.29% | 62.14% |

All 37 2025 outputs were selected through RM_LOGIT competence in `NON_CONSENSUS_UP` context. This is descriptive locked transport evidence only.

## 4. Interpretation

This result changes the picture materially.

The old 12-engine work was not dead weight. When FAST/SLOW/monthly direction are used in their original spirit—as regime/context rather than flat votes—they materially improve the **specificity** of the UP router.

The resulting system is deliberately selective:
- it misses many UP days;
- but when it does emit UP, the signal is much cleaner;
- false-UP burden is far lower than Router V1.

That is exactly the profile needed for a future SQRT counter-model: not a general UP forecaster, but a high-specificity UP verifier.

The surprising empirical pattern is that V2 abstains when the legacy layer is broadly bullish and emits only when fewer than two legacy direction states are UP. This should not be post-hoc reinterpreted as a causal economic law; it is the consequence of the frozen context-specific competence history and must be tested prospectively/with further predeclared evidence.

## 5. Binding decision

`UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH = PROMISING_LEGACY_CONTEXT_ROUTER_V2_PRE2025_GATE_PASSED / NOT_RUNTIME / NOT_PRODUCTION_AUTHORITY`

The next allowed step is a **separately preregistered SQRT countersign-veto intersection** using this frozen Router V2 output. No V2 threshold may change during that test.
