# ZN-VPT2: low-capacity continuous-volume interaction diagnostic — PRE OUTCOME FREEZE, 2026-10-09
**Status:** preregistered research only / revised because D∧H selected cohort yielded 14/18 development observations; NO conditional outcomes examined in the preceding gate. Not a new unrelated family and not a model promotion.

### Causal source/time
Normal 17:00→next business 09:00 XAU signed BID/ASK label (DOWN=1). Same gold source 2020–25; ZN.c.0 2023–25 native Databento H1. Origin local 17:00, last ZN feature H1 15:00–16:00 (ts_event bar start 15:00 local), pessimistic as-of 16:15. Prior 14:00–15:00 H1 for ZN log return, same instrument_id; XAU mid close local15:00/16:00 from 14:45/15:45 start M15. Only non-Friday overnight with no holiday gap and COMPLETE_SINGLE_SOURCE; exclude any missing/zero/nonpositive/roll-cross features. `v=ln(current ZN15h volume / PRIOR20 qualified ZN 15h local-time bars' median volume)`. Continuous volume, no class-cohort selection. Availability claim remains a source-observation assumption until provider archival publication latency proven.

### Hypothesis
ZN-VPT2 asks ONLY whether `rZN * v` adds **incremental signed endpoint discrimination** conditional on own gold return, absolute XAU/ZN price changes, ZN price direction, and ZN volume main effect. This is not genuine orderflow direction or causal Treasury leadership proof. Retain null and reject if no stable paired gains.

### Models / metrics (fully fixed before viewing VPT2 labels)
Let `rX=10000 ln(mid16/mid15)`, `rZ=10000 ln(ZN16/ZN15)`, `v=ln(volume_current/median(volume_prior20))`.
Baseline B0 raw features `[rX,rZ,abs(rX),abs(rZ),v]`. Challenger B1 = B0 + `rZ*v`. Both have intercept, training-only standardized features, L2 logistic with penalty `5/(2N) * sum(coef^2)`, no intercept penalty. Hard DOWN if probability>0.5. Train deterministic maximum-likelihood approximated by gradient descent 2000 iterations or convergence tolerance 1e-8, learning rate 0.1; no hyperparam search.
- 2023: expanding chronological label-matured prior 80 eligible rows minimum; for computational simplicity one updated fit per **calendar month** on rows strictly from months before issue, never use current-month/future labels. 2024: train solely on completed 2023, frozen all 2024. 2025 retrospective: train solely on completed 2023–24, frozen all 2025. No 2026 here. Do not use 2025 to revise predictors/penalty.
- Pair B0 and B1 on EXACT rows, report N, each year BA, accuracy, DOWN precision/recall, UP recall, Brier, rescue-break and exact McNemar; include always-UP reference; no execution P&L.
- Reject B1 if paired BA/Brier do not both improve in 2024 and 2025, if it only predicts UP, or if net rescues ≤0; any observed positive retrospective is hypothesis-generating only. Sample and 2025 inspection require prospective post-Oct9 date freeze before claim.
- This feature is explicitly adjacent to untrained GC CAVS and historical negative ZN *price-only* CME3-K25: DO NOT claim novelty of generic cross-asset modeling; test ONLY incremental causal pre-origin volume sign interaction.
