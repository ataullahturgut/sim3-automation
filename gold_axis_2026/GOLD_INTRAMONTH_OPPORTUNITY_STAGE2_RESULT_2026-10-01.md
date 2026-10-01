# GOLD INTRAMONTH OPPORTUNITY — Stage 2A Core Label Audit Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / SCIENTIFIC_GATE=PASS**  
**Workflow:** Gold Intramonth Opportunity Stage2A  
**Run:** **36860536563**  
**Artifact:** **11161358194**  
**Artifact digest:** `sha256:863b60fdf2ad5b18d749b271ef1f23b0bcad0fd08682627ff5c6bf2913e09da7`  
**Runner commit:** `06e9c1a76e1baedff48a2c27069353e9f097d839`  
**Authority:** `GOLD_INTRAMONTH_OPPORTUNITY_STAGE2_AUTHORITY_2026-10-01.md`

## 1. Main conclusion

The intramonth-opportunity research question is empirically real.

On the frozen monthly ChHHO DEV target months **2022-04..2024-12**:

- 33 monthly forecast months are available;
- ChHHO forecast **DOWN in 19 months**;
- ChHHO forecast **UP in 14 months**.

Among those 19 monthly-DOWN months, using only upward excursions that occur **inside the same calendar month**:

- **18/19 = 94.7%** contain at least one >= **+1%** five-observation opportunity;
- **15/19 = 78.9%** contain at least one >= **+2%** opportunity;
- **7/19 = 36.8%** contain at least one >= **+3%** opportunity.

Therefore:

> A monthly DOWN forecast does **not** imply that the month lacks meaningful tactical upside opportunities.

This validates the business motivation for a separate intramonth opportunity model.

It does **not yet prove predictability**. Stage 3 must test whether origin-known features can identify the opportunity days before they occur.

## 2. Governed Borsa İstanbul panel

Endpoint:
`https://www.borsaistanbul.com/metal-fiyatlari.php?op=fetchMetalFiyatlari`

Frozen filter:
- `priceRef = MTL`
- `priceCurrency = USD`
- `priceWeight = OZ`.

Coverage after filtering:

| Metal | Observations | First | Last |
|---|---:|---|---|
| Gold | 3742 | 2011-01-04 | 2025-12-31 |
| Silver | 3742 | 2011-01-04 | 2025-12-31 |
| Platinum | 3742 | 2011-01-04 | 2025-12-31 |
| Palladium | 2979 | 2012-07-25 | 2025-12-31 |
| All-4 common | 2979 | 2012-07-25 | 2025-12-31 |

Gold/Silver/Platinum have no duplicate dates after the governed filter. Palladium has materially shorter/sparser early history; no synthetic early values were created.

Observed request-level no-data years include:
- Palladium 2011
- Palladium 2013.

Cross-metal feature construction therefore uses causal as-of observations plus staleness age rather than forcing an artificial common-history fill.

## 3. Stage-2 population

Eligible label rows after required history/future windows:

- all historical eligible origins: **3717**
- DEV 2022-2024: **749**
- DEV with frozen monthly ChHHO context: **685**
- DEV origins inside monthly-DOWN months: **392**
- DEV origins inside monthly-UP months: **293**
- 2025 frozen transport eligible rows: **245**.

The difference between all DEV rows and ChHHO-context DEV rows is expected because canonical monthly ChHHO DEV begins at target **2022-04**.

## 4. Five-observation path distribution

DEV 2022-2024:

### MFE5
- mean: **+1.341%**
- median: **+1.023%**
- 75th percentile: **+2.311%**
- 90th percentile: **+3.738%**

### MAE5
- mean: **-0.966%**
- median: **-0.806%**
- 10th percentile: **-2.917%**

Thus the five-observation path contains economically non-trivial positive and negative excursions; a point-price-only target would discard important path information.

## 5. Pre-registered volatility-scaled opportunity labels

Scale:
`SCALE5 = population_std(last 20 Gold returns) × sqrt(5)`.

Candidates:

| Label | Full DEV prevalence | Monthly-DOWN | Monthly-UP | DOWN same-month |
|---|---:|---:|---:|---:|
| K050 | 48.6% | 39.0% | 59.4% | 35.2% |
| K075 | 36.3% | 26.5% | 46.4% | 23.7% |
| K100 | 25.9% | 17.6% | 33.8% | 15.1% |

Interpretation:
- monthly DOWN reduces the base rate of upside opportunity;
- it does not eliminate opportunity;
- all three thresholds retain enough DEV positives/negatives for later modeling;
- no threshold is selected using 2025/2026.

Stage 3 may therefore model continuous MFE/MAE plus the three frozen exceedance probabilities rather than forcing a single threshold prematurely.

## 6. Monthly-DOWN same-month detail

| Target month | Max same-month MFE5 |
|---|---:|
| 2022-04 | 2.32% |
| 2022-05 | 3.21% |
| 2022-06 | 1.72% |
| 2022-07 | 2.78% |
| 2022-08 | 1.94% |
| 2022-09 | 2.61% |
| 2022-10 | 3.25% |
| 2022-11 | 6.62% |
| 2023-01 | 2.93% |
| 2023-02 | 2.64% |
| 2023-06 | 1.56% |
| 2023-07 | 2.29% |
| 2023-09 | **0.86%** |
| 2023-10 | **7.40%** |
| 2024-01 | 4.40% |
| 2024-02 | 4.07% |
| 2024-05 | 3.76% |
| 2024-06 | 2.52% |
| 2024-12 | 2.85% |

Across the 19 monthly-DOWN DEV months:
- median of the month-level maximum same-month MFE5 = **2.78%**
- minimum = **0.86%**
- maximum = **7.40%**.

Only **2023-09** fails even the descriptive +1% same-month opportunity criterion.

## 7. Frozen 2025 transport — descriptive only

No 2025 information was used to define the Stage-2 label family.

Frozen monthly ChHHO forecast DOWN in:
- 2025-01
- 2025-03
- 2025-07
- 2025-11.

Same-month maximum MFE5:
- 2025-01: **2.45%**
- 2025-03: **5.03%**
- 2025-07: **2.70%**
- 2025-11: **4.91%**.

Therefore, descriptively:
- >=1% opportunity: **4/4**
- >=2% opportunity: **4/4**
- >=3% opportunity: **2/4**.

This transport evidence supports the persistence of the phenomenon but is **not label/model selection authority**.

## 8. Prior-only baseline metrics

DEV probability baselines:

| Label | Expanding prevalence Brier | Expanding log loss | Rolling-252 Brier | Rolling-252 log loss |
|---|---:|---:|---:|---:|
| K050 | 0.2503 | 0.6938 | 0.2523 | 0.6977 |
| K075 | 0.2316 | 0.6559 | 0.2329 | 0.6590 |
| K100 | 0.1920 | 0.5723 | 0.1933 | 0.5754 |

Continuous prior-median baselines:

### MFE5
- expanding median MAE(log): **0.01349**
- rolling-252 median MAE(log): **0.01325**

### MAE5
- expanding median MAE(log): **0.01157**
- rolling-252 median MAE(log): **0.01158**.

These become minimum baselines for Stage-3 model screening.

## 9. Scientific interpretation

The evidence answers the first question:

**Does an intramonth upside-opportunity problem exist even under monthly DOWN forecasts? — YES.**

It does not yet answer the harder question:

**Can those opportunity origins be forecast ex ante better than historical base-rate baselines? — NOT YET PROVEN.**

Monthly direction appears useful as context because opportunity prevalence is lower in monthly-DOWN than monthly-UP periods. But the high frequency of meaningful rallies inside DOWN months proves monthly direction cannot be used as a veto.

## 10. Data hashes

- `bist_metal_usd_oz_long.csv`: `19a9ba014905b6cf0358e7ec24d14ff3398d28f353e7ef69a1501c2ffd18e665`
- `bist_four_metal_usd_oz_wide.csv`: `ca701ac58fe3ed7282f3d3d243e0672c86b449d2ef65d26ededbb7eba0133d10`
- `intramonth_opportunity_stage2_dataset.csv`: `551318150e87b80ad87c8f7efac68ef9c35e2ff69b06dc2dccaf40372453a00a`
- `monthly_chhho_context.csv`: `724dcf1faf76b13633b0c75fc94c81068784de6cce84e647b7df350c7f1a9ce6`
- `dev_monthly_context_opportunity_summary.csv`: `db84fcb5f58bcb20275c8f1ce8af6a6bd19f1a8ed6aaa8467264183579bd3ba8`

## 11. Decision

**Stage 2A = PASS.**

The opportunity target is viable and sufficiently populated.

Exact next research stage:

**Stage 3 — Origin-Safe Intramonth Opportunity Predictability Screen**

Stage 3 must determine whether pre-outcome features can beat the frozen prior-probability and prior-median baselines for:
- MFE5
- MAE5
- K050
- K075
- K100.

Monthly context must first be excluded from the core model and later tested as an incremental block so its added value can be measured rather than assumed.
