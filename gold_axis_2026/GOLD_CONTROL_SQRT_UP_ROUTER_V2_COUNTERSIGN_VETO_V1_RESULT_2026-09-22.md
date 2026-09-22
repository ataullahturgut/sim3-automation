# GOLD CONTROL — SQRT × UP ROUTER V2 COUNTERSIGN VETO V1 RESULT

**Date:** 2026-09-22  
**Identity:** `SQRT_UP_ROUTER_V2_COUNTERSIGN_VETO_V1_RESEARCH`  
**Preregistration:** `375ceaa0d6a84ecb7a4da6f7dacc72c7a9b66693`  
**Frozen verifier:** `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Final status:** `NEAR_MISS_PRE2025_GATE_FAILED_BY_PRECISION_DELTA`  
**Runtime authority:** NONE

## 1. Alignment

The frozen Router V2 was intersected with SQRT alarms by exact origin date.

- 2024 SQRT alarms: 17; exact target/sign matches: 17/17.
- 2025 SQRT alarms: 90; exact target/sign matches: 90/90.
- target-date mismatches: 0.
- next-direction mismatches: 0.

No nearest-date or forward-fill matching was used.

## 2. Primary 2024 result

Baseline SQRT forced-DOWN anatomy:

- alarms: 17;
- true next-day DOWN: 7;
- false forced-DOWN / actual UP: 10;
- baseline forced-DOWN precision: **41.18%**.

Frozen Router V2 emitted UP on **4** of those 17 SQRT alarm origins:

- GOOD_VETO: **3**;
- BAD_VETO: **1**;
- veto precision: **75.00%**;
- false-alarm reduction: **30.00%**;
- true-DOWN retention: **85.71%**;
- remaining forced-DOWN calls: 13;
- remaining forced-DOWN precision: **46.15%**;
- precision gain: **+4.98 percentage points**;
- net veto benefit: **+2**.

The four veto origins were:
- 2024-08-06 → actual UP → good veto;
- 2024-11-12 → actual DOWN → bad veto;
- 2024-11-13 → actual UP → good veto;
- 2024-11-25 → actual UP → good veto.

All four were selected through RM_LOGIT competence inside the frozen `NON_CONSENSUS_UP` legacy bucket.

## 3. Frozen promising gate

| Gate | Requirement | Observed | Pass |
|---|---:|---:|---|
| Veto count | >=3 | 4 | PASS |
| Veto precision | >=65% | 75.00% | PASS |
| False-alarm reduction | >=25% | 30.00% | PASS |
| True-DOWN retention | >=80% | 85.71% | PASS |
| Remaining precision gain | >=+5.00 pp | **+4.98 pp** | **FAIL** |

The last gate misses by only about **0.02 percentage point**.

The preregistered rule is binding. It is not relaxed after seeing the result.

Therefore the formal 2024 decision is **FAIL / NEAR MISS**, not PROMOTED.

## 4. Locked 2025 stress

Rules were unchanged.

Baseline:
- 90 SQRT alarms;
- 45 true DOWN;
- 45 false forced-DOWN;
- baseline precision = 50.00%.

Router V2:
- vetoes: **16**;
- good vetoes: **10**;
- bad vetoes: **6**;
- veto precision: **62.50%**;
- false-alarm reduction: **22.22%**;
- true-DOWN retention: **86.67%**;
- remaining forced-DOWN precision: **52.70%**;
- precision change: **+2.70 pp**;
- net veto benefit: **+4**.

2025 is directionally supportive but cannot rescue the failed primary gate.

## 5. Interpretation

This is materially different from the earlier UP-veto experiments.

The frozen legacy-context Router V2 is selective enough that, on 2024 SQRT alarm days, **three of its four UP vetoes remove genuine false DOWN alarms and only one removes a true DOWN**.

That is the first tested architecture in this sequence to simultaneously show:
- veto precision well above 50%;
- meaningful false-alarm removal;
- >80% true-DOWN retention;
- improved remaining DOWN precision.

However the predeclared precision-gain threshold was +5.00 pp and the observed gain is +4.98 pp. The miss is tiny but binding.

The correct scientific conclusion is therefore:

`NEAR_MISS_PRE2025_GATE_FAILED_BY_PRECISION_DELTA`

not promotion.

Because the primary support is only 17 SQRT alarms and four vetoes, the next step should be **more independent same-clock historical evidence / longer parent-alarm support**, not a post-hoc threshold or rule change.

## 6. Governance

No random split, no 2025 tuning, no threshold relaxation, no production write and no runtime promotion occurred.
