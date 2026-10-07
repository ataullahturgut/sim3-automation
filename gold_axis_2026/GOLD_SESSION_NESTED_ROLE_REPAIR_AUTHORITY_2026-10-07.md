# GOLD SESSION — 07B / 08B / 09B development chronology repair authority

**Date:** 2026-10-07
**Scope:** feature-selection chronology; narrow supersession; no new consensus or transport selection.

## Finding and supersession

The three original selected producers collect chronological selection events over 2023–2024, aggregate a full-development frozen subset, then pass that subset back into development replay:

- `gold_session_model07b_sage_path_session_feature_selection_20261007.py`: `freeze_features(events)` → `replay_frozen(...,[2023,2024])`.
- `gold_session_model08b_sage_a1_session_feature_selection_20261007.py`: `freeze(events)` → `replay(...,[2023,2024])`.
- `gold_session_model09b_sage_a1_path_session_feature_selection_20261007.py`: analogous full-development freeze and backwards development replay.

Even when raw features and coefficient training are point-in-time, selecting the representation with later development outcomes contaminates earlier development predictions. Existing target-clock/source-ready audit PASS does not certify this separate selector chronology.

The original **selected** development metrics, eligibility gates and any selected-disagreement inference using these rows are no longer causal role-selection authority. This supersedes that inference in their 07B/08B/09B result files and the selected incremental-disagreement result. Historical files and values are preserved. Fixed-feature canonical heads, other model families and V5 labels are not invalidated by this finding.

Original 2025 selected forecasts used a subset chosen before 2025, so their numerical scores remain archived frozen-spec transport evidence. However, their prior eligibility claim was based on the contaminated development replay; therefore they are not evidence of a clean development-validated policy. They must never be joined to repaired nested development scores as if the identities were identical.

## Successor identity

The corrected successor is a **nested selection policy** preserving the original family and chooser, not a new algorithm family:

| Original family | New development identity | Exact matched comparator |
|---|---|---|
| 07B PATH + SAGE | NESTED_PATH_SESSION | NESTED_PATH_MATCHED (same selected PATH subset) |
| 08B A1 + SAGE | NESTED_A1_SESSION | DIRECT_A1 (fresh causal A1 probability) |
| 09B A1 + PATH + SAGE | NESTED_A1_PATH_SESSION | NESTED_A1_PATH_MATCHED (same selected PATH subset + A1) |

At each inherited chronological outer block, compute its first target origin, restrict training to earlier origins and already-matured target ends, then run the original inner chronological chooser on that restricted history. Fit only the selected representation and emit the block forecasts. No full-development frozen list is replayed backwards. Existing family-specific minimum training, upstream raw panel producers, imputation/scaling and chooser logic are retained.

This run produced 1,304 eligible family/window/outer blocks and 12,946 forecast rows including the matched comparators. Scored years are exactly 2023–2024. A full input panel may include 2025 for the inherited V5 identity verification; it is removed before downstream feature selection and replay. No 2025 successor scoring, 2026 role discovery, random split or consensus was performed.

The raw producers rebuild PATH/A1/SAGE from governed intraday/daily inputs; historical prediction CSVs are not used to fit the successor. Archived prediction CSVs in the separate evidence audit are **evaluation evidence only**, never a new model feature source. Existing source-ready and PIT authorities remain prerequisites; this repair addresses selector chronology in addition to those contracts.

## Artifacts and verification

- [Repair producer](tools/gold_session_nested_role_repair_20261007.py)
- [Development forecasts and matched comparators](GOLD_SESSION_NESTED_ROLE_REPAIR_PREDICTIONS_2026-10-07.csv)
- [Block timing and feature selections](GOLD_SESSION_NESTED_ROLE_REPAIR_TIMING_2026-10-07.csv)
- [Repair summary](GOLD_SESSION_NESTED_ROLE_REPAIR_SUMMARY_2026-10-07.json)
- [Matched incremental metrics](GOLD_SESSION_NESTED_ROLE_REPAIR_PAIRED_METRICS_2026-10-07.csv)
- [Window evidence result](GOLD_SESSION_WINDOW_EVIDENCE_RESULT_2026-10-07.md)

Assertions verified all train ends ≤ block cutoff, all train origins < cutoff, all emitted origins ≥ selection cutoff, and exactly 2023/2024 scored years. Every evaluation-ledger label was separately checked against the unchanged final V5 targets. The outer-block maturity rule is deliberately more conservative than merely training on earlier session starts.

Frozen V5 target SHA256 remains:

- WGC: `178f45e708b9faf415fb9e6d20bd15dda01983f0b3e0d269f3fa243a671e1e26`.
- Sobti: `cef50b30f895bb420196e1efd4ac01493c3939474199d098ca57428375a4cf06`.

The run used Python 3.12 and scikit-learn 1.8. Existing historical models were evaluated from their archived probabilities, rather than silently regenerated in this runtime. Numerical equivalence to an older runtime is not claimed for the new successor. Original producer files remain historical reproducibility records; their backwards selected development replay is prohibited as causal evidence by this authority. Use the successor producer for future development chronology work.

## Transport and next-step boundary

`NESTED_*` and `FROZEN_*` are distinct policies. Same-family selected/full probabilities must not become multiple independent votes. No 2025 score was consulted to tune the repaired policy. A future confirmation must lock its policy before an untouched period; already-seen 2025 cannot provide a new untouched test. Consensus/router and final Istanbul DAY/OVERNIGHT decisions remain deferred.
