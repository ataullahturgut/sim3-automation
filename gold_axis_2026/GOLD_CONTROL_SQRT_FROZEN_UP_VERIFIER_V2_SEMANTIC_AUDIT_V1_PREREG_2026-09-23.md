# GOLD CONTROL — SQRT × FROZEN UP VERIFIER V2 SEMANTIC AUDIT V1 PREREGISTRATION

**Date:** 2026-09-23  
**Identity:** `SQRT_FROZEN_UP_VERIFIER_V2_SEMANTIC_AUDIT_V1_RESEARCH`  
**Risk motor:** frozen `SQRT-HAR-DR`  
**UP motor:** frozen `UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESEARCH`  
**Purpose:** re-interpret the already-frozen SQRT × UP-verifier intersection under the corrected risk-versus-direction semantics.  
**Runtime authority:** NONE  
**Production authority:** NONE

## 1. Frozen question

The UP verifier is the authoritative frozen UP baseline in manifest section 6D.

This audit asks two separate questions on SQRT alarm days:

1. If the frozen UP verifier emits UP, how often does the next-day close actually finish UP?
2. If the verifier abstains, does abstention justify converting the case into DOWN?

The audit also cross-walks the 2024 verifier-UP cases against the corrected semantic risk label:
- realized high-risk hit versus realized risk miss.

No Router rule, SQRT rule, threshold, expert set or context definition is changed.

## 2. Frozen sources

1. `GOLD_CONTROL_UP_EXPERT_ROUTER_V2_LEGACY_CONTEXT_RESULT_2026-09-22.json`
   - frozen verifier result commit `f4c661731c8888985b82b4bf16eab401184fa76f`.

2. `GOLD_CONTROL_SQRT_UP_ROUTER_V2_COUNTERSIGN_VETO_V1_RESULT_2026-09-22.json`
   - frozen exact-origin intersection result;
   - primary 2024 and locked 2025 stress.

3. `GOLD_CONTROL_ROUTER_V2_HISTORICAL_EXTENSION_V1_RESULT_2026-09-22.json`
   - frozen 2022–2024 extension and exact 2024 reproduction.

4. `GOLD_CONTROL_SQRT_ALARM_SEMANTIC_AUDIT_V1_LEDGER_2026-09-22.csv`
   - corrected realized-risk semantics for 2020–2024.

No result is refit or regenerated.

## 3. Frozen decision rule for the user's proposed composition

For descriptive diagnosis only:

- Router V2 UP -> predict UP.
- Router V2 ABSTAIN -> predict DOWN.

This complement rule is evaluated exactly as stated, but ABSTAIN is **not** assumed to mean DOWN in the model contract. The audit explicitly measures whether that complement assumption is supported.

## 4. Primary 2024 metrics

Using the already-frozen 17 SQRT alarms:

- UP-verifier conditional precision:
  `P(actual UP | SQRT alarm, Router V2 UP)`.
- Abstain conditional DOWN share:
  `P(actual DOWN | SQRT alarm, Router V2 ABSTAIN)`.
- complement-rule accuracy and balanced accuracy.
- exact 2024 semantic crosswalk of Router-UP cases:
  - RISK_HIT_DOWN_CLOSE
  - RISK_HIT_UP_CLOSE
  - RISK_MISS_DOWN_CLOSE
  - RISK_MISS_UP_CLOSE

Also report the same risk-hit/miss anatomy for Router-ABSTAIN rows.

## 5. Locked 2025 stress

Use the existing frozen exact-origin intersection counts only.

Report:
- UP-verifier conditional precision;
- abstain conditional DOWN share;
- complement-rule accuracy and balanced accuracy.

The retained frozen 2025 intersection result does not store the 16 individual Router-UP dates. Therefore the 2025 realized-risk semantic crosswalk is `NOT_PROVEN` and must not be reconstructed from memory or guessed.

2025 cannot tune, rescue or alter any rule.

## 6. Secondary 2022–2024 support

Report the exact frozen historical extension:
- 2022 alarms=11, Router-UP overlap=0;
- 2023 alarms=2, overlap=0;
- 2024 alarms=17, overlap=4 = 3 actual UP / 1 actual DOWN.

This is descriptive support only.

## 7. Interpretation constraints

A positive UP-verifier result does not imply that ABSTAIN means DOWN.

Three possible findings are distinct:

- **UP-verifier useful:** Router UP is meaningfully enriched for actual UP.
- **Complement useful:** Router ABSTAIN is meaningfully enriched for actual DOWN.
- **Risk-cleaning useful:** Router UP identifies SQRT alarms that are realized-risk misses, not merely days that later close UP.

These must not be conflated.

This is a retrospective semantic audit after the relevant historical outcomes are already visible. It cannot certify a runtime policy.

## 8. Governance

- no random split;
- no model retraining;
- no threshold tuning;
- no 2025 tuning;
- no 2026 use;
- no production writes;
- no runtime promotion;
- missing row-level evidence is marked `NOT_PROVEN`.
