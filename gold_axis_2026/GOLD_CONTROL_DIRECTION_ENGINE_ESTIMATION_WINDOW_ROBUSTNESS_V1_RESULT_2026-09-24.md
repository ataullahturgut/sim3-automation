# GOLD CONTROL — Direction Engine Estimation-Window Robustness V1

**Status:** `ROBUSTNESS_SURFACE_COMPLETE`

This V1 maps pre-2025 history-window sensitivity only. 2025/2026 were not loaded for scoring or selection.

## Baseline reproduction

- SQRT alarms 2022/2023/2024: {'2022': 11, '2023': 2, '2024': 17}
- Router frozen yearly summaries: [{"actual_down": 98, "actual_up": 107, "actual_up_recall": 0.11214953271028037, "calls": 22, "coverage": 0.1073170731707317, "false_up_fpr": 0.10204081632653061, "fp": 10, "n": 205, "precision": 0.5454545454545454, "selected_counts": {"TTSM_S1": 7, "TTSM_S2": 15}, "tp": 12, "wilson90_lcb_precision": 0.411021293948683, "year": 2022}, {"actual_down": 102, "actual_up": 101, "actual_up_recall": 0.04950495049504951, "calls": 19, "coverage": 0.09359605911330049, "false_up_fpr": 0.13725490196078433, "fp": 14, "n": 203, "precision": 0.2631578947368421, "selected_counts": {"TTSM_S2": 19}, "tp": 5, "wilson90_lcb_precision": 0.15637192644964787, "year": 2023}, {"actual_down": 86, "actual_up": 119, "actual_up_recall": 0.2184873949579832, "calls": 42, "coverage": 0.2048780487804878, "false_up_fpr": 0.18604651162790697, "fp": 16, "n": 205, "precision": 0.6190476190476191, "selected_counts": {"AR1_RM_LOGIT": 1, "RM_LOGIT": 37, "TTSM_S2": 4}, "tp": 26, "wilson90_lcb_precision": 0.520254930914069, "year": 2024}]
- UP-2 external formation: n=98, UP=46
- UP-2 pooled frozen: {"actual_down": 13, "actual_up": 13, "auc": 0.78698224852071, "brier": 0.22715763997399374, "coverage": 0.4230769230769231, "false_up": 3, "false_up_fpr": 0.23076923076923078, "missed_up": 5, "missed_up_recall": 0.6153846153846154, "n": 26, "true_down_abstain": 10, "true_up": 8, "up2_calls": 11, "up_precision": 0.7272727272727273, "wilson90_lcb_up_precision": 0.5345329033149758}

## Interpretation

No best window is declared by this run. Use the CSV surfaces to assess broad neighboring stability versus isolated spikes. Structural-break-conditioned estimation is reserved for a separately preregistered follow-up.

## Governance

No random split, no 2025/2026 selection, no DB write, no runtime promotion, no model feature or threshold rule change.
