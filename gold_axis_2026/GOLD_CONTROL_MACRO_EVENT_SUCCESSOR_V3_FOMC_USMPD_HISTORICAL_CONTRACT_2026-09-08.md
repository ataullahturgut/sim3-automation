# Gold Control — Macro Event Successor V3 FOMC USMPD Historical Contract

Date: 2026-09-08
Engine: `MACRO_EVENT_SUCCESSOR_V3`
Family: `FOMC`
Lane: `HISTORICAL_REPLAY_RECONSTRUCTION`
Status: **FROZEN BEFORE V3 HISTORICAL TEST / RESEARCH CHALLENGER ONLY**

## 1. Change-control boundary

This contract does not replace the prospective/live CME-FedWatch contract. It adds only a historical/model-test lane after explicit user authorization to use the free San Francisco Fed source.

No production promotion, BUY/SELL mapping, Market Shock threshold change, raw Market Shock episode deletion, V2 mutation, canonical merge, or decision-authority write is authorized.

## 2. Authority source

Historical FOMC event-study source: Federal Reserve Bank of San Francisco, U.S. Monetary Policy Event-Study Database (USMPD), official `USMPD.xlsx`.

Method source: the SF Fed-provided `monetary-policy-surprises.zip`, specifically `gss.R`, implementing the Gürkaynak-Sack-Swanson target/path factor construction from statement-window changes in `MP1`, `MP2`, `ED2`, `ED3`, `ED4`.

The SF Fed describes statement changes as 30-minute high-frequency windows around FOMC statement releases. USMPD is historical event-study evidence; it is not relabeled as prospective evidence.

## 3. Source fields

Core statement inputs are exactly:

- `MP1`
- `MP2`
- `ED2`
- `ED3`
- `ED4`

The FOMC event timestamp is the USMPD `Statements.date_time` timestamp interpreted in `America/New_York`, consistent with Federal Reserve announcement timing documented by USMPD.

Unscheduled statement events are retained and explicitly tagged; they are not silently deleted.

## 4. Leakage-safe GSS factor construction

To avoid using future FOMC observations to determine historical factor weights, the GSS transformation is fitted once on complete statement observations dated before `2016-01-01` and then frozen.

Development/calibration period:

`1994-01-01 <= event_date < 2016-01-01`

Evaluation period:

`event_date >= 2016-01-01`

The fitted transformation reproduces the SF Fed `gss.R` construction:

1. standardize `MP1, MP2, ED2, ED3, ED4` using development-sample means and sample standard deviations;
2. obtain the first two principal components from the development covariance matrix;
3. rotate the factors so the second factor has no effect on `MP1`, following the GSS rotation in SF Fed `gss.R`;
4. normalize target so it moves `MP1` one-for-one in the development sample;
5. normalize path so its effect on `ED4` equals the target factor's effect on `ED4` in the development sample;
6. apply the frozen development transformation to 2016+ events without refitting.

No 2016+ outcome, gold price, Market Shock output, or reaction result may influence the factor loadings or normalization.

## 5. V3 FOMC score

The existing V3 robust-scoring convention is retained.

For each evaluation event, using only prior FOMC factor observations for scale estimation:

- robust scale = `1.4826 * MAD`; IQR fallback; population-SD fallback only if required;
- minimum prior count = `24`;
- `z_target = target / prior_scale_target`;
- `z_path = path / prior_scale_path`;
- positive target/path surprise is hawkish, therefore gold-adverse;
- oriented components = `[-z_target, -z_path]`;
- family score = mean of the two oriented components;
- strong threshold = absolute score `1.0`;
- breadth requirement = both components (`2/2`) must point in the same gold direction.

States:

- `GOLD_ADVERSE_MACRO_SHOCK`
- `GOLD_SUPPORTIVE_MACRO_SHOCK`
- `MACRO_MIXED_OR_SMALL`

No result-dependent threshold adjustment is authorized.

## 6. Persistence

Neon writes are append-only research/evidence-spine writes only.

Raw/factor series:

- `MACRO_FOMC_USMPD_MP1`
- `MACRO_FOMC_USMPD_MP2`
- `MACRO_FOMC_USMPD_ED2`
- `MACRO_FOMC_USMPD_ED3`
- `MACRO_FOMC_USMPD_ED4`
- `MACRO_FOMC_GSS_TARGET_FROZEN2015`
- `MACRO_FOMC_GSS_PATH_FROZEN2015`

Derived model series:

- `MACRO_EVENT_V3_FOMC_SCORE`

Historical reconstruction metadata must retain the source URL, workbook SHA-256, retrieval timestamp, event timestamp, scheduled/unscheduled flag, calibration cutoff, and evidence class. `available_as_of` must not be falsely backdated to imply that the current SF Fed workbook was retrieved historically.

## 7. Historical Macro Event reaction test

The test is frozen before results are inspected.

Primary historical reaction window:

`2021-01-01` through `2025-12-31`.

For every strong V3 event from Employment, Inflation, or FOMC with complete 1-minute XAU cache support:

- pre-event close: event timestamp minus 1 minute;
- R5 close: event timestamp plus 4 minutes;
- primary R15 close: event timestamp plus 14 minutes;
- R30 close: event timestamp plus 29 minutes.

Expected direction:

- `GOLD_ADVERSE_MACRO_SHOCK` -> negative XAU return;
- `GOLD_SUPPORTIVE_MACRO_SHOCK` -> positive XAU return.

Primary overall gate, inherited from the V2 reaction-validation convention:

- one-sided exact sign-test `p <= 0.10`; and
- median signed R15 `> 0`.

Family-level results are diagnostics and must be reported separately. Missing XAU bars are reported as unsupported; they are not imputed.

## 8. Evidence semantics

- USMPD historical source: `HISTORICAL_REPLAY_RECONSTRUCTION`.
- Historical V3 score: `HISTORICAL_REPLAY_RECONSTRUCTION`.
- Historical reaction test: `HISTORICAL_REPLAY_RECONSTRUCTION`.
- No historical result may be presented as prospective/live evidence.
