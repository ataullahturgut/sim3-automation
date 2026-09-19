# GOLD CONTROL — DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH PREREGISTRATION

**Date:** 2026-09-18  
**Identity:** `DIRECTION_VLMC_BS_FIXED_SHARE_V1_RESEARCH`  
**Status:** `FROZEN_BEFORE_2025_REPLAY`  
**Parent:** `DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`  
**Evidence class:** historical research only; no runtime or production authority

## 1. Scientific motivation

The corrected source-faithful VLMC-BS family shows material instability across rolling window lengths and across years. A fixed 52-week expert validates strongly in 2024, while other windows can be relatively stronger in other regimes.

This is a classic non-stationary "best expert may change" problem. Fixed-Share (Herbster & Warmuth, 1998) was designed to track a changing best expert by exponentially updating expert weights from realized loss and then sharing a fixed fraction of weight back across experts so previously weak experts can recover.

This successor does **not** change the internal VLMC-BS models. It adaptively combines two source-faithful rolling VLMC-BS experts whose forecasts are available throughout the 2023 development surface:
- VLMC-BS-26;
- VLMC-BS-52.

VLMC-BS-104 is excluded from V1 Fixed-Share because it is not available throughout the 2023 development period. It may not be injected after seeing 2025.

## 2. Expert inputs

Expert probabilities are taken unchanged from:
`DIRECTION_VLMC_BS_FAMILY_V2_RESEARCH`.

Each expert was produced with:
- source-faithful weekly return construction;
- pinned R VLMC 1.4-4 reference semantics;
- its own frozen bootstrap cutoff.

No refitting or feature augmentation occurs inside the Fixed-Share layer.

## 3. Fixed-Share recursion

Initial weights on the first common eligible 2023 target:
`w_26=w_52=0.5`.

At target t:
1. receive expert probabilities `p_26,t`, `p_52,t`;
2. aggregate
   `p_t = sum_i w_i,t p_i,t`;
3. final direction = UP iff `p_t>=0.5`;
4. after outcome `y_t` is observed, compute expert loss;
5. exponential loss update:
   `v_i ∝ w_i exp(-eta * loss_i)`;
6. fixed-share step:
   `w_i,t+1 = (1-alpha) v_i + alpha/2`.

Only information available before the next forecast may update the weights.

## 4. Pre-2025 development grid

The grid is frozen before any successor 2025 replay:

Loss family:
- binary zero-one direction loss;
- Brier loss.

Learning rate:
`eta in {0.25,0.5,1,2,4}`.

Share rate:
`alpha in {0,0.01,0.02,0.05,0.10,0.20}`.

Development surface:
- common 2023 targets on which both k=26 and k=52 experts exist;
- n=43.

Selection criterion, lexicographic:
1. highest 2023 balanced accuracy;
2. highest 2023 raw accuracy;
3. lowest 2023 Brier score;
4. smaller eta;
5. smaller alpha.

No 2024 or 2025 observation is allowed to select `loss`, `eta`, or `alpha`.

## 5. Frozen development selection

The above grid selects:

- expert loss: `ZERO_ONE`;
- `eta=1.0`;
- `alpha=0.05`.

2023 development result:
- n=43;
- accuracy=0.6046512;
- balanced accuracy=0.6184211;
- UP sensitivity=0.5000000;
- DOWN sensitivity=0.7368421;
- Brier=0.2955614.

This parameter selection is frozen before 2024 validation and before successor 2025 replay.

## 6. 2024 validation protocol

The selected Fixed-Share specification is replayed unchanged across 2024 common k=26/k=52 targets.

Weights continue sequentially from the end of 2023; there is no annual reset.

2024 may validate or reject the successor but may not retune it.

## 7. 2025 lock

Only if the full 2024 validation checkpoint is persisted first may the exact same successor continue into 2025.

2025 rules:
- no reset at 2025-01-01;
- carry forward the frozen end-2024 weights;
- weights may update online after each realized 2025 weekly outcome, as specified above;
- no parameter/window/loss changes;
- event overlay only after the full 2025 weekly forecast table is frozen.

## 8. Forbidden

- adding VLMC-104 after seeing 2025;
- choosing alpha/eta/loss from 2024 or 2025;
- changing final 0.5 threshold;
- adding FAST/GVZ/BOCPD/Macro/Emergency context;
- probability calibration;
- NO_SIGNAL tuning;
- flat equal voting;
- post-2025 rescue under this identity.
