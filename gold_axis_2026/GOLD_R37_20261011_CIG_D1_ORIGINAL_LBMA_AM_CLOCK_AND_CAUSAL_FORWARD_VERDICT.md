# R37 — FINAL old CIG-D1 source-clock and real-forward evaluation: original platform confirmed, 2023–25 LBMA AM, 2025 80.73% vs 54.13% causal clock

**Audit date 2026-10-11. FINAL for legacy original-model meaning.** No model refit, vote modification, clock search to maximize accuracy, false retrospective issued-at guarantee, bank P&L, or new champion promotion. Sources: (i) original 2025 frozen CIG exact 218 signal rows, (ii) **original 2023/24/25 StakTrakr price provider**, (iii) independent native HistData 2023–25 M15 source, (iv) source-authoritative IRIS and H3 issuance code. Supersedes prior overconfident descriptions of 74.40% as "one future tradable day" or "09TR–17TR" and clarifies R34–R36.

## 1. This is the OLD ORIGINAL platform, not a new quote source chosen to redefine it

Original model DAILY inputs: `gold_axis_2026/tools/gold_short_horizon_global_xau_readiness_r2.py` downloads `lbruton/StakTrakr/data/spot-history-{year}.json`, old original R2 freeze `54fdf1c8d39b7b6c7b874d0f30f784296e886044`. Daily Gold reference is the **dated** `spot` value, not a quote timestamp; `YYYY-MM-DD 12:00:00` in Stak year files is a **synthetic date tag** not a live fix at noon UTC. Original 2023 Gold daily records **251/251 seed/LBMA**, 2024 **254/254 seed/LBMA**, 2025 **253/253 seed/LBMA**. The original 2025 CIG selection is `GOLD_OLD_CIG_2025_EXECUTION_TARGET_ROWS_2026-10-07.csv` (218 real reconstructed 4/4 unanimous signals; original experts unchanged), origin `forecast_issue_date`.

Old H3 additional INTRADAY predictors: original `gold_axis_2026/tools/gold_h3_iris_v1.py` uses `api.twelvedata.com/time_series?symbol=XAU/USD&interval=1h&timezone=America/New_York` and archival Neon `XAU_USD_TWELVE_1H_RESEARCH_V1`; allowed H3 hourly cutoff = **16:00 New York PRIOR feature date**, and old CIG governed issue deadline = **08:00 New York on forecast date**. Twelve Data is a **feature provider**, not the old `Gerçekleşen` Gold target.

2026 original frozen 125 consensus target is additionally impacted by mixed providers and price versions: Jan2–Feb11 LBMA, Feb12–20 plus Mar9 MetalPriceAPI, Feb23–26 StakTrakr spot, Mar10–Jul31 private `sqld` arithmetic mean of UTC-date `spot`. The original 2026 **93/125=74.40%** remains reproducible as **MIXED source-label score**. Source target 2025 is homogeneous LBMA; source target 2026 is **NOT** homogeneous. The old independent 2026 daily realization series matches the public pinned `ed2e549f82ba0d1cd3ca32842b82d3888d301e01` Stak vintage; the earlier original R2 input pinned `54fdf1c8...` is a different vintage. Never assert identical 2026 labels without a vintage join.

## 2. 2023–2025 original LBMA daily prices correspond to London's **AM** benchmark, NOT 03TR–03TR daily mean

Direct price-value matching to the original historical Stak daily data, against the independently acquired **HistData XAU/USD M15** source `gold_research_histdata_xau15m_candidate` (2023–25 15-minute bars). All times are correctly **Europe/London-local** before conversion to **Europe/Istanbul = UTC+03 fixed**; British GMT/BST shifts applied by timezone. Comparison is absolute USD/oz deviation between old original Stak `seed/LBMA spot` price and HistData 15m market `open_price` at the specified local London clock.

| Year | Original Stak Gold daily LBMA rows | M15 matched 10:30 London | MAE at **10:30 AM** | M15 matched 15:00 London | MAE at **15:00 PM** |
|---|---:|---:|---:|---:|---:|
| 2023 | 251 | 239 | **$1.33** | 191 | $6.38 |
| 2024 | 254 | 254 | **$2.00** | 254 | $8.41 |
| 2025 | 253 | 253 | **$3.90** | 253 | $12.71 |

At 10:45 London prices were sometimes **even slightly closer** than the M15 10:30 opening print (2023 $1.32, 2024 $1.86, 2025 $3.35), unsurprising because the LBMA AM auction **begins** at 10:30 and the final fixing time is variable. This supports **AM benchmark identity**, NOT an exact trade at 10:30 sharp. Official LBMA: gold auctions 10:30 AM and 15:00 PM London; ICE says **no guaranteed exact final-price publication time** because final auction round varies. Official citations: https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices and https://www.ice.com/iba/lbma-precious-metals .

Concrete original-source to HistData M15 clock matches:
- **2025-01-02** original Stak LBMA $2644.60, M15 London10:30 $2644.568, gap **$0.032**.
- **2024-07-15** $2408.50 vs London10:30 $2408.228, gap **$0.272**.
- **2025-07-07** $3306.00 vs London10:30 $3310.205; London15:00 $3309.398. Individual days can be closer to PM; aggregate original-year evidence, not choosing on single day, determines the plausible AM identity.
- Secondary Dukascopy H1 full 2025 March-Dec subset at London10:00 (85 original matched dates) MAE $4.66; London11:00 $2.75; London15:00 $14.18; corroborates AM, though H1 hourly sampling is coarser and coverage limited.

**Türkiye AM clock:** British winter GMT 10:30 = **13:30 Türkiye**. British summer BST 10:30 = **12:30 Türkiye**. The AM auction's FINAL settlement occurs after that start, at variable time. There is no universal 02:00–02:00 or 03:00–03:00 original model target for 2023–25.

## 3. Crucial causality: the old reported same-day LBMA movement is largely formed BEFORE old governed issue

Original `GOLD_D1_CIG_V1_RESULT_2026-10-05.md` scores `sign(LBMA_AM(issue_date) - LBMA_AM(prior_original_weekday))`, while old issued forecast deadline `08:00 America/New_York` on `issue_date`: **15:00 or 16:00 Türkiye** according to US DST. London's AM auction begins **12:30 or 13:30 Türkiye** according to UK DST. Thus at the governed issue deadline, the AM auction has *already started* **1.5–2.5 hours earlier** and would ordinarily already have been finalized, though exact individual auction final publication timestamps were not logged.

This is a **temporal target/issue misalignment**: the original old **2025 176/218=80.73%** was NOT the accuracy of post-issue price direction. Do **NOT** infer feature lookahead leakage from this alone; old H3 features were nominally prior-cutoff only. Also do **NOT** invent historical physical issuance logs: 08NY is a governing deadline, not an independently verified archived `issued_at` for each retrospective row.

It is plausible that some/all old frozen signals could be emitted **earlier on issue date** because their last hourly IRIS observation is 16NY **prior day** (23TR prior day during US DST, 00TR issue day during winter); but this earlier issue and every dependent feature release time **have not been proved**. Even when issued 09TR before AM, original **previous-AM→current-AM** label already includes most price movement *before 09TR* and must not be called 09TR→AM transaction direction.

## 4. Critical empirical result: exact 2025 frozen 218 old CIG votes, original source, FIXED new endpoints

Reused the existing independent source `GOLD_OLD_CIG_2025_EXECUTION_TARGET_ROWS_2026-10-07.csv` (218 old consensus directions, H3 reconstruction identity previously confirmed QA PASS: V5 165/248 H3, SAGE/RuleFlow 171/248 H3, CIG 218/248). Re-read original `lbruton/StakTrakr` 2024,2025,2026 dated Gold `seed/LBMA` prices at frozen original model pin `54fdf1c8...`. No trained model rerun. For market spot comparisons use independent HistData XAUUSD 15min at precise timezone-aware dates: `09:00 Europe/Istanbul`, `08:00 America/New_York`, `17:00 Europe/Istanbul`, `10:30 Europe/London`.

| Old forecast compared to actual market interval | Same frozen old votes | Success | Interpretation |
|---|---:|---:|---|
| **Original old target:** prior available LBMA AM (day D-1) → issue-day LBMA AM (day D) | **176/218** | **80.73%** | Correct original historical LABEL count; **not post-08NY issuance return**. |
| **After official forecast issue:** **08:00 New York issue-day spot → next available LBMA AM** | **118/218** | **54.13%** | Proper strictly **post-issue timestamp** start, counterfactual signal at governing deadline; **always UP baseline 118/218 = 54.13%**. |
| LBMA AM day D → next available LBMA AM day D+1 | **117/218** | **53.67%** | Fixed same-vendor **one full benchmark-to-benchmark forward day**; always UP on same 218 dates **125/218 = 57.34%**, so old signal loses. First price is already known before old issue deadline, so point-to-point reference rather than executable entry. |
| **Before-fixing hypothetical:** **09:00 Türkiye issue-day spot → 10:30 London same-day spot** | **121/218** | **55.50%** | **Same-vendor HistData M15** spot-to-spot; always UP **121/218 = 55.50%**. Historical early-issued signal *NOT certified*. |
| **Before-fixing hypothetical:** **09:00 Türkiye spot → original same-day LBMA AM reference price** | **117/218** | **53.67%** | Cross-source spot to benchmark; always UP baseline 113/218=51.83%; early issue *NOT certified*. |
| **Post-issue bankish:** 17:00 Türkiye day D spot → next day's LBMA AM | **108/218** | **49.54%** | Spot-to-benchmark; always UP 116/218 =53.21%. |
| 17:00 Türkiye D → next eligible day 09:00 Türkiye | **106/216** | **49.07%** | Existing frozen source-clock rescore, `GOLD_OLD_CIG_2025_EXECUTION_TARGET_RESCORE_RESULT_2026-10-07.md`. |
| 09:00 →17:00 Türkiye same day | **114/217** | **52.53%** | NOT executable at 09TR by the original governed 15/16TR issuance; price-label transfer only. |

**Major conclusion:** Old **80.73% historical same-day label agreement collapses to 54.13% on the very same 218 decisions when the evaluated price move is genuinely after the governed issue timestamp; this is identical to the naive always-UP baseline.** Not proof old signal lacks any future predictive relationship for any possible redesigned time or earlier issuance, but definitively NOT evidence of a bank-ready 80%-accurate daily model.

**Exact observed 2025 original-vs-forward:** Of 218 forecasts, 176 matched old D-1 AM→D AM sign; only 117 match the NEXT benchmark D AM→next D+1 AM sign. 111/218 issue dates have different old vs next-benchmark labels. 85 originally correct calls become incorrect for next LBMA benchmark, whereas 26 originally wrong become correct. This is a large *paired target-label shift* without changing any model forecast.

**Concrete row 2025-01-03:** model UP; original 2025-01-02 AM $2644.60 → Jan03 AM $2654.30 = UP (old "correct"). But after forecast deadline on Jan03 NY08:00 HistData spot $2655.095 → Monday Jan06 original LBMA AM $2631.80 = DOWN (new "wrong"). **2025-01-06:** model DOWN; original Jan03 AM $2654.30 → Jan06 AM $2631.80 = DOWN old correct, but NY08:00 Jan06 spot $2645.065 → Jan07 AM $2644.40 is marginal DOWN, direction *happens to be correct* for NY08→nextAM while *AM dayD→nextAM* is UP. Time-origin specificity matters.

## 5. 2026 January/February same-original-source confirmatory subset

Original old 125 frozen CIG forecast CSV `GOLD_CIG_EXACT_125_ROWS_2026-10-06.csv` + original daily Stak snapshot `ed2e549...` yields **25 4/4 consensus LBMA** calls Jan2–Feb11. Same-source next available LBMA benchmark exists for all 25:
- Old D-1→D AM reference direction: **18/25 = 72.00%**;
- Shift the frozen vote to D AM→next LBMA AM: **13/25 = 52.00%**;
- Next LBMA AM reference UP on these dates **17/25 = 68%** (always UP baseline). Small N; supports the 2025 finding but not standalone power.

Other 2026 periods use MetalpriceAPI, Stak spot seed or `sqld` UTC daily average; do NOT present an ex-post 2026 mixed-source clock as one continuous 24-hour tradable period.

## 6. Verifiability and operational verdict

Reproduce original 2025 218 calls from `GOLD_OLD_CIG_2025_EXECUTION_TARGET_ROWS_2026-10-07.csv` as `forecast_issue_date,consensus_pred`. Fetch original raw historical `lbruton/StakTrakr` at `54fdf1c8d39b7b6c7b874d0f30f784296e886044` files `data/spot-history-{2024,2025,2026}.json`, Gold rows only, exact source `seed/LBMA` in 2025, sorted date. For each forecast at D calculate preceding available Gold price and next available Gold price; the old label is current > preceding, true post-deadline reference label is next > current. Independently query `gold_research_histdata_xau15m_candidate` from Neon for `open_price` timestamp `08:00 America/New_York` issue day and `09:00 Europe/Istanbul` issue day. The 08NY→nextAM output is from **HistData market spot at model governed issuance hour**, compared with **old Stak LBMA AM next day**; a cross-provider direction test affected by small spreads/benchmark quote differences, not a fee-adjusted return. HistData 09TR→LBMA_AM M15 and 2025 original same-source AM clock search provide cross-checks.

**Research decision:** Keep old CIG H3 experts and valuable previous-day state signals as experimental ingredients; **retire 74.40% (2026) and 80.73% (2025) as evidence of daily executable direction accuracy**. Old 80% is numerically real for original **earlier benchmark-labeled** D1 target but temporally inconsistent with governed issuance. At **the old issue time**, the rigorously matched 2025 score is **54.13%**, equal to always-UP baseline, and cannot be promoted. The earlier user intuition about source-specific Turkey hours was correct: most source history Gold LBMA AM, not arbitrary 09TR/17TR, and later 2026 switches to UTC calendar mean. All scoring must continue from one fixed **origin-safe** time contract (e.g. 08:45TR issue→09TR market entry→09TR after 3 actual eligible days), untouched training and correct BID/ASK fills, with a real prospective lockbox. Do not invent a new >=70% short-term result from this audit.
