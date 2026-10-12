# E5 prospective lockbox — capture protocol, stage 1 (2026-10-12)

**Status:** operational **validation/append code is created**, but automated forecast publication and real bank quote capture are **NOT active**. No real forecast or bank quote has been inserted. Do not describe this as deployed or as an untainted backtest.

## Objective
Create a source-aware, prospective record that distinguishes data feature cutoff, actual forecast issuance, DAY 09:00–16:45 TR outcome and OVN 16:45→next 09:00 TR outcome. Real Turkish bank bid/ask is to be collected at actual decision/exit times; no synthetic spreads, no credentials.

## Available implementation
- `tools/gold_e5_prospective_ledger.py`: append-only local timestamp captured from the runtime clock; events `FORECAST`, `BANK_QUOTE`; rejects forecast issued after session start; validates full git model SHA + input snapshot SHA; fixed Europe/Istanbul clocks; JSON key allow-list prohibits attaching arbitrary private account information; chained SHA-256 record hashes and monotonic timestamps. Quotes require provider, product, currency, unit and bid<=ask.
- `prospective/GOLD_E5_PROSPECTIVE_EVENTS.ndjson`: **empty initialization**, zero authentic observations. New submissions must be reviewed and committed promptly to a branch; Git commit server time plus immutable remote commit SHA is external provenance (hash-chain alone is not a cryptographic timestamp authority).
- `.github/workflows/gold-e5-prospective-ledger-validation.yml`: PR/push validation and synthetic self-test, with **read-only** repository permission. It does **not** generate forecasts, poll banks or append rows.
- Direct CLI: `python3 gold_axis_2026/tools/gold_e5_prospective_ledger.py --self-test`; `--validate`; `--append-forecast path/to/forecast_payload.json`; `--append-quote path/to/quote_payload.json`. The CLI captures system UTC time. Do not backdate payload.
- Forecast payload keys: `session, window_start, window_end, feature_cutoff, model_git_sha, model_name, prediction, probability_up, data_snapshot_sha256`. Session DAY/OVN; permitted signal UP/DOWN/ABSTAIN; probability may be null.
- Bank quote keys: `provider, product, currency, unit, bid, ask`. Never include account holder, account/card numbers, tokens, passwords. Record whether bank product is TRY/gram and XAU/USD is USD/oz; do not cross units.

## Launch gates: NOT YET SATISFIED
1. Obtain a single owner-approved, truly frozen **execution-time** model and reproducible source **input snapshot** with timestamp and SHA. Never repurpose old H3 label as a live intraday forecast without its future-only target.
2. Confirm an actual authenticated forecast execution provider (GitHub Actions runner permissions and any needed connectors) can read market data before 08:45 / 16:30 TR, and prove latency/PIT. GitHub Actions scheduled jobs do not guarantee exact-minute execution. There is no such verified job in this PR.
3. Agree how to collect bank quotes (manual timestamped observation or an authorized official data export) at 09:00, 16:45 and optionally 17:00; do not scrape authenticated bank UI with credentials. Collect bid/ask unit/currency both sides.
4. Store records immediately to GitHub with protected history; a local journal not committed before the target is known is **not** a tamper-proof prospective lockbox. Build a server-side signed timestamp or CI provenance before calling records immutable.
5. Pre-register cohort inclusion, no-trade policy, costs, bank spread vs spot, missed issuance, review every 20 trading days, no model updates during one locked cohort.
6. Never present hypothetical cost results as actual profit.

## Future normal sequence
Decision day's DAY forecast record before 09:00 TR; quote 09:00 and 16:45 TR. OVN forecast before 16:45 TR Mon–Thu; quote 16:45 and next day 09:00. If no timestamp-safe forecast exists, record no forecast; **never retro-create it**. Only after a complete, time-stamped history score directional, risk, MAE, quote-adjusted outcome and coverage.

Implementation is intentionally unable to invent quotes or generate forecasts. Merging this PR activates a validation workflow only, **not** autonomous trading, quote polling, model retraining or scheduling.
