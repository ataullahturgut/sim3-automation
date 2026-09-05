# Gold Control — Macro Event Successor V1 Consensus Provider Decision

Date: 2026-09-05
Branch: `gold-control-macro-event-successor-v1-source-contract`
Engine identity: `MACRO_EVENT_SUCCESSOR_V1`
Scope: doctoral-research source/provider decision only. No model score, direction vote, Forecast Store write, or Decision Store write is authorized by this document.

## 1. Decision

For this doctoral-research path, the working historical event-level consensus source is **Investing.com Economic Calendar**.

The user explicitly chose Investing.com for internal doctoral research after the paid Trading Economics path was judged too costly. This is a research-governance decision, not a legal conclusion about Investing.com licensing. Investing.com terms currently state that use/storage/reproduction of site data requires prior written permission. Therefore this source is classified **RESEARCH_ONLY_DOCTORAL_INTERNAL / USER_ACCEPTED_LICENSE_RISK** and is not promoted as a licensed production authority source.

Provider hierarchy for this research path:

1. **Investing.com Economic Calendar** — primary research consensus source for normalized historical `Forecast` values.
2. **Reuters pre-release economist survey reporting** — independent public spot-check lane for selected releases.
3. **Bloomberg Economic Calendar historical consensus** — preferred professional benchmark if entitlement becomes available later.
4. **Trading Economics PIT** — optional paid validation source only; not required for the current doctoral path.

## 2. Frozen event components

The consensus input universe remains limited to the U.S. BLS Employment Situation event family:

- headline `Nonfarm Payrolls`
- `Unemployment Rate`
- `Average Hourly Earnings (MoM)` for all employees on private nonfarm payrolls

No extra macro indicators may be added during this source phase.

## 3. Investing.com semantics and binding rules

Investing.com Economic Calendar states that:

- `Forecast` / `Consensus` is the consensus estimate from economists before the data is released;
- `Previous` is the prior reporting-period value;
- `Actual` is populated when the official number is released.

Binding rules for Gold Control:

- Only the Investing.com **Forecast/Consensus** value is eligible as the research consensus input.
- Investing.com `Actual` is **not** the authority actual. BLS/ALFRED first-release reconstruction remains the actual-data authority lane.
- We do not claim the Investing.com page preserves the exact final pre-release update timestamp unless separately proven.
- Therefore historical consensus reconstructed from the calendar is eligible **no earlier than the official BLS release timestamp**, tagged `PRE_RELEASE_CONSENSUS_PRESERVED_ON_INVESTING_CALENDAR_RESEARCH_RECONSTRUCTION`.
- It must not be used for any decision timestamp strictly before the official release.
- Missing consensus is fail-closed. It is not filled from another provider after viewing model results.
- Provider identity is frozen for the research dataset; no per-origin provider switching is allowed.

## 4. Storage / redistribution rule for this doctoral path

Because the source terms contain explicit restrictions on use/storage, this project will minimize retained material:

- do **not** archive raw Investing.com HTML or bulk page content in the public repository;
- do **not** redistribute the Investing.com dataset;
- retain only normalized research fields required for reproducibility: event date, reference month, event identity, consensus numeric value/unit, source URL/reference, retrieval timestamp, evidence classification, and hash/provenance metadata;
- label every retained consensus observation `RESEARCH_ONLY_DOCTORAL_INTERNAL` and `USER_ACCEPTED_LICENSE_RISK`;
- do not represent this dataset as a licensed production data feed.

The project should seek permission or replace the provider before any external/commercial deployment.

## 5. Audit gates before scoring

Before Investing.com consensus can enter Macro Event historical scoring, the following must pass on multiple separated release dates and then on the intended historical coverage window:

1. The three frozen indicators are identifiable without ambiguity.
2. `Forecast/Consensus` is present and numerically parseable.
3. Event date and reference month align with the BLS/ALFRED first-print reconstruction.
4. Units are frozen (`thousand_persons_change`, `percent`, `percent_mom`).
5. Missing values remain missing; no imputation from Reuters, Bloomberg, Trading Economics, previous consensus, or current pages.
6. Selected releases are independently spot-checked against Reuters where available.
7. No current-vintage actual substitutes for BLS/ALFRED first print.
8. No raw page archive is committed to the public repository.
9. No model score, direction vote, Forecast Store write, or Decision Store write occurs during source audit.

## 6. Current stop point

- BLS current machine access: proven.
- ALFRED initial-release access: proven.
- ALFRED-as-of construction vs selected BLS first releases: proven on the frozen sample audit.
- Investing.com calendar semantics for `Forecast/Consensus`, `Actual`, and `Previous`: publicly documented.
- Investing.com provider selection for internal doctoral research: **USER AUTHORIZED**.
- Investing.com source classification: **RESEARCH_ONLY_DOCTORAL_INTERNAL / USER_ACCEPTED_LICENSE_RISK**.
- Historical coverage audit: **PENDING**.
- Model scoring: **NOT AUTHORIZED YET**.
- Forecast/Decision Store writes: **NOT AUTHORIZED**.

Next executable action: build and run an Investing.com historical consensus coverage/reconciliation audit for NFP, unemployment, and AHE; if coverage passes, create a separate normalized research-ingestion bundle for Neon and then proceed to the frozen historical Macro Event score replay.
