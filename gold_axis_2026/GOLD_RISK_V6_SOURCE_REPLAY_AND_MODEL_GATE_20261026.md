# GOLD RISK V6 — verified source-feature replay, model deployment gate (2026-10-26)

**Read-only execution completed** using independently downloaded original official-source artifact bytes (GitHub Actions 40277837580, 40278659820) and independent read-only Neon price checks; no model weights, thresholds, live integrations, Neon tables, schedulers or forecast models changed.

## Executed checks (NOT claim of finished model replay)

1. Six original official file SHA256 hashes all matched the archived acquisition audit (SLV issuer XML, FRB H15 CSV, 2023–2026 Treasury TIPS curve CSV).
2. Parsed **958 SLV** historical daily source dates, **994 H15** weekday-date rows, **953 10Y real yield** numeric dates (2023–Oct 2026). No source-date duplicates. Exactly two missing SLV outstanding shares (2024-03-29, 2024-03-31), **42 H15 blank/ND** per 2Y and 10Y; no fabricated zeros.
3. Under the original BASE14 after-US-close issue assumption **17:30 America/New_York**, built **994 Monday–Friday as-of research rows** from Jan 2023 to Oct 2026. H15 same-day only after documented **16:15 New York** publication; SLV and Treasury TIPS are delayed to next US weekday 09:00 New York **UNVERIFIED RESEARCH PROXIES**; raw date+value vintage certainty is NOT proven. Real data available in **988** rows, H15 2Y/10Y in **989**, historical share-change proxy in **986**; gaps NOT filled with zero. Computed non-null nominal/TIPS 5-day deltas from valid released observations, and refused a share delta when any publisher source row in its lookback lacks share count. Tested March/April 2024 share gap and known 2026 research scenarios.
4. Independently queried Neon daily gold PRICE_SQL lineage restrictions as in `gold_monthly_h1_neon_source_v2.py` (2010–2025 original version plus pinned 2026 git snapshot) and confirmed the expected **2025 three next-day >=3% drawdown origins**: 2025-04-22, 2025-05-09, 2025-10-21. Under the documented Feb-27-2026 bad-reference quarantine the **2026 four origins** are 2026-01-29, 2026-01-30, 2026-02-04, 2026-06-09. **Critical lineage check:** A naive 2026 query against differently-versioned public price observations produces extra apparent events in March/June and cannot be used as a reproduction of the existing BASE14 source. Use pinned PRICE_SQL, not mixed vintage sources.
5. Illustrative research-only SLV outstanding-share delta across last five issuer rows at 17:30 NY (using previous-day data): **2026-01-29 -18.8 million**, **2026-03-30 +5.7 million**, **2026-08-11 +2.7 million**. Other real 2025 downside events had mixed signs: **2025-04-22 +5.2 million**, **2025-05-09 -1.6 million**, **2025-10-21 +0.55 million**. Hence a negative SLV-share-change rule would miss prior large selloffs and is NOT eligible for promotion. These are exploratory, affected by unknown original first-publication and potential later source revisions.

## Scientific gates and locked execution plan

- Incumbent **BASE14** must remain the primary major-drawdown reference. The earlier matched BASE14/CFTC21 comparison found 2026 next-day 3% recall **4/4 both**, but for 5-day 5% risk origin groups BASE14 **4/4**, CFTC21 **2/4**; independent earliest-before-fall prediction is NOT proven. These are **previously archived results**, **NOT re-executed in V6**.
- Two different objectives: (A) daily >=3% next-day drop, (B) minimum of next 5 trading sessions <=-5%, reported separately with event clusters, pre-onset warning, false-alarm *origin days* and alert episode counts. Compare models on strictly identical eligible origins.
- Frozen 2023–24 fit -> 2025 exploratory validation; frozen refit to 2025 -> 2026 historical stress; **no 2026-specific threshold or rule chosen to remove March 30–April 3 / August 11 alerts**. The 2026 cases are already seen, NOT fully blind future evidence.
- NO zero imputation; use verifiable source publication timestamps; missing values unavailable => drop that candidate row only under transparent paired-origin selection. H15 historical archive is not vintage-certified; SLV and Treasury real-yield T+1 are not proven first-publication. GLD archives and CFTC position data need a separate originals hash and first-publication review; CME GC/SI still absent.
- Do not call new feature value a certified signal, gold cashflow, silver tonnes, or a calibrated probability of selloff. New research-only covariates are quarantined from the live risk engine.
- **BLOCKED:** Full paired old/new model score replay in this V6 turn: original `risk-overlay-source` snapshot ZIP and separate 398-row quality-gated CFTC GC/SI CSV used for V2 model scoring are NOT among downloaded raw-source artifacts in working research environment. Without those exact files and a reproducible risk script run, **no new false-positive reduction, sensitivity improvement, or retrained model claim is valid**. No new 2026 score re-fit was done. Do not substitute independently generated price or proxy data without re-checking the original source contract.

## Code/artifact

Created and **executed** independent companion script `gold_risk_source_features_v6_20261026.py` locally with genuine BlackRock/FRB/Treasury bytes, producing research-only daily as-of candidate CSV, dated event source CSV and machine-readable source gate. Self checks included SHA256, schema, duplicate dates, XML exact bare ampersand repair, all historical NA gaps, DST-aware as-of rules, and missing-row share delta quarantine. The current run produced downloadable research package for manual audit. Source ingest/vintage certification and matched model-run gate remain distinct.

Original publisher references:
- H15: https://www.federalreserve.gov/data/releaseschedule.htm
- CFTC 2026: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm
- CFTC shutdown revisions 2025: https://www.cftc.gov/PressRoom/PressReleases/9147-25
- Treasury 10Y real: https://home.treasury.gov/policy-issues/financing-the-government/interest-rate-statistics
- SLV: https://www.ishares.com/us/products/239855/ishares-silver-trust-fund

**V6 status: SOURCE AS-OF RESEARCH FEATURE EXECUTION PASS; FULL PAIRED MODEL BACKTEST NOT RUN; LIVE MODEL GATE CLOSED.**
