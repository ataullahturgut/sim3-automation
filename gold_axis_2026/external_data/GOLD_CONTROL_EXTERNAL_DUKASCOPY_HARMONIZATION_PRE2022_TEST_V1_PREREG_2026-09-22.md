# GOLD CONTROL — EXTERNAL DUKASCOPY HARMONIZATION + PRE-2022 PARENT TEST V1 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `EXTERNAL_DUKASCOPY_HARMONIZATION_PRE2022_TEST_V1_RESEARCH`  
**External source:** staged Dukascopy-derived XAUUSD mid 5m daily feature spine, 2018–2021  
**Governed overlap source:** `public.xau_intraday_research_cache_5m`  
**Runtime authority:** NONE  
**Production DB writes:** FORBIDDEN

## 1. Purpose

Determine whether the newly staged older Dukascopy intraday data are sufficiently harmonized with the governed Gold Control 5-minute source to be used for a pre-2022 research extension of SQRT-HAR-DR and frozen Router-V2-style analysis.

This is a source-harmonization test before any pooled LTT calibration claim.

## 2. Overlap window

Use exact common retained weekdays between:
- external Dukascopy-derived daily features;
- governed `xau_intraday_research_cache_5m`.

Expected overlap begins 2020-04-06 and continues through 2021-12-31.

No nearest-date joins.

## 3. Feature comparisons

On exact common dates report:

1. date coverage;
2. daily close log-return Pearson correlation;
3. daily close-return sign agreement;
4. realized variance Pearson and Spearman correlation;
5. downside realized variance Pearson and Spearman correlation;
6. positive/negative semivariance Pearson and Spearman correlation;
7. scale ratios external/governed for RV and DR;
8. top-quintile DR event agreement using source-specific 80th-percentile thresholds over the common overlap.

## 4. Harmonization gate

External source is `HARMONIZED_FOR_RESEARCH_EXTENSION` only if all hold:

- exact overlap >= 90% of governed retained weekdays in the overlap window;
- close-return sign agreement >= 90%;
- close-return Pearson correlation >= 0.95;
- DR Spearman correlation >= 0.80;
- RV Spearman correlation >= 0.80;
- source-specific top-quintile DR event agreement >= 75%.

Scale ratios need not equal 1 because venue/feed/mid construction can change intraday noise scale; they are diagnostic, while rank/event agreement is binding.

If the gate fails, do not pool external pre-2022 parent alarms with governed 2022+ alarms.

## 5. Pre-2022 extension — only if harmonization gate passes

If and only if the harmonization gate passes:

- reconstruct SQRT-HAR-DR annual-origin parent on external data for 2020 and 2021, using the exact frozen parent equations and source-specific formation thresholds;
- reconstruct the five direct UP experts and legacy context using the exact frozen definitions;
- evaluate Router-V2-style yearly formation using Y-1 common rows;
- report SQRT alarm anatomy and Router-UP intersection.

These external years remain clearly labeled `EXTERNAL_SOURCE_EXTENSION`; they do not become governed production history merely by passing this research gate.

## 6. 2025 restriction

No 2025 data are used anywhere in this study.

## 7. Governance

- exact chronological/origin-safe reconstruction;
- no random split;
- no production writes;
- no runtime promotion;
- no weakening of LTT alpha/delta.
