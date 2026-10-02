# TWIN-H3 V1 — TEMPORAL WEIGHTED INTRADAY NEIGHBOURHOOD AUTHORITY

**Date:** 2026-10-02
**Identity:** `TWIN_H3_V1_RESEARCH`
**Parent:** `AURORA_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Objective

Correct a subset of AURORA-H3 direction errors using a new representation of information that the linear IRIS PATH head does not explicitly model:

**the geometry of the last 24–48 hours of the hourly XAU path.**

TWIN is not an error-risk classifier. It asks a direct counterfactual question:

> among previously matured origins whose normalized intraday path looked most similar to the current path, which H3 direction subsequently occurred?

## 2. Information timing

- Same validated IRIS 1-hour XAU source.
- Anchor: 16:00 America/New_York on feature_cutoff_date.
- No forecast_issue_date or later hourly bar.
- Neighbour memory at origin t may contain only rows with `target_end_date_h3 <= feature_cutoff_date_t`.

## 3. Shape-only embeddings

For each origin:

### SHAPE24
- last 24 hourly log returns ending at the 16:00 NY anchor;
- normalize by sqrt(sum(return^2)) + epsilon;
- cumulative normalized path;
- Piecewise Aggregate Approximation (PAA) into 8 equal blocks.

### SHAPE48
- last 48 hourly log returns;
- same normalization;
- cumulative normalized path;
- PAA into 12 equal blocks.

### SHAPE_MULTI
- concatenate SHAPE24 and SHAPE48.

Amplitude is deliberately normalized out. IRIS/AURORA already carries return magnitude; TWIN adds **path shape**.

## 4. Local analogue probability

At each origin and for each representation:

1. standardize embedding dimensions using only matured-memory mean/std;
2. Euclidean distance to all matured prior origins;
3. retain the nearest **25** neighbours;
4. similarity weight:
   `w_i = exp(-d_i / median(d_1..d_25))`;
5. local H3 UP probability:
   `p_local = sum(w_i y_i) / sum(w_i)`.

If fewer than 40 matured analogues are available, no rescue is allowed.

## 5. Frozen rescue rule

AURORA remains the default probability.

Override only when the local analogue evidence strongly contradicts AURORA:

- AURORA predicts DOWN and `p_local >= 0.70` -> replace with `p_local`;
- AURORA predicts UP and `p_local <= 0.30` -> replace with `p_local`;
- otherwise retain `p_aurora`.

The 0.70 / 0.30 rescue thresholds and k=25 are fixed ex ante and are not searched.

## 6. Representation selection

Representation only is selected on **Jul-Dec 2022**:
- SHAPE24
- SHAPE48
- SHAPE_MULTI.

Matched AURORA is the comparator.

Eligibility:
- balanced accuracy >= AURORA;
- accuracy >= AURORA -0.5 pp;
- Brier <= AURORA +0.0025;
- at least 3 rescue decisions in the selection period.

Rank:
1. balanced accuracy;
2. accuracy;
3. Brier;
4. log loss.

If no representation is eligible, TWIN fails closed.

## 7. Frozen confirmation

Selected representation is frozen after 2022-H2.

TWIN is a mechanism pass only if:
- 2023 accuracy >= AURORA -1 pp;
- 2024 accuracy >= AURORA -1 pp;
- 2023 Brier <= AURORA +0.003;
- 2024 Brier <= AURORA +0.003;
- 2023-2024 aggregate balanced accuracy >= AURORA;
- and TWIN produces at least one genuine rescue in 2023-2024.

2025 and 2026 are report-only transport/stress and cannot alter V1.

## 8. Diagnostics

Report:
- annual accuracy / balanced accuracy / Brier;
- rescue count, broken-call count, net rescue;
- strong analogue overrides by year;
- 2026 call-by-call rescued and broken origins;
- performance conditioned on local analogue confidence.

## 9. Scientific rationale

Recent shapelet research supports interpretable directional forecasting from recurrent local time-series patterns, while modern shapelet-selection work emphasizes diverse and nonredundant local subsequences. TWIN uses a deliberately simpler, leakage-safe analogue formulation to test whether **path geometry** contains transportable H3 information beyond IRIS's aggregate multi-scale returns.

## 10. Governance

If TWIN fails, do not tune rescue thresholds or k on 2023-2026.

If TWIN passes, it remains a challenger until prospective evidence is available; the frozen AURORA prospective ledger is not modified retroactively.
