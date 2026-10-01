# GOLD SHORT-HORIZON GLOBAL XAU — Historical Target Bridge Authority

**Date:** 2026-10-01  
**Status:** FROZEN PRE-RUN AUDIT  
**Purpose:** replace the mistaken BIST Metal Price tactical target with the already-existing global XAU data stack.

## 1. Candidate target authorities

### Historical development target
- series: `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- prior role: retrospective global XAU research history
- status: research reconstruction, not PIT-proven as an input.

### Prospective / live target anchor
- series: `XAU_EOD_TWELVE_NY17`
- provider: Twelve Data
- symbol: `XAU/USD`
- definition: close of the exact 16:59 America/New_York 1-minute bar, internal 17:00 ET daily reference
- approved canonical live pipeline.

The historical reconstruction is being evaluated only as a **target history**, not as an origin-known predictor.

## 2. Audit questions

1. How much historical XAU coverage already exists?
2. How much NY17 canonical overlap exists?
3. On same trade dates, do historical-target returns match NY17 returns closely enough to treat the old series as a development bridge?
4. Is there a stable level relationship, or only return-level compatibility?
5. Are there duplicate / non-weekday / nonpositive observations?

## 3. Frozen chronology requirement

For a usable H1/H3/H5 global-XAU development program:
- pre-DEV history through 2021: >= 2,000 weekday observations preferred
- DEV 2022-2024: >= 700 eligible origins per horizon
- 2025 remains frozen transport.

## 4. Bridge metrics

On exact common weekday dates between historical XAU and NY17:

- N common levels
- Pearson correlation of daily log returns
- Spearman correlation of daily log returns
- sign agreement
- mean absolute daily-return difference
- return-difference SD
- median level ratio historical / NY17
- level-ratio coefficient of variation.

## 5. Bridge PASS gate

Historical XAU may serve as the development target bridge to NY17 only if:

- common return pairs >= 30
- Pearson return correlation >= **0.90**
- Spearman >= **0.88**
- sign agreement >= **85%**
- daily return-difference SD <= **0.50%**.

Level ratio stability is diagnostic and is not required if the model target is return rather than absolute price.

## 6. Target use if PASS

If bridge PASS:
- global XAU H1/H3/H5 targets are defined on the historical XAU return series for development;
- prospective live target identity is NY17 XAU/USD;
- models predict returns/direction, not an absolute cross-source price level;
- BIST Metal Price is removed from the main tactical target role and retained only as archived prior research.

## 7. If bridge FAIL

Do not silently stitch the two series.
A longer NY17-authority history or another single-identity global XAU history must be obtained before restarting the short-horizon model program.

## 8. No 2025 selection

2025 may be counted for coverage but not inspected for model/horizon selection.
