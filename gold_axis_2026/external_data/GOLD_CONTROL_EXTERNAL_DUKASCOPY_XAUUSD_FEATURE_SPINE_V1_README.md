# GOLD CONTROL — EXTERNAL DUKASCOPY XAUUSD FEATURE SPINE V1

**Date:** 2026-09-22  
**Identity:** `EXTERNAL_DUKASCOPY_XAUUSD_FEATURE_SPINE_V1_RESEARCH`  
**Purpose:** stage older intraday XAUUSD evidence needed to investigate pre-2022 SQRT/Router support.  
**Authority:** RESEARCH STAGING ONLY — NOT GOVERNED MODEL INPUT YET.  
**Production DB writes:** FORBIDDEN.

## Source

Public historical XAUUSD one-minute bid/ask OHLC files mirrored in:
`kevingtlin/Market-Data-Lab`

The repository states the files were downloaded from Dukascopy using `dukascopy-node`, timestamps are UTC, and bid/ask are stored separately.

No raw third-party minute files are copied into this repository.

Instead, the import produces compact **derived daily research features** from an inner join of bid and ask timestamps:

`mid_close = (bid_close + ask_close)/2`

The joined 1-minute series is downsampled to 5-minute last-close bars, then grouped by `America/New_York` calendar date to mirror the existing Gold Control research conventions.

## Derived features

For each retained weekday with at least 240 five-minute bars:

- last 5m mid close;
- bar count;
- realized variance `sum(r^2)`;
- realized third moment `sum(r^3)`;
- downside realized variance `sum(r^2 where r<=0)`;
- positive realized semivariance;
- negative realized semivariance;
- average and maximum bid/ask close spread.

## Staged period

Initial requested extension:
- 2018
- 2019
- 2020
- 2021

This window is sufficient to investigate 2020/2021 parent and Router formation while retaining overlap with the governed 2020+ internal cache for source-harmonization tests.

## Binding limitation

These external-source derived features MUST NOT be pooled into the frozen SQRT/Router calibration merely because they increase sample size.

Before any model use, an overlap audit against `public.xau_intraday_research_cache_5m` must assess:
- date coverage;
- close-return sign agreement;
- close-return correlation;
- realized-risk rank/correlation;
- high-risk alarm concordance under identical formation rules.

If source harmonization is not adequate, this dataset remains an independent external-replication asset only.

## Governance

- no 2025 model tuning;
- no raw third-party redistribution in the project;
- no production writes;
- no runtime promotion;
- provenance blob SHAs must be stored with each derived-year audit.
