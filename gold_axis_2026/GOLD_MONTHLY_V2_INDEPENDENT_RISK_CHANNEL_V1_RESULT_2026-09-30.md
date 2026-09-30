# GOLD MONTHLY — V2 Independent Risk Channel V1 Result

**Date:** 2026-09-30  
**Status:** COMPLETE / SCIENTIFIC_GATE=PASS / DEV CANDIDATE FAIL

## 1. Authority and execution

Authority:
- `gold_axis_2026/GOLD_MONTHLY_V2_INDEPENDENT_RISK_CHANNEL_V1_AUTHORITY_2026-09-30.md`
- authority commit: `9f8e69862c79200740915afa46b5d7d04b9c5830`

Code:
- `gold_axis_2026/tools/gold_monthly_v2_independent_risk_channel_v1.py`
- code commit: `ecd0f9c72fc791d050ee1661885443ffdc1b06d7`

Workflow:
- `.github/workflows/gold-monthly-v2-independent-risk-channel-v1.yml`
- workflow commit: `80bf75a4c2c18a717578fb4ea72156d1e4bad6ef`

Execution:
- workflow: **Gold Monthly V2 Independent Risk Channel V1**
- run: **36771008214**
- artifact: **11123875754**
- artifact digest: `sha256:40e92901f74566038538c6aa8715f6c4b7642ab76b82602d54e9d211d4d0686c`
- scientific gate: **PASS**

## 2. Critical chronology

V2 TRANSITION at origin t is evaluated against target t+1.

No target-month V2 state is used.

## 3. Primary DEV result — 2022-04..2024-12

### STABLE

- n = 24
- HIGH = **7/24 = 29.17%**
- MEDIUM = 2/24 = 8.33%
- ELEVATED = **9/24 = 37.50%**
- NORMAL = 15/24 = 62.50%

### TRANSITION

- n = 9
- HIGH = **1/9 = 11.11%**
- MEDIUM = 0
- ELEVATED = **1/9 = 11.11%**
- NORMAL = **8/9 = 88.89%**

Risk comparison:
- HIGH risk ratio TRANSITION/STABLE = **0.381**
- ELEVATED risk ratio = **0.296**

Thus in DEV, frozen V2 TRANSITION is associated with **lower**, not higher, next-month error severity.

## 4. Independent no-alarm test in DEV

### V2_TRANSITION + NO_ANY_VISIBLE

- n = 3
- HIGH = **0**
- MEDIUM = **0**
- NORMAL = **3**

Months:
- origin 2022-03 -> target 2022-04 NORMAL
- origin 2023-05 -> target 2023-06 NORMAL
- origin 2023-06 -> target 2023-07 NORMAL

Therefore V2 does **not** add an independent HIGH catch beyond ANY_VISIBLE in primary DEV.

### V2_TRANSITION + NO_T0_STANDARD

- n = 7
- HIGH = 1
- NORMAL = 6

The one HIGH is origin 2022-04 -> target 2022-05, but I1 already fired, so this is not independent of ANY_VISIBLE.

## 5. DEV union augmentation

### ANY_VISIBLE

- 25 events
- 8 HIGH
- 2 MEDIUM
- 15 false
- HIGH recall **100%**
- false-call rate **60.0%**
- useful-call rate 40.0%

### ANY_VISIBLE OR V2

- 28 events
- **same 8 HIGH**
- **same 2 MEDIUM**
- false calls increase **15 -> 18**
- HIGH recall remains 100%
- false-call rate rises **60.0% -> 64.3%**
- useful-call rate falls **40.0% -> 35.7%**

V2 adds no DEV coverage beyond ANY_VISIBLE and only adds false calls.

### T0_STANDARD

- 11 events
- 4 HIGH
- 2 MEDIUM
- 5 false
- HIGH recall 50.0%

### T0_STANDARD OR V2

- 18 events
- 5 HIGH
- 2 MEDIUM
- **11 false**
- HIGH recall 62.5%
- false-call rate rises **45.5% -> 61.1%**

V2 adds one HIGH beyond T0, but at the cost of six additional false calls.

## 6. DEV candidate gate

Pre-registered conditions:

1. TRANSITION HIGH rate > STABLE HIGH rate -> **FAIL**
2. TRANSITION ELEVATED rate > STABLE ELEVATED rate -> **FAIL**
3. at least one DEV HIGH in V2_TRANSITION + NO_ANY_VISIBLE -> **FAIL**

Overall:
- **CANDIDATE FAIL**

V2 is not promoted as a general independent risk-warning channel from DEV evidence.

## 7. Opened 2025-2026 result

This period is already opened and descriptive only.

### STABLE

- n = 17
- HIGH = 5/17 = 29.41%
- MEDIUM = 3/17
- ELEVATED = 8/17 = 47.06%
- NORMAL = 9/17

### TRANSITION

- n = **3**
- HIGH = **3/3 = 100%**
- ELEVATED = **3/3 = 100%**
- NORMAL = 0

Risk comparison:
- HIGH risk ratio = **3.40**
- ELEVATED risk ratio = **2.125**

This is the opposite pattern from DEV.

## 8. Opened independent no-alarm value

### V2_TRANSITION + NO_ANY_VISIBLE

Only one case:
- origin **2026-05**
- V2 = R2_TRANSITION
- no frozen alarm
- target **2026-06 = HIGH**
- APE about **8.57%**

This is a genuine incremental HIGH catch by V2 beyond all existing alarms.

### V2_TRANSITION + NO_T0_STANDARD

Two cases:
- origin 2026-05 -> target Jun HIGH, no alarm
- origin 2026-07 -> target Aug HIGH, G visible but not T0

Both are HIGH.

## 9. Opened union augmentation

### ANY_VISIBLE

- 12 events
- 7 HIGH
- 2 MEDIUM
- 3 false
- HIGH recall **87.5%**
- false rate 25.0%
- useful rate 75.0%

### ANY_VISIBLE OR V2

- 13 events
- **8 HIGH**
- 2 MEDIUM
- **same 3 false**
- HIGH recall improves **87.5% -> 100%**
- false-call rate falls slightly **25.0% -> 23.1%**
- useful-call rate rises **75.0% -> 76.9%**

The entire improvement is the independent 2026-05 -> 2026-06 HIGH catch.

### T0_STANDARD

- 6 events
- 4 HIGH
- 1 MEDIUM
- 1 false
- HIGH recall 50.0%

### T0_STANDARD OR V2

- 8 events
- **6 HIGH**
- 1 MEDIUM
- **same 1 false**
- HIGH recall improves **50.0% -> 75.0%**
- false-call rate falls **16.7% -> 12.5%**
- useful rate rises **83.3% -> 87.5%**

Again, opened V2 is highly complementary.

## 10. 2026 specifically

STABLE:
- n=6
- 1 HIGH
- 1 MEDIUM
- 4 NORMAL
- HIGH rate 16.7%

TRANSITION:
- n=2
- **2/2 HIGH**
- HIGH rate 100%

Thus 2026 HIGH risk ratio TRANSITION/STABLE = **6.0**.

ANY_VISIBLE:
- HIGH recall 2/3 = 66.7%.

ANY_VISIBLE OR V2:
- HIGH recall **3/3 = 100%**
- no additional false call.

T0:
- HIGH recall 0/3.

T0 OR V2:
- HIGH recall **2/3 = 66.7%**
- no false call.

## 11. Full 58-row perspective

Across all rows:

STABLE:
- HIGH rate 28.57%
- ELEVATED rate 40.48%

TRANSITION:
- HIGH rate 31.25%
- ELEVATED rate 43.75%

The full-sample difference is small.

Among `NO_ANY_VISIBLE`:
- STABLE: 0 HIGH / 12
- TRANSITION: 1 HIGH + 1 MEDIUM / 6.

So there is some non-redundant V2 information in the full sample, but it is driven materially by the recent episode and is not supported in DEV.

## 12. Binding interpretation

The independent-channel hypothesis is **not historically stable**.

Primary DEV says:
- V2 TRANSITION is not a high-risk warning;
- adding V2 to ANY_VISIBLE only adds false calls.

Opened 2025-2026 says:
- V2 TRANSITION is a severe-risk warning;
- 3/3 transition origins precede HIGH errors;
- adding V2 recovers the only HIGH missed by ANY_VISIBLE with no added false call.

Therefore:

> V2 has a strong **recent-regime / concept-drift** signal, but not a stationary historical risk-channel effect.

## 13. Binding decision

Do not deploy:
- V2 TRANSITION as a universal risk warning;
- `ANY_VISIBLE OR V2` as a production rule;
- `T0 OR V2` as a production rule.

Do not retune V2 using 2025/2026.

Retain the 2025-2026 result as important opened evidence.

## 14. Next defensible question

The evidence now points to **non-stationarity** rather than a fixed V2 effect.

If the project continues, the next test should ask:

> Is the alarm/V2 relationship conditioned by a persistent market era/regime shift, such that older R0/R1 history should not be pooled equally with the long R2 era?

That requires a preregistered recency / regime-era validation design, not a post-hoc recent-window threshold.
