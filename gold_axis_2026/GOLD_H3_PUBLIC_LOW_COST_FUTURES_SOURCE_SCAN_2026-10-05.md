# GOLD H3 — PUBLIC/LOW-COST 2023–2024 FUTURES SOURCE SCAN — 2026-10-05

## Objective
Find a practical source for 2023–2024 1-hour GC/SI/NQ/ZN/CL data so the frozen H3 LLRS/Handoff/DPTC lineage can be replayed without silently substituting spot/ETF/CFD proxies.

## Decision summary

### 1. Databento — PRIORITY A / strongest exact-source candidate
- Dataset: CME Globex MDP 3.0 (GLBX.MDP3), covering CME/CBOT/NYMEX/COMEX.
- Historical coverage: 16+ years.
- Schema includes OHLCV-1h.
- Supports futures continuous symbology directly.
- Continuous symbols map to actual tradable instruments and return original, unadjusted prices.
- Available roll rules: calendar (c), prior-day open interest (n), prior-day volume (v).
- Candidate bridge symbols:
  - GC.c.0 / GC.n.0 / GC.v.0
  - SI.c.0 / SI.n.0 / SI.v.0
  - NQ.c.0 / NQ.n.0 / NQ.v.0
  - ZN.c.0 / ZN.n.0 / ZN.v.0
  - CL.c.0 / CL.n.0 / CL.v.0
- New accounts advertise $125 historical-data credits.
- Metadata cost estimation is free before downloading data.

Scientific use:
1. Use 2025 frozen Yahoo LLRS panel only as source-bridge calibration.
2. Compare c.0 / n.0 / v.0 per channel on aligned hourly timestamps.
3. Freeze the matching rule without looking at DPTC outcomes.
4. Require return-direction, rolling-return, timestamp/session and GC/SI volume stability.
5. Then fetch 2023–2024 and replay frozen LLRS/IFBC/DPTC.

Status: BEST CANDIDATE. Requires a Databento API key/account.

### 2. MarketParquet — PRIORITY B / validated-bridge candidate, not exact lineage by default
- GC, SI, NQ, ZN, CL are all explicitly covered.
- 1-hour OHLCV history extends back to 2008 for these products.
- 2023–2024 therefore covered.
- However futures are continuous and ratio-back-adjusted.
- This differs from Databento's unadjusted continuous contract approach and may differ from Yahoo =F roll behavior.
- Full archive: $79 one-time; free intraday sample is only one week.

Scientific use:
- Can be tested against the 2025/2026 frozen Yahoo panel.
- It can only become a source-bridged reconstruction if downstream LLRS/IFBC score stability passes.
- Do not call it exact Yahoo-lineage data solely because the root symbols match.

Status: STRONG FALLBACK / CHEAP FULL ARCHIVE.

### 3. Massive Futures API — PRIORITY C
- Direct CME/CBOT/NYMEX/COMEX futures.
- Minute aggregates on free plan; individual futures contracts.
- Free plan currently advertises 2 years historical data, which is insufficient for full 2023 from Oct-2026.
- Developer plan ($79/month) advertises 5 years history.
- Continuous contracts are listed as coming soon, so 2023–2024 would require explicit contract discovery + roll construction.

Status: technically usable, but more reconstruction work than Databento.

### 4. Sierra Chart Historical Data Service — PRIORITY C
- CME/NYMEX/COMEX/CBOT intraday data originates from CME MDP feeds.
- Historical intraday extends well before 2023.
- Access is tied to Sierra Chart service packages and desktop workflow rather than a lightweight research API.

Status: exact market data possible, operationally less convenient.

### 5. Barchart — PRIORITY C
- Advertises historical intraday data back approximately 10 years, down to 1-minute.
- Supports individual futures contracts and Nearby continuous futures.
- Requires subscription/tool access for deep downloads.

Status: viable paid fallback; roll semantics must be bridged.

### 6. FirstRate Data / Kibot — PRIORITY D
- Both advertise deep futures intraday history and continuous series.
- Paid commercial datasets.
- Useful only if higher-priority sources fail.

### 7. FMP — NOT ENOUGH FOR EXACT FIVE-CHANNEL LLRS
- Has 1-hour commodity endpoints such as GCUSD and commodity benchmarks.
- Useful for gold/silver/oil research.
- Does not establish the same five-channel CME futures lineage, especially NQ and ZN, under the frozen LLRS contract.
- Treat as proxy/alternative research only.

### 8. GitHub/Kaggle/HuggingFace public scan
- Public GitHub searches found many scripts/notebooks referencing Yahoo futures and a few locally cached 1h files.
- One Finance_data repo logged paths such as futures_datasets/1h/ZN=F_1h.csv, but the actual data files are not committed in the repository.
- Other public repositories either contain only code, recent 2025/2026 data, a subset of channels, or gitignored local databases.
- No trustworthy public repository containing the complete 2023–2024 five-channel hourly panel was verified.

Status: NO COMPLETE PUBLIC FREE PANEL VERIFIED.

## Recommended next move
Do not alter DPTC. The best next move is a Databento source-bridge probe:
- request metadata.get_cost first for 2025 bridge windows and then 2023–2024;
- test GC/SI/NQ/ZN/CL under c.0, n.0, v.0 continuous rules;
- choose the source mapping solely on price/return/session/volume agreement with frozen 2025 Yahoo data, never on outcome labels;
- if the bridge passes, fetch 2023–2024 and replay frozen DPTC Q95/Q99 unchanged.

## Governance
This scan does not establish 2023/2024 DPTC performance and does not promote any new source into the canonical lineage. It identifies acquisition/bridge candidates only.
