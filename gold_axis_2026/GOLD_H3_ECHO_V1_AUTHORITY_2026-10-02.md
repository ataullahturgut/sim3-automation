# ECHO-H3 V1 — EQUITY CONFIRMATION & HEDGED OVERLAY AUTHORITY

**Date:** 2026-10-02
**Identity:** `ECHO_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Motivation

Two richer representations of XAU's own intraday path failed cleanly:
- TWIN-H3 nearest historical path analogues;
- SIGNET-H3 rough-path/signature geometry.

Therefore ECHO introduces genuinely new market information rather than further repackaging XAU:

- Newmont (`NEM_TWELVEDATA`)
- Barrick (`BARRICK_B_TWELVEDATA`)
- GLL (`GLL_TWELVEDATA`)
- DZZ (`DZZ_TWELVEDATA`)

These are gold-linked equity / inverse-gold market prices already frozen in Neon.

Hypothesis:
**some AURORA errors are confirmation failures: the XAU intraday path points one way while gold-linked equities / inverse-gold instruments do not confirm that move.**

## 2. Timing / anti-leakage

For an AURORA feature cutoff date D:

- only linked-asset observations with observation date **strictly before D** may be used;
- same-day linked-market close at D is deliberately excluded;
- all linked-asset series are point-in-time values already stored in Neon;
- no forecast_issue_date or future outcome data may enter features.

This conservative one-day information lag avoids close-time / timezone ambiguity.

## 3. Frozen linked-market features

For each asset A in:
- NEM
- BARRICK
- GLL
- DZZ

compute log returns over:
- 1 retained observation
- 3 retained observations
- 5 retained observations
- 10 retained observations.

For each horizon h, derive:

### Miner confirmation
- `miner_mean_h = mean(NEM_rh, BARRICK_rh)`
- `miner_spread_h = NEM_rh - BARRICK_rh`
- `miner_breadth_h = mean(1[NEM_rh>0], 1[BARRICK_rh>0])`

### Inverse-gold confirmation
- `inverse_mean_h = mean(GLL_rh, DZZ_rh)`

### Gold-up confirmation score
Because GLL/DZZ are inverse-gold instruments:
- `confirm_h = miner_mean_h - inverse_mean_h`

### Linked-market breadth / dispersion
Treat `-GLL` and `-DZZ` as gold-direction-aligned returns:
- `linked_breadth_h = mean(1[NEM>0], 1[BARRICK>0], 1[-GLL>0], 1[-DZZ>0])`
- `linked_dispersion_h = std(NEM, BARRICK, -GLL, -DZZ)`.

No feature selection is allowed after seeing later years.

## 4. Fixed rescue heads

Two candidate heads only:

1. `LINKED_ONLY`
   - linked-market features only.

2. `AURORA_PLUS_LINKED`
   - logit(p_AURORA) + linked-market features.

Both:
- StandardScaler
- LogisticRegression L2
- C = 0.25
- no class weighting
- chronological monthly expanding refit.

No model-family or C search.

## 5. Frozen rescue rule

AURORA remains default.

Override only if the ECHO head strongly contradicts AURORA:

- AURORA predicts DOWN and `p_echo_up >= 0.70` -> ECHO overrides to UP;
- AURORA predicts UP and `p_echo_up <= 0.30` -> ECHO overrides to DOWN;
- otherwise retain AURORA.

Thresholds 0.70 / 0.30 are fixed ex ante.

## 6. Selection authority

Only **Jul-Dec 2022** selects the head.

Eligibility relative to matched AURORA:
- balanced accuracy >= AURORA;
- accuracy >= AURORA - 0.5 pp;
- Brier <= AURORA + 0.0025;
- at least 3 override decisions.

Rank eligible heads by:
1. balanced accuracy;
2. accuracy;
3. Brier;
4. log loss.

No eligible head -> fail closed.

## 7. Frozen confirmation

Selected head is frozen after 2022-H2.

It passes only if, separately:

2023:
- accuracy >= AURORA -1 pp;
- Brier <= AURORA +0.003.

2024:
- accuracy >= AURORA -1 pp;
- Brier <= AURORA +0.003.

Aggregate 2023-2024:
- balanced accuracy >= AURORA;
- at least one genuine corrected AURORA error.

Only after all confirmation gates pass may 2025 / 2026 be opened.

## 8. Transport diagnostics

If confirmation passes, report:
- 2025 / 2026 accuracy, balanced accuracy, Brier, log loss;
- override count;
- corrected AURORA errors;
- broken AURORA calls;
- net rescue;
- 2026 call-by-call override table;
- performance on high-confidence AURORA errors.

## 9. Dependence-aware inference

If ECHO passes and improves transport:
- paired circular moving-block bootstrap;
- 10,000 replicates;
- block lengths 5 and 10 origins;
- compare ECHO vs AURORA in 2026 and 2025-2026.

## 10. Governance

If ECHO fails, do not tune:
- C;
- rescue thresholds;
- horizons;
- linked instruments;
- feature definitions
using 2023-2026 outcomes.

Any redesign requires a new identity.

The frozen AURORA prospective champion is not modified retroactively by ECHO research.
