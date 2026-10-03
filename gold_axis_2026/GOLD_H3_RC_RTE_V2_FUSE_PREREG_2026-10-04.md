# RC-RTE-H3 V2 — ONLINE CREDIBILITY FUSE PREREGISTRATION

**Date:** 2026-10-04  
**Identity:** `RC_RTE_H3_V2_FUSE`  
**Branch:** `gold-h3-rc-rte-v1-20261004`  
**Status:** **PREREGISTERED BEFORE 2026 OPENING**

## 1. Development finding

RC-RTE V1 showed that a regime can be historically reversal-enabled and then invert quickly.

In 2025 H2:
- static regime gate produced 20 candidates;
- 6 rescue / 14 broken / net -8;
- the first five static candidates were broken;
- regime-level deterioration was visible after matured candidate outcomes, not only at semester end.

Therefore V2 adds an online safety layer. The regime map and specialist proposals are unchanged.

## 2. Static regime layer

Identical to RC-RTE V1:
- origin-state axes: persistence, fragility, option opposition, participation shock;
- KMeans K=3, n_init=50, seed=20261004;
- static regime enabled only if training proposal support >=8, precision >=0.55 and net rescue >0;
- proposal union remains SB OR OPT OR MAT with all prior thresholds frozen.

## 3. One-outstanding-event rule

Within a live block, for each regime:
- at most **one accepted reversal candidate may be unresolved at a time**;
- if an earlier accepted candidate in that regime has `target_end_date_h3 > current feature_cutoff_date`, a new proposal is suppressed.

This prevents overlapping H3 events from being counted as independent evidence or creating clustered false flips.

## 4. Online credibility fuse

For each regime, using only previously **accepted and matured** live candidates:
- utility = +1 for rescue, -1 for broken;
- live regime score = cumulative matured utility.

A statically enabled regime is live-enabled only while:
`live_regime_score >= 0`.

Therefore:
- first matured broken event makes score -1 and closes that regime for the remainder of the current refit block;
- a regime is not reopened inside the block;
- the next scheduled block refit may reopen it based on the expanded matured training history.

No rolling-window length or fuse threshold is searched.

## 5. Sequential pre-2026 blocks

Same blocks as RC-RTE V1:
- 2024 H2, training before 2024-07-01
- 2025 H1, training before 2025-01-01
- 2025 H2, training before 2025-07-01

For each block:
- fit scaler + K=3 regime map on training only;
- static enablement from training outcomes only;
- apply one-outstanding rule + credibility fuse prospectively through the test block.

## 6. Robustness gate

Pooled across the three blocks, V2 passes if:
- accepted candidates >= 6
- net rescue >= +3
- rescue precision >= 0.60
- pooled assisted accuracy > pooled V5 accuracy
- at least 2 of 3 blocks have net rescue >= 0
- at least 1 block has net rescue > 0
- no block has net rescue < -2

The -2 block floor is a bounded exploration-loss condition: with K=3 and static enablement, the fuse is explicitly designed to cap damage from newly inverted regimes.

Failure => `NO_ROBUST_RC_RTE_V2_FUSE`; 2026 remains unopened.

## 7. 2026 final holdout

Only after robustness PASS.

Final fit uses all eligible data through 2025-12-31:
- refit state scaler;
- refit K=3 regime map;
- compute static enabled regimes;
- reset live scores to 0 at 2026 start;
- apply one-outstanding + credibility fuse prospectively through 2026.

Report:
- accepted / suppressed-overlap / suppressed-fuse counts
- rescue / broken / net
- precision
- eligible V5 vs assisted accuracy
- whole clean 2026 correct count / accuracy
- OPAL-no-candidate missed-reversal coverage
- per-regime live chronology

No 2026 outcome may alter the fuse, overlap rule, regime map, proposal union or robustness gate.
