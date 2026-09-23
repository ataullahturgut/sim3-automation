# GOLD CONTROL — RESIDUAL SEQUENCE-SHAPELET UP V1 IMPLEMENTATION CLARIFICATION

**Date:** 2026-09-23  
**Identity:** `RESIDUAL_SEQUENCE_SHAPELET_UP_V1_RESEARCH`  
**Timing:** before scoring.

Frozen numerical edge cases:

- The terminal sequence has exactly 97 cumulative-path points whenever the origin day has at least 96 retained 5-minute returns.
- Candidate and comparison-window z-normalization uses population standard deviation (`ddof=0`).
- Candidate shapelets with standard deviation <1e-8 are discarded.
- A comparison window with standard deviation <1e-8 is assigned infinite distance and cannot become the minimum match.
- Shapelet distance is RMS Euclidean distance after z-normalization.
- If no finite comparison window exists for a selected shapelet, the row is blocked as an integrity error.
- Logistic standardization uses population standard deviation and replaces values <1e-12 by 1.0.
- ROC AUC is computed only when both target classes are present.
- Wilson lower bound uses one-sided 90% z=1.2815515655.

No candidate family, length, start grid, selection rule, threshold rule, or evaluation gate changes.
