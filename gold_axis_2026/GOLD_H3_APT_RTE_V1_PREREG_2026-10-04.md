# APT-RTE-H3 V1 — ASYMMETRIC PRESSURE TRANSFER REVERSAL ENGINE

**Date:** 2026-10-04  
**Identity:** `APT_RTE_H3_V1`  
**Branch:** `gold-h3-apt-rte-v1-20261004`  
**Status:** **PREREGISTERED BEFORE 2026 OPENING**

## 1. Mechanism

OAR q=0.60 is the strongest pre-2026 reversal specialist so far:
- 34 candidates
- 22 rescues
- 12 broken
- net +10
- precision 64.71%.

Its false-alarm diagnostic shows a coherent participation difference:

True rescues:
- median GC one-day log-volume change ≈ -0.037
- median GC volume acceleration ≈ -0.100

Broken flips:
- median GC one-day log-volume change ≈ +0.107
- median GC volume acceleration ≈ +0.059

Interpretation:
- options pressure is turning against the prevailing price momentum;
- at the same time futures participation supporting the current move is fading.

APT-RTE models this as **pressure transfer** from futures continuation into options opposition.

## 2. Frozen rule

No threshold search.

Candidate if all hold:
- `p_rte >= 0.60`
- `p_inst >= 0.50`
- `signed_opt_pressure > 0`
- `signed_d_opt_pressure > 0`
- `gc_dlog_volume_1 < 0`
- `gc_volume_accel_5 < 0`

All sign thresholds are structural zero thresholds, not fitted cut points.

Action:
flip V5 direction.

## 3. Development robustness

Evaluate exactly once on:
- 2024 H1
- 2024 H2
- 2025 H1
- 2025 H2

Pre-2026 PASS requires:
- total candidates >=8
- aggregate net rescue >= +4
- aggregate rescue precision >=0.65
- candidate rate <=0.10
- at least 3 of 4 blocks have net rescue >=0
- no block net rescue < -1
- pooled assisted accuracy > pooled V5 accuracy

Failure => `NO_ROBUST_APT_RTE_RULE`; 2026 remains unopened.

## 4. 2026 final holdout

Only if development PASS.

Apply the exact frozen rule once to 2026.

Report:
- candidates/rate
- rescued/broken/net
- rescue precision
- eligible V5 -> assisted accuracy
- whole-clean-2026 correct count and accuracy
- OPAL-no-candidate missed reversal coverage.

No holdout-driven modification is permitted.

## 5. Governance

2024-2025 is complete development.  
2026 is the first independent APT-RTE evaluation.  
HELIOS V5-DCE remains binding until promotion is separately justified.
