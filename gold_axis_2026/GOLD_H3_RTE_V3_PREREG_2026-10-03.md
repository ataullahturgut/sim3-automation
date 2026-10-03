# RTE-H3 V3 — OPTION-CONFIRMED TRANSITION CASCADE PREREGISTRATION

**Date:** 2026-10-03  
**Identity:** `RTE_OPT_H3_V3`  
**Branch:** `gold-h3-rte-v3-20261003`  
**Status:** **PREREGISTERED BEFORE 2026 OPENING**

## 1. Development history

V1 established that raw high transition probability is not selective enough.

V2 showed a slow-burn plateau pattern can be highly selective in 2023-2024 development (+7 net, 81.8% precision) but did not transport to 2025.

After the failed 2025 confirmation, 2025 became development data. Its strongest independent reversal-vs-continuation separation among the audited features was `signed_opt_pressure`: Gold call/put volume pressure oriented against prevailing 12h momentum.

V3 therefore drops the regime-specific plateau requirement and requires an independent options confirmation.

No 2026 outcome has been opened.

## 2. Fixed candidate cascade

For each V5-continuation eligible origin:

1. Transition-state gate:
   - `p_rte >= q`

2. Instant-state confirmation:
   - `p_inst >= 0.50`

3. Independent options counter-pressure:
   - `signed_opt_pressure > 0`

Candidate action:
- flip V5 direction.

The only searched parameter is:
`q ∈ [0.60, 0.65, 0.70]`

No other threshold or feature combination is searched.

## 3. Development robustness

2023 is excluded from robustness selection because only 12 origin-safe predictions exist after warm-up.

Development blocks:
- 2024 H1
- 2024 H2
- 2025 H1
- 2025 H2

For each q:
- candidate count
- rescued
- broken
- net rescue
- precision
- candidate rate

A q is robust-eligible if:
- aggregate 2024-2025 candidate count >= 15
- aggregate net rescue >= +5
- aggregate rescue precision >= 0.55
- aggregate candidate rate <= 0.25
- no half-year block has net rescue < -1
- at least 3 of 4 half-year blocks have net rescue > 0

Selection:
1. largest aggregate net rescue
2. higher aggregate precision
3. more rescued
4. lower candidate rate
5. higher q

No eligible q => `NO_ROBUST_RTE_V3_RULE`; 2026 remains unopened.

## 4. 2026 final holdout

Only if a development rule passes the robustness gate.

The selected q is frozen and applied exactly once to 2026.

Report:
- candidates / rate
- rescued / broken / net rescue
- rescue precision
- eligible V5 accuracy -> assisted accuracy
- whole-clean-2026 correct count and accuracy
- V5 missed reversal + OPAL-no-candidate count
- V3 hits in that set

No post-2026 tuning is permitted.

## 5. Governance

RTE V3 is a development successor using 2023-2025 history.  
Its first independent evaluation is 2026.  
No 2026 outcome may alter q, gates, source clock, feature construction, or action rule.
