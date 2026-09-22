# GOLD CONTROL — SQRT × FROZEN UP VERIFIER V2 SEMANTIC AUDIT V1 RESULT

**Date:** 2026-09-23  
**Identity:** `SQRT_FROZEN_UP_VERIFIER_V2_SEMANTIC_AUDIT_V1_RESEARCH`  
**Status:** `RETROSPECTIVE_SEMANTIC_AUDIT_COMPLETE_NOT_CERTIFIED`

## 1. Primary 2024 result

Frozen SQRT alarms: **17** = 10 actual UP + 7 actual DOWN.

Frozen UP Verifier V2 emitted UP on **4** alarm days:
- 3 actual UP;
- 1 actual DOWN;
- conditional UP precision = **75.00%**.

On the other **13** alarm days the verifier abstained:
- 7 actual UP;
- 6 actual DOWN;
- P(DOWN | ABSTAIN, SQRT alarm) = **46.15%**.

Therefore `ABSTAIN => DOWN` is not supported.

If the user's full complement rule is nevertheless forced:
- Router UP => UP;
- Router ABSTAIN => DOWN;

then 2024:
- TP_UP=3;
- FP_UP=1;
- TN_DOWN=6;
- FN_UP=7;
- accuracy = **52.94%**;
- balanced accuracy = **57.86%**.

## 2. Corrected semantic crosswalk — the important result

The four 2024 Router-UP/SQRT-overlap days were cross-walked against the frozen semantic risk audit.

| Target date | Router V2 | Close | Realized risk state | Semantic class |
|---|---|---|---|---|
| 2024-08-07 | UP | UP | risk miss | RISK_MISS_UP_CLOSE |
| 2024-11-13 | UP | DOWN | risk hit | RISK_HIT_DOWN_CLOSE |
| 2024-11-14 | UP | UP | risk miss | RISK_MISS_UP_CLOSE |
| 2024-11-26 | UP | UP | risk miss | RISK_MISS_UP_CLOSE |

Thus:
- **3/4 Router-UP calls were genuine SQRT realized-risk misses**;
- all three correct UP calls were not merely UP-close days — they were actual downside-risk misses under the parent's frozen Q80 semantics;
- the single incorrect Router-UP call suppressed a genuine realized-high-risk DOWN day.

This means the frozen UP verifier's 2024 intersection remains meaningful even after the risk-vs-direction semantic correction.

## 3. What happened when Router abstained in 2024?

Among 13 abstain alarm rows:

- RISK_HIT_DOWN_CLOSE = 5;
- RISK_HIT_UP_CLOSE = 2;
- RISK_MISS_DOWN_CLOSE = 1;
- RISK_MISS_UP_CLOSE = 5.

So abstention contains both directions and both risk states. It is not a DOWN label.

## 4. Secondary 2022–2024 support

Across 30 frozen SQRT alarms:
- actual UP=16;
- actual DOWN=14;
- Router UP only 4 times = 3 UP / 1 DOWN;
- Router abstained 26 times = 13 UP / 13 DOWN.

Forced complement rule accuracy = **53.33%**, balanced accuracy = **55.80%**.

The selective UP call has information; the complement does not.

## 5. Locked 2025 stress

Frozen SQRT alarms: **90** = 45 UP + 45 DOWN.

Router V2 emitted UP on **16**:
- 10 actual UP;
- 6 actual DOWN;
- conditional UP precision = **62.50%**.

Router abstained on **74**:
- 35 actual UP;
- 39 actual DOWN;
- P(DOWN | ABSTAIN) = **52.70%**.

Forced complement rule:
- accuracy = **54.44%**;
- balanced accuracy = **54.44%**.

The 2025 row-level realized-risk crosswalk is **NOT_PROVEN** because the retained frozen intersection result does not preserve the 16 individual Router-UP dates. It is not reconstructed from memory.

## 6. Binding interpretation

The correct conclusion is asymmetric:

> **Router V2 UP is useful evidence for UP. Router V2 ABSTAIN is not evidence for DOWN.**

In 2024 the UP verifier was especially interesting because 3 of its 4 SQRT-overlap UP calls identified genuine realized-risk misses. So the old "good veto" cases survive the corrected semantic audit.

But the user's stronger complement rule:

> `UP verifier says UP => UP; otherwise => DOWN`

does **not** solve the direction problem. The weakness is not the positive UP signal; it is treating abstention as a negative DOWN signal.

The architecture should therefore preserve three states:
- HIGH RISK + VERIFIED UP;
- HIGH RISK + NO VERIFIED UP / UNCERTAIN;
- a separate DOWN-confirmation signal is still required before converting uncertainty into DOWN.

No runtime promotion is authorized.
