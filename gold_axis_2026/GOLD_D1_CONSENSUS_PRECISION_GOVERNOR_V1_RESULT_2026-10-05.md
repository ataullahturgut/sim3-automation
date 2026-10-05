# GOLD D1 — CONSENSUS PRECISION GOVERNOR V1

**Date:** 2026-10-05  
**Identity:** `CPG_D1_V1`  
**Status:** **RETROSPECTIVE DEVELOPMENT / FROZEN SHADOW CHALLENGER — NOT PRODUCTION**  
**Binding baseline remains:** `CIG_D1_V1`

## 1. Objective

The research target is deliberately narrower than UNCERTAIN resolution.

> Improve precision on days where CIG-D1 already produces a 4/4 direction, without forcing decisions on existing UNCERTAIN days.

The governor therefore may only **downgrade confidence / abstain** on an existing 4/4 consensus. It does not create a new UP/DOWN forecast and does not resolve any existing disagreement day.

## 2. Regime-break model identification

The regime-sensitive model referred to in the prior project history is the **Handoff Competence BOCPD** line, especially `V4 Hysteresis`.

Its native H3 evidence is strong but retrospective:
- 2026 Handoff alarms: 28
- V4 acted: 10
- H3 rescue / broken: 8 / 2
- precision: 80.00%
- H3 baseline: 126/191 = 65.97%
- V4 assisted H3: 132/191 = 69.11%.

However, that H3 success does **not** transport directly to next-day D1 direction.

On the 10 V4 acted dates that are also 4/4 D1 consensus dates:
- D1 consensus correct: 6/10 = 60.00%
- forcing the opposite Handoff direction: 4/10 = 40.00%.

Therefore Handoff/BOCPD is retained as a **regime-risk corroborator**, not a fifth direction vote.

## 3. Primary risk representation

The strongest reusable error-risk signal is TRES Stage-1 `F_reversal`.

Frozen reference threshold:
- derived from the 2024 TRES eligible-continuation distribution;
- 80th percentile = **0.16448401023042702**.

This numeric threshold is origin-independent once frozen.

Important caveat:
the later choice to focus the governor on **UP consensus** was discovered during retrospective 2025–2026 analysis. Therefore historical performance is development/stress evidence, not clean untouched OOS proof.

## 4. Frozen shadow states

### NORMAL
Keep the existing 4/4 CIG action when the YELLOW condition is false.

### YELLOW — reversal-risk conflict
All must hold:
1. CIG is a valid 4/4 consensus action;
2. CIG direction = **UP**;
3. TRES `eligible_v5_continuation = True`;
4. TRES `F_reversal >= 0.16448401023042702`.

Shadow action:
**downgrade HIGH-CONFIDENCE to CAUTION / ABSTAIN in strict-precision mode.**

No direction flip is permitted.

### RED — independent Handoff corroboration
All YELLOW conditions plus:
- a canonical Handoff alarm is present at the same origin.

Shadow action:
**STRONG CAUTION / ABSTAIN.**

The BOCPD-V4 trust state and DPTC-Q95 state are logged as stronger retrospective corroborators, but are not allowed to create a production action because their architectures were developed after inspection of 2026 behavior.

## 5. Historical precision evidence

### 2024 common-core proxy
Exact SAGE V2 history cannot be reconstructed under the later frozen source contract, so the earlier-year transport proxy is the common 3-expert consensus: V5 + RIFT + VEGA.

Baseline:
- 178/220 = **80.91%**.

YELLOW:
- flagged 5
- flagged correct 4/5 = **80.00%**
- retained 174/215 = **80.93%**.

Interpretation:
essentially neutral in 2024; no meaningful degradation.

### 2025 common-core proxy

Baseline:
- 182/225 = **80.89%**.

YELLOW:
- flagged 19
- flagged correct 13/19 = **68.42%**
- retained 169/206 = **82.04%**
- retained share of consensus actions = **91.56%**
- accuracy delta = **+1.15 pp**.

RED using canonical Handoff alarm:
- flagged 5
- flagged correct 2/5 = **40.00%**
- retained 180/220 = **81.82%**
- retained share = **97.78%**
- accuracy delta = **+0.93 pp**.

The five RED dates are a small sample and must not be treated as conclusive validation.

### 2026 common-core proxy

Baseline:
- 113/160 = **70.63%**.

YELLOW:
- flagged 16
- flagged correct 6/16 = **37.50%**
- retained 107/144 = **74.31%**
- retained share = **90.00%**
- accuracy delta = **+3.68 pp**.

The deterioration is concentrated especially in 2026 H2:
- common-core baseline 34/48 = **70.83%**
- YELLOW subset 4/11 = **36.36%**
- retained 30/37 = **81.08%**.

This is retrospective stress evidence and not an untouched 2026 test.

## 6. Exact enhanced 2026 CIG-D1 replay

Binding retrospective baseline:
- 191 D1 days
- 157 4/4 actions
- 112 correct
- accuracy **71.34%**
- all-day coverage **82.20%**.

### YELLOW strict-precision counterfactual
- flagged: 14
- flagged correct: 6/14 = **42.86%**
- flagged errors: 8
- retained actions: 143
- retained correct: 106
- retained accuracy: **74.13%**
- accuracy delta: **+2.79 pp**
- consensus-action retention: **91.08%**
- all-day coverage: **74.87%**.

The YELLOW flag removes 8/45 = **17.78%** of all consensus errors while removing 14/157 = **8.92%** of consensus actions.

### RED canonical-Handoff corroboration
- flagged: 5
- flagged correct: 2/5 = **40.00%**
- retained: 110/152 = **72.37%**
- accuracy delta: **+1.03 pp**
- all-day coverage: **79.58%**.

The same TRES + Handoff + UP pattern is also 2/5 correct in the 2025 common-core proxy.

### Stronger retrospective corroborators
These are diagnostic only:

**YELLOW + BOCPD V4 acted/trust state**
- 3 dates
- consensus correct 1/3 = **33.33%**.

**YELLOW + DPTC-Q95**
- 4 dates
- consensus correct 1/4 = **25.00%**.

Both samples are too small and both mechanisms are contaminated by post-2026 design knowledge. They are not eligible to define the binding shadow rule.

## 7. Main scientific conclusion

The user hypothesis is supported in a narrower form:

> When all four D1 experts agree, an independent reversal/regime mechanism can still identify a subset in which that agreement is materially less trustworthy.

But the useful role is **confidence governance**, not direction replacement.

Specifically:
- Handoff BOCPD V4 is valuable on its native H3 horizon;
- on D1, blindly taking the opposite Handoff direction is harmful;
- TRES provides the more stable D1 error-risk signal;
- Handoff/BOCPD adds useful corroboration when it agrees with that risk state;
- DPTC adds an even stronger 2026 diagnostic warning but is post-hoc and cannot be promoted.

## 8. Binding project decision

1. **Do not change CIG_D1_V1.**
2. **Do not touch existing UNCERTAIN days.**
3. Freeze `CPG_D1_V1` in shadow mode.
4. Primary shadow state = YELLOW rule above.
5. RED = YELLOW + canonical Handoff alarm.
6. No automatic FLIP under CPG V1.
7. BOCPD-V4 trust and DPTC-Q95 are telemetry-only corroborators.
8. Future unseen origins must decide whether the precision gain persists.

This architecture changes the question from:

`4/4 agreement => always high confidence`

to:

`4/4 agreement => high confidence unless an orthogonal reversal/regime-risk governor detects a fragile consensus state`.

## 9. Evidence sources

- `GOLD_D1_CIG_V1_EXTENDED_JAN_SEP_REPLAY_2026-10-05.csv`
- `GOLD_H3_TRES_V1_STAGE1_PREDICTIONS_2026-10-04.csv`
- `GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V1_TIMELINE_2026-10-04.csv`
- `GOLD_H3_HANDOFF_COMPETENCE_BOCPD_V4_HYSTERESIS_TIMELINE_2026-10-04.csv`
- `GOLD_H3_DPTC_V1_ACTIONS_2026-10-05.csv`
- clean V5 / RIFT / VEGA prediction files
- clean frozen daily Gold price snapshot
