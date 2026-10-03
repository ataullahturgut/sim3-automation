# CLEAN H3 PROSPECTIVE V1 — PROSPECTIVE FREEZE

**Date:** 2026-10-03  
**Identity:** `CLEAN_H3_PROSPECTIVE_V1`  
**Status:** **FROZEN / READY FOR FIRST FUTURE ORIGIN**  
**First eligible feature cutoff:** **2026-10-05**

## 1. Purpose

Create a clean prospective H3 experiment that is completely separate from the pre-existing AURORA V1 prospective ledger.

The new experiment uses the corrected historical daily price lineage and the clean retrospective AURORA / reversal chain as its frozen starting state.

No prior prospective forecast is rewritten or backfilled.

## 2. Clean source freeze

The frozen daily price snapshot is the prior frozen snapshot with exactly one validated integrity correction:

2026-02-27:
- Gold 3516.02 -> **5183.80**
- Silver 62.15 -> **88.14**
- Platinum 1585.39 -> **2369.25**
- Palladium 1201.26 -> **1789.96**

All other historical daily prices remain unchanged.

Frozen file:
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv`

## 3. Clean AURORA training freeze

Frozen file:
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_EXPERT_TRAIN_MATRIX.csv`

The matrix is generated from the clean A1 / clean target history and reproduces the clean retrospective September AURORA expert probabilities.

Reproduction:
- September rows: **19**
- max structural probability difference: **8.05e-16**
- max PATH probability difference: **8.88e-16**
- result: **PASS**

## 4. Clean reversal expert freeze

Historical training panels are frozen for:
- RIFT
- VEGA
- OPAL

TURN remains the same deterministic frozen rule driven by the hourly tail-state calculation.

Bootstrap reproduction against recorded clean history:

- RIFT: **931 rows**, override decisions identical, max probability diff **9.27e-15**
- TURN: **1029 rows**, override decisions identical, max probability diff **8.33e-17**
- VEGA: **931 rows**, override decisions identical, max probability diff **9.44e-16**
- OPAL: **931 rows**, override decisions identical, max probability diff **7.51e-12**

All checks: **PASS**.

## 5. Clean router binding

The clean prospective challenger will preserve the already-recorded clean-chain architecture without retuning:

- AURORA clean baseline
- RIFT V1
- TURN V1
- VEGA V1
- OPAL V1 threshold 0.70
- HELIOS V1 W8 / enter 5 / exit 3
- HELIOS V2 posterior calibration
- V3-GT binding W8, broken cost 1.0, GT threshold >0.50
- V4-RGE expansion window 10, regret +2 / -2
- V5-DCE PATH posterior >0.50 and GT share >0.50
- Data Integrity Gate V1 on all new daily data.

The diagnostic GT >0.60 / >0.70 sensitivity is **not** promoted.

## 6. Prospective governance

1. First eligible clean prospective feature cutoff is **2026-10-05**.
2. No date before this cutoff may be entered as clean prospective evidence.
3. If an eligible origin misses its issuance deadline, it is recorded as MISS and never reconstructed after outcome maturity.
4. Forecast fields are immutable after issuance.
5. Settlement may append only realized H3 outcome fields.
6. A quarantined daily input cannot issue or settle a prospective origin.
7. Any change to the clean price history, model rules, thresholds, router state logic or source lags requires a new version.

## 7. Evidence

Bootstrap workflow run:
- **37120224350 — SUCCESS**

Bootstrap evidence commit:
- `c2286108458c47a65aade15da7ec5eadbd842498`

Evidence files:
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_BOOTSTRAP_RESULT_2026-10-03.md`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_BOOTSTRAP_SUMMARY_2026-10-03.json`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_DAILY_PRICES.csv`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_EXPERT_TRAIN_MATRIX.csv`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_RIFT_PANEL.csv`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_VEGA_PANEL.csv`
- `GOLD_H3_CLEAN_PROSPECTIVE_V1_FROZEN_OPAL_PANEL.csv`
