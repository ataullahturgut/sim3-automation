# R34 — CIG-D1 %74.40 old daily reference: Turkey clock & cross-vendor 24-hour-price reconciliation

> **CRITICAL FOLLOW-UP SOURCE DISCOVERY (R34B, binding):** The original StakTrakr daily reference is NOT one uniform UTC-day mean or one fixed Turkey clock. Its 2026 rows are mixed: 29 LBMA-labeled Gold prices (strong AM 10:30 London price fit), 8 MetalPriceAPI seed values, 4 StakTrakr seed values, and 104 `sqld` daily averages in the original 145. See `GOLD_R34B_20261011_CIG_D1_MIXED_LBMA_AM_METALPRICEAPI_SQLD_TARGET_CLOCK_PROVENANCE_RESULT.md`. Below UTC/TR 24h reconstructions are **alternative uniform cross-source proxies**, not the original mixed target's verified timing. Do not infer a single tradable entry or exit from their accuracy.


**As of:** 2026-10-11. **Scope:** historical source-clock forensic on the exact frozen 2026 Jan–Jul CIG 125 predictions. **NO model refit/retuning, no retroactive H3 promotion, no executable bank P&L.**

## 1. Why this exists

The user correctly noted that the **original CIG-D1 objective was a one-day movement** and must be translated to the appropriate Turkish **source observation period** before declaring its old 74.40% score wrong. Earlier analyses comparing the old prediction against 09TR–17TR, or post-08NY intraday windows, measured **other endpoints**. Those are valid *transfer tests*, not valid refutations of the originally labeled D1 objective.

Recover exact 125 CIG predictions (93/125 = 74.40%) from
`GOLD_CIG_EXACT_125_ROWS_2026-10-06.csv`. Frozen 145 legacy daily-reference prices from `GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv`, where a label compares current reference price against **previous available reference date**, including the six-date gap. **Never compare a new-vendor price to the old-vendor prior price when defining the proxy direction.** All proxy labels compare **new vendor to same new vendor, same averaging window**, on paired original dates.

Independent historical quote candidates use the private Neon **direct Dukascopy monthly native-H1 archive**
`gold_research_dukascopy_xau_h1_monthly_source_candidate_v1` (BID/ASK OHLC, `utc` bar-START timestamps, historical retrieval NOT original live PIT). Its H1 file can contain **calendar-padded closed hours**, so it is fit for retrospective numerical comparison only, not a valid proof of real 24h liquidity.

### Candidate definitions, in Turkey time (no Turkish DST)

1. **UTC calendar day, 24h hourly quote arithmetic mean:** 2026-D UTC 00:00–24:00. **Türkiye saati D 03:00–D+1 03:00**. Exactly 24 Dukascopy H1 ASK-open sampled prices at UTC hours 00..23 (TR 03..next02), then equal-weighted mean. Direction = **today's 24h price mean vs previous available *day's* 24h price mean**. This is **not the point-to-point 03TR buy-to-03TR sell return**.
2. **Türkiye calendar day, 24h hourly quote arithmetic mean:** Türkiye D 00:00–D+1 00:00, equivalently previous UTC day 21:00 through current UTC day 20:00 hourly samples. Same mean-vs-prior-mean direction rule.
3. **Specific clocked spot prices for falsification:** 09:00TR, 17:00TR, end UTC23:00; must not mislabel a one-point close-vs-close return as a daily mean.
4. **Independent publisher corroboration already executed 2026-10-06:** Twelve Data 1h UTC calendar-day mean of hourly closes, `GOLD_CIG_EXACT125_REFERENCE_CLOCK_AUDIT_2026-10-06.json`: 125/125 observations, **old label agreement 88.0%**, **CIG score 67.20% = 84/125**, independent of Dukascopy's quote values. This supports *daily-mean-like label semantics*, not exact StakTrakr source contract.

## 2. Actual SQL-assisted numerical results

Same 145 frozen legacy daily reference price values. 2026 Jan–Jul direct H1 archive has 24 H1 hours per calendar day; price-level matching is **not** direction-accuracy matching.

| 24h source candidate | 145-day price median absolute difference | 145-day price MAE | Exact 125 old CIG predicted directions vs that new-source *paired daily mean* | Agreement old-source vs new-source labels |
|---|---:|---:|---:|---:|
| Dukascopy ASK-open, UTC daily mean (**03TR–next03TR**) | **USD 1.89** | **USD 11.76** | **87/125 = 69.60%** | **113/125 = 90.40%** |
| Dukascopy ASK-open, Türkiye calendar-day mean (**00TR–next00TR**) | USD 8.56 | USD 14.79 | **96/125 = 76.80%** | **108/125 = 86.40%** |
| Previous original daily reference | zero by definition | zero | **93/125 = 74.40%** | 125/125 |
| Twelve Data 1h UTC mean, earlier published independent audit | Not calculated on matched 145 prices | Not calculated | **84/125 = 67.20%** | **110/125 = 88.00%** |

**How the 125 counts were reconstructed:** On 124 original 125 rows with a prior reconstructed 2026 legacy date, UTC mean was 86/124, TR mean was 95/124. The remaining first signal **2026-01-02** has prior original reference date **2025-12-31** (not Jan 1 holiday): direct H1 UTC ASK means 2025-12-31 **4327.4108**, 2026-01-02 **4358.4574**, both UP; direct H1 TR-calendar ASK means 2025-12-31 **4330.3487**, 2026-01-02 **4357.1533**, both UP. Its frozen CIG prediction UP was correct for both, yielding 87 and 96 correct in 125. Exact source label matches add +1 to 112/124 UTC and 107/124 TR. Never use the old source price as the new source prior.

**Clock selection warning:** The **best price-level reconstruction** is the **UTC 00–24 mean**, not the TR-calendar mean; the latter's 96/125 result is a **post-hoc inspected alternative**, and a higher accuracy alone cannot identify the original publisher's clock. 2026 is multiply investigated and not virgin out-of-sample. USD 11.76 daily MAE includes substantial outliers; median USD 1.89 does not mean an exact per-date equality. No single exact bid/ask tradeable 24h entry/exit clock is proven by a **daily-average target**.

**Subperiod numerical reproducibility:** On Jan–Apr original 66 CIG dates, same source UTC mean 47 correct; TR mean 52 correct. On May–Jul original 59 CIG dates, UTC 40 correct, TR 44 correct. Strictly price-window transfer is NOT a new model score, because the CIG consensus inherited H3 experts and the daily source is historical/reconstructed and chosen retrospectively.

## 3. Real-date source crosschecks

- **2026-01-02** old daily reference **4307.95 prior -> 4386.85 current = UP**, model UP correct. Direct Dukascopy **UTC mean** 2025-12-31 4327.4108 -> 2026-01-02 4358.4574 = UP; **TR day mean** 4330.3487 -> 4357.1533 = UP. This is a true same-period daily-mean comparison, not a 09–17 spot return.
- **2026-01-07** old daily reference 4452.75 -> 4459.55 = UP, model UP counted correct. Direct H1 **UTC-day mean** around 4469.48 -> 4461.01 = **DOWN**. Thus 1day quote vendor and price construction can reverse marginal directions. Same day/source clock and provider identity matter.
- **2026-01-30** old daily reference 5501.70 -> 5063.45 = DOWN, model DOWN counted correct; Dukascopy daily UTC mean also fell sharply. The source-level absolute differences can be ~USD 27 that day, even while direction agrees.
- **2026-04-03 Good Friday** historic daily reference has an UP label and model UP; Dukascopy direct source has **96/96 M15 bars flat** and no real market throughout the day. Calendar-filled vendor quote rows must **NOT** be used as an executable market session. Report source-direction comparisons with and without such days separately before model approval.

## 4. Minimal SQL reproduction (Neon PRIVATE data only)

```sql
-- Exact UTC calendar-day 24-hour hourly ask-open average; 24 source rows
SELECT (utc AT TIME ZONE 'UTC')::date AS d,
       COUNT(*) AS n, AVG(ask_open) AS utc_mean_ask
FROM gold_research_dukascopy_xau_h1_monthly_source_candidate_v1
WHERE utc >= '2025-12-31' AND utc < '2026-08-01'
GROUP BY 1
HAVING COUNT(*) = 24
ORDER BY 1;

-- Exactly local Istanbul-calendar 24-hour average, not UTC result relabeling
SELECT (utc AT TIME ZONE 'Europe/Istanbul')::date AS d,
       COUNT(*) AS n, AVG(ask_open) AS tr_mean_ask
FROM gold_research_dukascopy_xau_h1_monthly_source_candidate_v1
WHERE utc >= '2025-12-30' AND utc < '2026-08-02'
GROUP BY 1
HAVING COUNT(*) = 24
ORDER BY 1;
```

Merge exact frozen 125 `issue_date,consensus_pred,actual_daily_label` rows and the 145 historical daily-reference file. For each issue row, derive prior legacy date from the previous **available** dated reference ledger row, except 2026-01-02 which uses 2025-12-31. Calculate UP when `new_source_mean(issue_date)>new_source_mean(prior_legacy_date)`, else DOWN. No source merging when defining direction and no model retraining. Source-level monthly H1 is an independently downloaded Dukascopy file and not proof of live executable prices.

## 5. Interpretation and next binding correction

**The 74.40% old CIG forecast has genuine cross-source daily-average directional support; the earlier 47.20% post-issue spot-window rescore was a DIFFERENT TARGET and cannot invalidate the original D1 one-day reference task.**

But identifying a 24-hour **daily mean averaging interval** does **not** automatically produce 24-hour tradable entry and exit instants; a return from 03TR to next 03TR is not the change between two UTC-day average prices. Nor can already-ended intraday prices be treated as known at 09TR or a model issue earlier than official source-ready time.

Future research: 1) obtain original StakTrakr daily-reference *aggregation operator* and timestamp authority; 2) check source-ready timing of every original consensus member, feature cutoff and frozen expert state; 3) compare fixed 24h **point-to-point** Turkish return windows and fixed daily-mean targets **separately**, with predeclared windows; 4) reject closed holidays and calendar padding; 5) evaluate consistent earlier years 2023–25 without using the same post-hoc clock selection; 6) do not claim bank-transaction profit without actual venue spread.
