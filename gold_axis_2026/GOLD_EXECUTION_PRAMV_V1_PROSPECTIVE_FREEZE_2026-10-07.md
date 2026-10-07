# GOLD EXECUTION PRAMV V1 — PROSPECTIVE FREEZE AUTHORITY

**Freeze date:** 2026-10-07
**Status:** FROZEN / NEXT UNSEEN TEST ONLY
**Target:** 17:00 -> next eligible 09:00 Europe/Istanbul

## Frozen identity

PRAMV V1 = Path-Reversal Agreement + Macro Veto.

At 17:00 Europe/Istanbul:

1. If a same-day paired macro surprise has been released and is available by 17:00 -> **ABSTAIN**.
2. Otherwise require the completed 16:00-16:30 and 16:30-17:00 XAU/USD half-hour returns to have opposite signs. If not -> **ABSTAIN**.
3. RFR direction = the sign of the 16:00-16:30 return.
4. M4 direction = frozen M4_SIG_FPCA_MACRO from the PSF-OVN architecture:
   - 3h return
   - realized volatility
   - semivolatility balance
   - maximum drawdown
   - sign-change count
   - 16:00-16:30 return
   - 16:30-17:00 return
   - normalized lead-lag signature area
   - normalized time-price signature area
   - rolling FPCA PC1 / PC2
   - same-day macro-released flag
   - PIT max absolute macro surprise z
   - upcoming FOMC before next eligible 09:00
   - StandardScaler + L2 LogisticRegression C=1.0, threshold 0.50
5. If M4 direction == RFR direction -> issue that direction.
6. Otherwise -> **ABSTAIN**.

No additional confidence threshold exists.

## Frozen evidence

2023:
- N 89
- coverage 34.77%
- Accuracy 60.67%
- BA 60.59%

2024:
- N 86
- coverage 33.20%
- Accuracy 60.47%
- BA 60.05%

2023-2024 pooled:
- N 175
- coverage 33.98%
- Accuracy 60.57%
- BA 60.35%
- one-sided binomial p vs 50% = 0.0032
- vs PAIR exact-common rows: rescue 15 / break 6 / net +9
- exact rescue-vs-break p = 0.0784

2025 retrospective corroboration:
- N 82
- coverage 32.28%
- Accuracy 63.41%
- BA 63.41%

2025 is not untouched prospective evidence because the archive was already accessible before PRAMV synthesis.

## Forbidden before next unseen test

Do not:
- change the macro veto definition;
- change the two half-hour windows;
- invert the first-impulse rule;
- change M4 features;
- add PATH/STRUCTURAL/session votes;
- change logistic C or threshold;
- add a confidence cutoff;
- tune coverage;
- use 2026 outcomes to alter the rule before scoring.

## Next valid test

The next valid evidence is a locked 2026+ / newly unseen origin set produced after this freeze, with all source-ready and target-clock rules applied unchanged.

Report:
- N and coverage
- Accuracy / BA
- UP / DOWN recall
- confusion matrix
- PAIR exact-common comparison
- rescue / break / net rescue
- risk/coverage
- zero-cost and spread-aware P&L only after directional scoring.

A failure on the next unseen test must be recorded as a failure; it must not trigger same-sample retuning.
