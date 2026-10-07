# GOLD SESSION — BOCPD V1 STAGE-3 FROZEN 2025 TRANSPORT PREREGISTRATION

**Date:** 2026-10-07  
**Status:** **FROZEN BEFORE 2025 BOCPD RESULT**

Upstream authority:
- `GOLD_SESSION_BOCPD_V1_STAGE2_RESULT_2026-10-07.md`
- `GOLD_SESSION_BOCPD_V1_STAGE2_GATE_2026-10-07.csv`

## Eligible heads

Only the two Stage-2 heads that passed the pre-2025 gate may be opened:

1. `SOBTI_5_ET / ASIA_AFTERNOON_LIT / S17_A1_SESSION`
2. `SOBTI_5_ET / NY_LONDON_LIT / STRUCTURAL_IRIS_1H`

All other session heads remain closed in 2025 for BOCPD.

## Frozen identity

Unchanged from Stage-2:

- BOCPD V1;
- Jeffreys Beta(0.5,0.5);
- expected run = 4 Handoff alarms;
- ACT iff predictive P(RESCUE) >= 0.60 and mixture P(theta>0.50) >= 0.80;
- Handoff thresholds 0.60 / 0.60 / nonnegative internal delta;
- BASE continuous-contract mapping:
  - GC.v.0
  - SI.v.0
  - NQ.v.0
  - ZN.n.0
  - CL.c.0
- no V4 hysteresis, DPTC, SELLR, RTE-family or later controller.

## 2025 source contract

The BASE Databento hourly continuous-contract observations are fetched for 2025 and combined with the already-governed 2022–2024 raw archive.

No 2025 source mapping is selected from outcome performance.

Every hourly bar is available only after its bar completion. Exact target-boundary equality is rejected.

## Baseline reconstruction

### Asia Afternoon
Rebuild `S17_A1_SESSION` with its frozen SESSION identity:
- fresh causal A1 logit;
- frozen SAGE session feature family;
- C=1 logistic;
- five-row causal blocks;
- minimum matured training rows unchanged.

### NY/London
Rebuild canonical `STRUCTURAL_IRIS_1H` using the frozen full 1h path identity and its original causal block/train rules.

No 2025 feature selection is permitted.

## BOCPD chronology

BOCPD state for each eligible session is reconstructed from its 2023–2024 Handoff alarm chronology first.

2025 is then replayed sequentially:
- only prior alarm outcomes with `end_utc <= current start_utc` may update state;
- current target outcome is never used in its own decision;
- state remains independent by partition/window.

## Frozen 2025 transport acceptance

A head is retained after 2025 only if all hold:

1. at least one BOCPD ACT occurs;
2. 2025 net rescue > 0;
3. assisted 2025 Balanced Accuracy >= baseline 2025 Balanced Accuracy;
4. assisted 2025 Accuracy >= baseline Accuracy - 1.0 percentage point.

No threshold or model identity may change after seeing 2025.

## 2026

2026 is stress/reporting only and remains blocked until a governed V5-equivalent 2026 SESSION target/source extension exists.

If neither head passes 2025 transport, BOCPD closes as **NOT PROMOTED**.
