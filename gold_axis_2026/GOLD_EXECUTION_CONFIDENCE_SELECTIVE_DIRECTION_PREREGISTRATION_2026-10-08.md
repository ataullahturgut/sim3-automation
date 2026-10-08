# Gold execution — historical forecast-confidence selective test (2026-10-08)

Prerecorded hypothesis: high pre-origin model confidence, operationalized as absolute distance of predicted UP probability from 0.5, selects fewer decisions with improved conditional balanced direction skill. This is a risk/coverage hypothesis; no guarantee of improved BA. No use of 2025 outcomes to set selection.

Fixed eligible models: SHAPE_GVZ_HGB, VIX_GVZ_HGB already independently fitted and their model architecture/calendars frozen. Control: BASE_LOGIT evaluated on the same selected nights. Targets: Istanbul 17:00 to next eligible 09:00 REGULAR 16h, Friday 64h excluded. DAY not included because initial out-of-sample direction test did not show stable stand-alone skill.

Fixed rule: for each candidate model, start after 60 previous dated probability outputs; collect at most last 90 strictly earlier predictions; compute their 60th percentile of abs(pUP-0.5) WITHOUT observed labels; issue UP/DOWN if current absolute margin >= that historical percentile, otherwise ABSTAIN. This rule targets approximate 40% action rate as the score distribution remains stationary, but actual coverage may differ. No performance-derived threshold adjustment. On a tie at 0.5, use original binary UP rule.

2023–24 chronological development, 2025 frozen-fit historically examined transport; all models' probabilities are calculated only with prior matured labels in model training. Forecaster-choice is fixed; no 2025 winner promotion.

Must report by 2023, 2024, 2025: N, coverage, UP/DOWN recall, BA, accuracy, Brier, predicted-UP share and score-split confusion matrices. Same selected-date BASE_LOGIT comparison, plus full-unselected figures. Direction on action days is not a live profitability estimate: Turkish bank spread and source quote timestamp validation remain absent.

Interpretation constraints: baseline and selected samples cannot be compared naively as same population; show matched controls on each model-selected sample. 2025 has been repeatedly inspected so remains retrospective rather than untouched OOS. Do not mix positive findings with prior 3 external-variable experiment results without acknowledging multiplicity.
