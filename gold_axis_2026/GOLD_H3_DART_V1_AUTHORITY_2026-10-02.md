# DART-H3 V1 — DISAGREEMENT-AWARE REGIME TRANSFER AUTHORITY

**Date:** 2026-10-02
**Identity:** `DART_H3_V1_RESEARCH`
**Parent:** `SENTRY_H3_V1_RESEARCH`
**Status:** PREREGISTERED / RESEARCH-ONLY

## 1. Motivation

SENTRY improved transport by switching between:
- STRUCTURAL_IRIS = A1 + frozen hourly PATH
- PATH_GLOBAL = frozen hourly PATH only

But SENTRY accumulates paired advantage over the last 63 matured H3 origins, including many rows where the experts issue the same direction and therefore provide no information about relative directional competence.

DART uses only **matured expert-disagreement events**.

For a binary H3 disagreement:
- if PATH_GLOBAL is correct, `X=1`;
- if STRUCTURAL_IRIS is correct, `X=0`.

Because the two expert directions differ, exactly one expert is correct at each disagreement event.

## 2. Bayesian online change-point model

The disagreement-winner sequence is modeled as piecewise Bernoulli.

Within a regime:
`X_t ~ Bernoulli(theta)`

where:
- `theta > 0.5` favors PATH_GLOBAL,
- `theta < 0.5` favors STRUCTURAL_IRIS.

Prior at a new regime:
- Beta(1,1).

Run-length recursion:
- standard Bayesian Online Change-Point Detection (BOCPD) recursion;
- constant hazard `h = 1/20` per matured disagreement event;
- maximum tracked run length 120 disagreement events.

The hazard is fixed ex ante; no 2023-2026 tuning.

## 3. Current evidence summaries

At each forecast origin, after updating only with disagreement events whose H3 targets have already matured:

- posterior predictive PATH win probability:
  `q_path = E[theta | matured disagreements]`
- posterior probability PATH is superior:
  `Pr(theta > 0.5 | data)`
- posterior expected run length.

If fewer than 8 matured disagreement events have been observed, DART remains on STRUCTURAL_IRIS.

## 4. Frozen state rule

Initial state:
- STRUCTURAL_IRIS.

Enter PATH_GLOBAL when:
- matured disagreements >= 8;
- `Pr(theta > 0.5) >= 0.90`;
- `q_path >= 0.60`.

Return STRUCTURAL_IRIS when:
- `Pr(theta > 0.5) <= 0.10`;
- `q_path <= 0.40`.

Otherwise retain current state.

Thresholds are symmetric and fixed before evaluation.

## 5. Timing / anti-leakage

At forecast origin t:
- only historical rows with `target_end_date_h3 <= feature_cutoff_date_t` may update BOCPD;
- current and future targets are unavailable;
- expert probabilities are the same monthly expanding leakage-free OOS experts already used by AIM/SENTRY.

## 6. Evaluation

Diagnostic warm-up:
- 2022.

Frozen confirmation:
- 2023
- 2024

Transport/stress:
- 2025
- 2026.

DART is a mechanism pass only if:
- 2023 and 2024 accuracy are each no worse than STRUCTURAL_IRIS by >1 pp;
- 2023 and 2024 Brier are each no worse by >0.003;
- 2023-2024 aggregate balanced accuracy is no worse by >1 pp;
- DART performs at least one state transition after warm-up.

No 2025/2026 outcome may alter hazard or thresholds.

## 7. Diagnostics

Report:
- annual metrics;
- state-switch dates;
- number of matured disagreements;
- annual PATH-active share;
- posterior q_path and superiority probability by year;
- 2026 rescued vs broken calls;
- 2026 monthly comparison.

## 8. Interpretation

DART tests whether an explicit probabilistic change-point model over **only information-bearing expert disagreements** can adapt faster and more cleanly than SENTRY's fixed 63-origin net-rescue window.

The evaluation remains retrospective research, not prospective proof.
