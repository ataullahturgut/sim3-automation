# GOLD MONTHLY — BOOSTING STAGE 2 FEATURE REPRESENTATION REPORT

Date: 2026-09-27
Status: **STAGE 2 COMPLETE — PASS**
Scope: DEV 2022-04..2024-12 only (n=33)
2025/2026: NOT OPENED / NOT EVALUATED

## Objective

Test whether the Boosting family was being handicapped by using only the preprocessed CURRENT8 VW-MIDAS representation.

Frozen representations:
- CURRENT8
- RAW_LEVEL_LAGS8
- SIMPLE_RETURNS8
- DAILY_SUMMARY12
- MIXED20

All Stage-1 model hyperparameters remained unchanged. Target remained next-month Gold log return. No target/loss tuning occurred.

## Methodological correction

The first valid Stage-2 design used a common historical start of 2010-05 so every representation saw the same training span. That was necessary because 3-month momentum is not buildable for historical targets 2010-03 and 2010-04.

However, the common-start run exposed strong sensitivity to removing the first two historical rows, especially in CatBoost. Therefore Stage 2 was not closed until a pairwise-history audit was run:

- RAW_LEVEL_LAGS8 vs CURRENT8: both start 2010-03.
- DAILY_SUMMARY12 vs CURRENT8: both start 2010-03.
- SIMPLE_RETURNS8 vs CURRENT8: both start 2010-05.
- MIXED20 vs CURRENT8: both start 2010-05.

This separates feature-representation effect from history-length effect.

## Stage-1 exact reconciliation

The original Stage-1 CURRENT8 scores were reproduced exactly:

| Model | Stage-1 SigmaAE |
|---|---:|
| CatBoost Ordered | 1460.4339 |
| Random Forest anchor | 1614.4908 |
| XGBoost | 1778.0649 |
| GBRT | 1801.8648 |
| LightGBM | 1832.5777 |

All absolute differences versus Stage 1 were 0.0.

## Pairwise fair-history results

### CatBoost Ordered

| Representation | Candidate SigmaAE | Matched CURRENT8 | Delta | Direction candidate/control |
|---|---:|---:|---:|---:|
| RAW_LEVEL_LAGS8 | 1691.360 | 1460.434 | +230.926 | 19 / 20 |
| DAILY_SUMMARY12 | 1491.957 | 1460.434 | +31.523 | 20 / 20 |
| SIMPLE_RETURNS8 | 1768.331 | 1530.669 | +237.662 | 18 / 20 |
| MIXED20 | 1523.486 | 1530.669 | **-7.183** | 20 / 20 |

Interpretation:
- CatBoost still prefers the original CURRENT8 when the full compatible history is available.
- MIXED20 has a small benefit only under the shortened 2010-05 common-history condition.
- No new representation beats the Stage-1 CatBoost CURRENT8 absolute score of 1460.4339.

**Stage-3 primary CatBoost representation: CURRENT8.**

### XGBoost

| Representation | Candidate SigmaAE | Matched CURRENT8 | Delta | Direction candidate/control |
|---|---:|---:|---:|---:|
| RAW_LEVEL_LAGS8 | **1695.556** | 1778.065 | **-82.509** | 18 / 21 |
| DAILY_SUMMARY12 | 1772.070 | 1778.065 | -5.995 | 20 / 21 |
| SIMPLE_RETURNS8 | 1814.040 | 1601.546 | +212.494 | 16 / 24 |
| MIXED20 | 1638.996 | 1601.546 | +37.450 | 20 / 24 |

Interpretation:
- Raw level/lag inputs materially reduce XGBoost price error.
- But direction falls from 21/33 to 18/33.
- CURRENT8 remains the direction-oriented challenger.

**Stage-3 XGBoost lanes: RAW_LEVEL_LAGS8 for price; CURRENT8 retained as direction challenger.**

### GBRT

| Representation | Candidate SigmaAE | Matched CURRENT8 | Delta | Direction candidate/control |
|---|---:|---:|---:|---:|
| RAW_LEVEL_LAGS8 | 1740.028 | 1801.865 | -61.837 | 17 / 19 |
| DAILY_SUMMARY12 | **1594.084** | 1801.865 | **-207.781** | **20 / 19** |
| SIMPLE_RETURNS8 | 1968.009 | 1728.724 | +239.285 | 16 / 21 |
| MIXED20 | 1638.708 | 1728.724 | -90.017 | 19 / 21 |

Interpretation:
- DAILY_SUMMARY12 is a strong and coherent improvement for GBRT in both price error and direction.
- This confirms that the original processed representation was materially handicapping GBRT.

**Stage-3 primary GBRT representation: DAILY_SUMMARY12.**

### LightGBM

| Representation | Candidate SigmaAE | Matched CURRENT8 | Delta | Direction candidate/control |
|---|---:|---:|---:|---:|
| RAW_LEVEL_LAGS8 | **1719.852** | 1832.578 | **-112.725** | 18 / 20 |
| DAILY_SUMMARY12 | 1749.055 | 1832.578 | -83.522 | 18 / 20 |
| SIMPLE_RETURNS8 | 1782.653 | 1858.901 | -76.247 | 20 / 19 |
| MIXED20 | 1720.406 | 1858.901 | -138.495 | 19 / 19 |

Interpretation:
- LightGBM benefits materially from alternative representations.
- RAW_LEVEL_LAGS8 gives the lowest absolute SigmaAE.
- MIXED20 is nearly tied on price and gives a slightly better direction count than RAW.

**Stage-3 primary LightGBM representation: RAW_LEVEL_LAGS8.**
**Balanced challenger: MIXED20.**

### Random Forest anchor

| Representation | Candidate SigmaAE | Matched CURRENT8 | Delta | Direction candidate/control |
|---|---:|---:|---:|---:|
| RAW_LEVEL_LAGS8 | 1766.553 | 1614.491 | +152.062 | 17 / 20 |
| DAILY_SUMMARY12 | **1491.551** | 1614.491 | **-122.940** | 20 / 20 |
| SIMPLE_RETURNS8 | 1824.537 | 1612.170 | +212.368 | 16 / 22 |
| MIXED20 | 1544.475 | 1612.170 | -67.695 | 20 / 22 |

Interpretation:
- DAILY_SUMMARY12 is substantially better for the RF anchor.
- RF remains a comparator, not a Boosting-family production winner.

## Main conclusion

The user's hypothesis was valid: **feature representation materially changes Boosting-family performance.**

But the effect is algorithm-specific:
- CatBoost: CURRENT8 remains best.
- XGBoost: raw levels improve price error but hurt direction.
- GBRT: daily within-month summaries strongly improve both price error and direction.
- LightGBM: raw/mixed representations materially improve price error.
- RF: daily summaries strongly improve price error.

Therefore there is no single universally best input representation for tree ensembles.

The best absolute Boosting score remains:
- **CatBoost Ordered + CURRENT8: SigmaAE 1460.4339, direction 20/33.**

This is still above the strongest existing nonlinear project families (~1413–1416), so Boosting remains promising but is not yet the overall project leader.

## Promotion to Stage 3 — Target & Loss Ablation

Primary lanes:
- CatBoost Ordered → CURRENT8
- XGBoost → RAW_LEVEL_LAGS8
- GBRT → DAILY_SUMMARY12
- LightGBM → RAW_LEVEL_LAGS8
- RF anchor → DAILY_SUMMARY12

Retained challenger lanes:
- XGBoost → CURRENT8 for direction
- LightGBM → MIXED20 for balance

Stage 3 must keep representation fixed within each lane and change only target/loss.

## Engineering failures retained separately

These are not scientific evidence:
1. Run 36312695742 / Job 108601549507 — failed because 3M momentum was not buildable for 2010-03/04.
2. Run 36312847868 / Job 108601955895 — compile failure due literal newline patch artifact.
3. Run 36312989109 / Job 108602357064 — compile failure due second literal newline patch artifact.

Valid evidence:
- Stage 2 common-history run: Run 36313121013 / Job 108602723097 / Artifact 10930260146 / SHA256 72698bb9b645a91391f6dbb84af071e6c8dd4e595580a1d2b9ab85f73d76fe44.
- Stage 2B pairwise-history audit: Run 36313754165 / Job 108604460993 / Artifact 10930530188 / SHA256 d14ed2e0430ceac0e1055e0a01f22a681074477360b3a4db05dad20377228064.

## Kontrol ve Uyum Özeti

- Stage 2: PASS.
- Stage-1 exact reconciliation: PASS.
- Pairwise history fairness: PASS.
- Random split: NONE.
- Hyperparameter tuning: NONE.
- Target/loss changes: NONE.
- 2025/2026 opened: NO.
- DB writes: NONE.
- Feature-representation hypothesis: SUPPORTED, algorithm-specific.
- Overall Boosting leader remains CatBoost + CURRENT8.
- Next stage: Stage 3 Target & Loss Ablation.
