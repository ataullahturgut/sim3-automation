# GOLD H3 — Remaining-53 Signal Audit Preregistration

**Date:** 2026-10-04  
**Status:** retrospective mechanism audit; NOT a promotion/validation test.  
**Target:** the 2026 missed reversals that remain after the already-recorded SAGE V2 exceptions plus the surviving RuleFlow V3-TG exception.

## Question

Were the remaining missed reversals already preceded by origin-safe evidence that the prevailing H3 momentum was losing structural support?

This is a signal audit, not a new classifier search.

## Fixed mechanism families

### A. Internal fragility
Trailing expanding/rolling percentile ranks, using only prior origins:
- low trend_strength
- high session_against_trend
- low trend_close_location
- high adverse_excursion

Score = median of the four adverse-state percentile ranks.

### B. Gold/Silver flow opposition
Momentum-normalized 12h flow state:
- high Gold opposite-volume share
- high Silver opposite-volume share
- high joint opposition share
- Gold signed flow against prevailing momentum
- Silver signed flow against prevailing momentum
- low Gold 12h path efficiency

Score = median of the six adverse-state percentile ranks.

### C. External lead-lag opposition
Use the already origin-safe LLRS state:
- llrs_external_opposes = True
- llrs_pressure > 0
- llrs_incremental > 0

Report both the strict three-part flag and continuous pressure/incremental ranks. Do not retune the SAGE OCS rule.

### D. Cross-asset reaction-function break
Using the DIVERGE panel's prior-date data, fit a trailing-60 OLS relationship:
Gold daily return ~ Silver return + USD return + 10Y-yield change + Nasdaq return + VIX return.

For each origin, fit on the preceding 60 origins only, predict the current prior-day Gold return, and compute:
- standardized absolute residual (unexpected Gold behavior);
- momentum-normalized residual against the prevailing H3 momentum.

No current or future target data enters the regression.

### E. Existing path-state warning
Use frozen TRES V2 probabilities only as a secondary diagnostic:
- mu_reversal
- mu_unresolved
They are not allowed to define the primary signal finding.

## Timing audit

For every remaining missed reversal inspect:
- t = feature cutoff
- t-1 previous available origin
- t-2 second previous origin

For clustered reversals, define an episode break when consecutive missed-reversal origins are more than 4 calendar days apart. Evaluate especially the **first origin of each episode**, so later observations do not masquerade as early warning.

## Fixed descriptive thresholds

Report mechanism coverage at percentile-score thresholds:
- 0.60
- 0.67
- 0.75
- 0.80

These thresholds are descriptive only. No threshold will be selected as a trading rule from 2026 results.

## Controls

Compare against 2026 correct-continuation origins where:
- actual H3 direction equals prevailing momentum;
- the combined SAGE+RuleFlow decision also keeps that momentum.

Report signal prevalence, lift, episode-first coverage, and overlap between mechanism families.

## Governance

- No new FLIP rule is created by this audit.
- No threshold is promoted on 2026.
- Findings must distinguish same-origin detection from true t-1/t-2 early warning.
- If a family appears promising, its successor rule must be frozen using earlier-year/development evidence before any promotion claim.
