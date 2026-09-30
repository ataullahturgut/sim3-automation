# GOLD MONTHLY — Origin-Safe Gold ETF Anomaly Screen V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING
**Scope:** explain HIGH-APE ChHHO misses using ETF data available by the forecast origin. No routing/model switching.

## 1. Primary question

Do origin-known gold ETF states contain abnormal flow/activity information before ChHHO HIGH-error months, especially the currently unexplained core:

- target 2022-05 / origin 2022-04
- target 2022-07 / origin 2022-06
- target 2022-09 / origin 2022-08
- target 2024-03 / origin 2024-02

Primary error severity is the binding APE V3 definition:
- NORMAL <2.5%
- MEDIUM 2.5%..<3.0%
- HIGH >=3.0%

## 2. Official daily ETF sources

### GLD
SPDR Gold Shares official historical archive:
`https://api.spdrgoldshares.com/api/v1/historical-archive?exchange=NYSE&lang=en&product=gld`

Use:
- Date
- Tonnes of Gold
- Daily Share Volume

### IAU
iShares Gold Trust official historical data download:
`https://www.blackrock.com/varnish-api/blk-one01-product-data/product-data/api/v1/get-fund-document?appSubType=ISHARES&appType=PRODUCT_PAGE&component=fundDownload&locale=en_US&portfolioId=239561&targetSite=us-ishares&userType=individual`

Use Historical worksheet:
- As Of
- Shares Outstanding

These daily fund-level data are contemporaneous and are eligible for origin-safe analysis. Monthly World Gold Council aggregate flow reports may be used only as ex-post corroboration because publication occurs after month-end.

## 3. Calibration window

All ETF anomaly thresholds are calibrated on monthly states from **2010-01..2020-12** only.

No 2021+ ChHHO errors are used to select thresholds.

## 4. Monthly origin features

At each calendar month-end, using the last available official daily observation in that month:

1. `GLD_TONNES_PCT1` = month-end GLD tonnes / prior month-end tonnes - 1.
2. `IAU_SHARES_PCT1` = month-end IAU shares / prior month-end shares - 1.
3. `COMBINED_FLOW` = arithmetic mean of GLD_TONNES_PCT1 and IAU_SHARES_PCT1.
4. `GLD_CHURN` = sum of absolute daily changes in GLD tonnes during the month / prior month-end tonnes.
5. `IAU_CHURN` = sum of absolute daily changes in IAU shares during the month / prior month-end shares.
6. `GLD_VOLUME_RATIO12` = monthly mean GLD daily share volume / prior-12-month median monthly mean volume.
7. `ETF_DIVERGENCE` = absolute difference between GLD_TONNES_PCT1 and IAU_SHARES_PCT1.
8. `OUTFLOW_BREADTH` = count of GLD/IAU monthly changes below zero (0, 1, 2).

## 5. Frozen anomaly flags

Using 2010-2020 calibration only:

- **ETF_OUTFLOW_Q10**: COMBINED_FLOW <= calibration Q10.
- **ETF_GLD_OUTFLOW_Q10**: GLD_TONNES_PCT1 <= calibration Q10.
- **ETF_IAU_OUTFLOW_Q10**: IAU_SHARES_PCT1 <= calibration Q10.
- **ETF_GLD_CHURN_Q90**: GLD_CHURN >= calibration Q90.
- **ETF_IAU_CHURN_Q90**: IAU_CHURN >= calibration Q90.
- **ETF_VOLUME_Q90**: GLD_VOLUME_RATIO12 >= calibration Q90.
- **ETF_DIVERGENCE_Q90**: ETF_DIVERGENCE >= calibration Q90.

Composite:
- **ETF_STRESS_2PLUS** = at least two of the seven frozen anomaly flags are true.

The 2+ rule is fixed before evaluation and is not optimized on ChHHO outcomes.

## 6. Required output

For every scientifically usable 2021-11..2026-08 ChHHO target:
- target/origin
- APE severity
- A/B/C/D/H
- all ETF features
- calibration percentile ranks
- seven ETF anomaly flags
- ETF_STRESS_2PLUS.

Report:
- the four unexplained core HIGH-error origins in detail;
- all HIGH-error targets;
- all ETF_STRESS_2PLUS targets;
- ETF_STRESS_2PLUS precision/recall for HIGH error;
- precision/recall on the four unexplained core cases;
- normal/medium false alarms;
- whether the ETF state is common to all four or splits them into distinct mechanisms.

## 7. Governance

- No target-month ETF data.
- No WGC monthly report used as predictor.
- No threshold retuning.
- No Boolean search across flags after seeing outcomes.
- No routing/model switching.
- A useful ETF anomaly may be promoted only as a candidate warning from this screen.
