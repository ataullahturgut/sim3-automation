# GOLD H3 — REVERSAL INFORMATION EXTENSION CLOSURE

**Date:** 2026-10-03  
**Scope:** post-Phase-1–9 R&D extension after HELIOS V6 admissibility failure.  
**Status:** **NO NEW PROMOTED REVERSAL SPECIALIST**

## 1. Objective

Continue searching for genuinely new reversal information rather than retuning HELIOS V5 on the same OPAL candidate universe.

This extension pursued:
1. official GC futures open-interest access salvage;
2. a new price-path CHANGEPOINT representation;
3. public directional options-flow sources;
4. an official OCC GLD call/put specialist.

## 2. GC futures Open Interest salvage

CME's public daily-volume archive is discoverable, including historical dated XLSX files.

The correct public archive family was identified under:
`/ftp/pub/pub/pub/daily_volume/`.

However automated requests from the GitHub runner returned HTTP 403 under CME anti-scraping controls. No bypass was attempted.

Result:
- official historical GC OI remains unavailable in the current execution environment;
- full FLOW-H3 Volume+OI remains **UNTESTED / ACCESS-BLOCKED**, not failed.

## 3. CHANGEPOINT-H3 V1

A distinct specialist was preregistered before fit.

Mechanism:
- first differences of origin-safe path states;
- signs normalized so positive = weakening of current momentum;
- z60 innovation shocks;
- weakening impulse / CUSUM persistence;
- selected second differences.

DEV 2023-2024 result:
- no threshold satisfied precision >=45% and candidate-rate <=40%;
- status **NO_ELIGIBLE_CHANGEPOINT_THRESHOLD**;
- 2025/2026 remained unopened.

Representative thresholds:
- 0.40: precision 33.33%, recall 73.58%, candidate rate 62.07%;
- 0.55: precision 32.23%, recall 36.79%, candidate rate 32.10%.

Interpretation:
price-path innovations identify broad deterioration zones but are still not selective enough to form a new reversal-candidate channel.

## 4. Public options-source audit

### Cboe
The official historical-options page and its own JavaScript exposed a public class-download endpoint.

A GLD probe confirmed:
- daily total options volume by exchange is downloadable;
- free export does not provide call/put direction in that payload;
- tested OI mode is not available through that endpoint.

Therefore Cboe free class-volume export was not relabeled as directional skew.

### OCC
OCC's public Volume Query batch interface was verified and is materially richer.

For exact option class GLD it provides:
- Call / Put indicator;
- Customer / Firm / Market Maker account type;
- exchange;
- activity date;
- volume quantity.

The public retention window is approximately 24 months. 2023 is rejected; 2024-10-04 onward was verified.

A separate OCC daily-open-interest probe showed that the free daily OI download is aggregate market OI by asset class, not GLD-specific OI.

## 5. OPTIONS-FLOW-H3 V1

Evidence class:
`SHORT_HISTORY_OFFICIAL_OCC_AUTHORITY`.

Source:
- official OCC GLD options volume;
- 498 accepted source dates;
- 2024-10-04 through 2026-09-30;
- all 498 accepted dates retrieved with a single BOTH call/put transport.

Origin rule:
- strict prior source date;
- same-date OCC activity forbidden;
- maximum source staleness 5 calendar days.

Frozen period roles:
- 2024-Q4 warm-up / formation;
- 2025-H1 DEV;
- 2025-H2 confirmation only if DEV passes;
- 2026 final holdout only if confirmation passes.

Frozen feature family included:
- total and customer log put/call ratios;
- one-day PCR changes;
- total/customer call-put imbalances;
- backward-looking z20 states;
- volume shock;
- customer-vs-market-maker divergence;
- all conditioned on current Gold momentum direction.

Model:
- standardized balanced logistic regression;
- monthly expanding refit;
- training restricted to AURORA-follows-momentum origins.

### DEV result

Eligible 2025-H1 origins: 84  
True reversals: 36

| Threshold | Precision | Recall | Candidate rate | Eligible |
|---:|---:|---:|---:|---|
| 0.35 | 44.29% | 86.11% | 83.33% | NO |
| 0.40 | 43.94% | 80.56% | 78.57% | NO |
| 0.45 | 42.86% | 66.67% | 66.67% | NO |
| 0.50 | 42.86% | 50.00% | 50.00% | NO |
| 0.55 | 41.67% | 41.67% | 42.86% | NO |
| 0.60 | 31.82% | 19.44% | 26.19% | NO |

Binding status:
**NO_ELIGIBLE_OPTIONS_FLOW_THRESHOLD**

Therefore:
- 2025-H2 confirmation was not opened;
- 2026 holdout was not opened;
- no threshold was relaxed after seeing results;
- no HELIOS routing rule was created.

## 6. Scientific interpretation

OPTIONS-FLOW V1 is the strongest new accessible information-channel attempt in this extension, but it still does not meet the preregistered selectivity requirement.

At threshold 0.35:
- recall is high (86.11%);
- precision is close to the 45% gate (44.29%);
- but candidate rate is far too high (83.33%).

This is not a usable candidate generator under the current architecture.

The accessible OCC feed is also limited relative to the strongest options-order-flow literature:
- it identifies call vs put and account type;
- it does **not** identify buyer-vs-seller initiated direction;
- it does **not** identify opening-buy flow in the public aggregate used here;
- it is therefore not equivalent to signed option order imbalance or buyer-to-open put/call measures.

Accordingly:
- do not lower the candidate-rate gate merely to promote this result;
- do not claim that directional option information itself is disproven;
- CME CVOL / true signed order flow remain different information sets.

## 7. Binding project state

HELIOS V5-DCE remains binding.

No new 2026 score is created in this extension.

The research evidence is now stronger that:
1. price-path-only reformulations have reached a selectivity ceiling;
2. gross futures volume is insufficient;
3. coarse cross-asset divergence is insufficient;
4. public aggregate call/put activity is more promising but still too broad;
5. a meaningful next leap likely requires information closer to actual position change / signed flow / implied-distribution asymmetry, rather than another classifier over the same state variables.

## 8. Evidence

CHANGEPOINT:
- `GOLD_H3_CHANGEPOINT_V1_PREREG_2026-10-03.md`
- `GOLD_H3_CHANGEPOINT_V1_RESULT_2026-10-03.md`
- run `37141776408`.

OPTIONS-FLOW:
- `GOLD_H3_OPTIONS_FLOW_V1_PREREG_2026-10-03.md`
- `GOLD_H3_OPTIONS_FLOW_V1_RESULT_2026-10-03.md`
- `GOLD_H3_OPTIONS_FLOW_V1_SUMMARY_2026-10-03.json`
- `GOLD_H3_OPTIONS_FLOW_V1_THRESHOLD_GRID_2026-10-03.csv`
- source evidence commit `ac041db97cdf7c445617d5b429afde18c68241e2`.
