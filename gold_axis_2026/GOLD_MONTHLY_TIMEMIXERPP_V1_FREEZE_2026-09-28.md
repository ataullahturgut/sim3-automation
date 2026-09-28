# GOLD MONTHLY FORECAST — TIMEMIXER++ V1 FREEZE

**Freeze date:** 2026-09-28
**Branch:** `gold-midas-headswap-v1-20260925`
**Status:** PRE-RUN METHOD FREEZE

## Provenance
Model: TimeMixer++ (ICLR 2025), evaluated through the PyPOTS forecasting implementation at exact commit:
`WenjieDu/PyPOTS@53b3eac34be9491ac3f28e65ee1993436e9318af`

Reference implementation class:
`pypots.forecasting.TimeMixerPP`

The PyPOTS reference forecasting example uses:
- n_steps=48
- term="short"
- n_layers=2
- top_k=5
- d_model=32
- d_ffn=32
- n_heads=1
- n_kernels=3
- downsampling_window=2
- downsampling_layers=1
- channel_mixing=True
- channel_independence=True
- use_norm=True
- dropout=0.1

V1 preserves those architectural settings.

## Gold Monthly V1 representation
- 4-variate monthly raw price-level input:
  1. Gold
  2. Silver
  3. Platinum
  4. Palladium
- lookback/context: 48 completed months
- horizon: 1 month
- predicts all 4 metals jointly; Gold is the business/evaluation target.
- no CURRENT8 engineered predictors
- no GPR or macro covariates
- no external scaler; TimeMixer++ internal use_norm=True (RevIN path)
- no target-month values in input

## Per-origin supervised sample construction
For each outer target month M:
- origin = M-1
- samples are rolling 48-month contexts with 1-month-ahead 4-metal targets.
- the latest 12 matured target months ending at the outer origin form the chronological validation set.
- all earlier eligible target months form the training set.
- no random split.

## Training
- seed = 20260928, reset for every outer origin.
- batch_size=32
- maximum epochs=40
- patience=6
- optimizer/loss/validation metric: PyPOTS defaults
- device=CPU
- model_saving_strategy=None
- verbose=False

Early stopping is permitted only on the explicit latest-12-month pre-target validation set. 2025 and 2026 are never used for architecture or training-policy selection.

## Evaluation
- DEV: 2022-04..2024-12, n=33 — sole scientific comparison authority.
- 2025: LOCKED_REPORT_ONLY.
- 2026-01..2026-07: QUARANTINED_REPORT_ONLY.
- primary metric: DEV SigmaAE.
- secondary: Gold direction accuracy.
- support: MAE, RMSE, MAPE, WAPE, relative MAE vs RW, worst month.

## Governance
- DB READ_ONLY
- random split: NONE
- target-month leakage: FORBIDDEN
- main Challenger-A/B paths unchanged
- no post-result architecture changes inside V1
