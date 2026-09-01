# GOLD CONTROL — XAU EOD DECISION SOURCE CHANGE CONTROL

**Status date:** 2026-09-01  
**Manifest:** `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.3  
**Stage:** 4 — Deterministic R4.1 Decision Engine / Issuer  
**Decision:** `TWELVE_XAUUSD_EOD_TECHNICALLY_QUALIFIED_NOT_APPROVED`

## 1. Purpose

This record evaluates whether a new daily XAU/USD source can become the canonical EOD decision-price source for frozen R4.1 without silent provider substitution or undocumented session semantics.

No production source is promoted by this document. No Neon market observation is written by this change-control step.

## 2. Existing live-data candidates remain non-authoritative

- `XAU_DAILY_XAUS` remains Tier C / operational cross-check / `CANDIDATE_NOT_BENCHMARK`. Its disclosed upstream Yahoo lineage does not make it settlement/EOD authority.
- `XAU_SPOT_XAUS` remains `APPROVED_INDICATIVE_NOT_SETTLEMENT` monitoring only.
- Therefore neither existing XAUS series is promoted or overwritten.

## 3. Authority benchmark considered but not equivalent to R4.1 daily close

`LBMA_GOLD` is the authority-grade benchmark candidate already named in `source_contracts.json`, but model use is licence-gated.

The LBMA Gold Price is an IBA-administered benchmark set twice daily at 10:30 and 15:00 London time. The PM benchmark is therefore a defined London auction benchmark, not a generic 24-hour XAU/USD EOD close. Replacing the frozen R4.1 daily close with LBMA PM would be a timing/market-definition change and requires a separate architecture decision plus applicable licensing.

## 4. Twelve Data XAU/USD candidate identity

Candidate:

- provider: `Twelve Data`;
- symbol: `XAU/USD`;
- provider classification returned by probe: `Precious Metal`;
- Twelve reference identity: `Gold Spot / US Dollar`, Commodity Aggregate;
- supported market schedule in provider reference: `24/7`;
- provider exchange timezone in reference: `Australia/Sydney`;
- candidate endpoints: `/time_series` with `interval=1day` and `/eod`;
- daily/weekly/monthly intervals use provider exchange-local date semantics.

This is a vendor-defined EOD surface. It is not represented as an LBMA settlement benchmark or exchange settlement price.

## 5. Protected live feasibility probe

GitHub Actions run `33504422651`, job `99844972295`:

- protected `TWELVE_DATA_API_KEY` present;
- `XAU/USD` `1day` time-series access: PASS;
- `/eod` access: PASS;
- returned symbol identity: `XAU/USD`;
- returned type: `Precious Metal`;
- raw market values logged: NO;
- EOD value logged: NO;
- database writes: NONE.

Result:

`TWELVE_XAUUSD_EOD_ACCESS_PROVEN`

## 6. Read-only source bridge against current XAUS daily series

GitHub Actions run `33504774858`, job `99846111870` used:

- Neon transaction `SET TRANSACTION READ ONLY`;
- current `XAU_DAILY_XAUS` only as comparison surface, not authority;
- protected Twelve XAU/USD daily history;
- exact frozen R4.1 Fast, Slow, Emergency Level, Reversal Alert and classification functions;
- canonical VW monthly references from `production_closure/production_2026.csv` for Emergency comparison;
- no raw price values in public logs;
- no database writes.

Common comparison window:

- dates: `2026-03-11` through `2026-08-31`;
- common dates: `120`.

Observed bridge metrics:

| Metric | Result |
|---|---:|
| Median absolute level gap | 0.254712% |
| P95 absolute level gap | 0.944068% |
| Maximum absolute level gap | 2.952721% |
| Daily return correlation | 0.878266 |
| Daily return-sign agreement | 83.193% |
| Frozen Fast-state agreement | 89.000% / 100 eligible dates |
| Frozen Slow-state agreement | 100.000% / 103 eligible dates |
| Emergency Level agreement | 98.990% / 99 eligible dates |
| Reversal Alert agreement | 98.990% / 99 eligible dates |
| R4.1 classification agreement across UP/DOWN/NEUTRAL monthly-direction cases | 95.960% / 297 cases |

Interpretation:

`TWELVE_XAUUSD_IS_NOT_A_SILENT_EQUIVALENT_OF_XAU_DAILY_XAUS`

The candidate tracks the same underlying market closely, especially for Slow and Emergency states, but the source/session definition changes some frozen R4.1 states. It therefore cannot be substituted under the existing series identity or approved merely because price levels are close.

## 7. Current decision

`TWELVE_XAUUSD_EOD_TECHNICALLY_QUALIFIED_NOT_APPROVED`

Reasons for qualification:

- direct vendor access is proven with the existing protected credential;
- daily history and EOD endpoint are available;
- instrument identity is explicit;
- provider schedule/timezone semantics are documentable;
- historical overlap is sufficient for a first source-bridge audit;
- Slow/Emergency/classification agreement is high.

Reasons approval is not yet issued:

- provider-defined `Australia/Sydney` EOD is a material decision-time/session definition;
- Fast-state agreement is not identity-level;
- overall R4.1 classification changes in a non-zero share of audited cases;
- no existing canonical contract authorizes Twelve XAU/USD as the R4.1 EOD decision source;
- source promotion must create a new explicit lineage rather than mutate XAUS history.

## 8. Promotion contract required before any ingestion

If this candidate is approved under change control, implementation must use a new series identity, provisionally:

`XAU_EOD_TWELVE`

Minimum frozen fields before first write:

- provider and API endpoint identity;
- source symbol `XAU/USD`;
- unit `USD/troy_oz`;
- frequency `1day`;
- exact observation-date/session definition;
- provider exchange timezone `Australia/Sydney`;
- incomplete-current-bar rejection rule;
- first-retrieval / historical-availability policy;
- immutable payload/lineage hashing;
- licence/use note;
- role = canonical R4.1 EOD decision-price candidate/approved source, never settlement benchmark unless separately proven;
- no overwrite or relabelling of `XAU_DAILY_XAUS` or `XAU_SPOT_XAUS`.

Only after the source contract is explicitly approved may the Stage 4 sequence proceed to successful daily ingestion, immutable H=1 forecast input snapshot, forecast contract, canonical issuer and first `PROSPECTIVE_SHADOW` Decision Store record.

## 9. Blocker state after this audit

The original blocker remains open but is narrowed from source discovery to source-change approval:

`NO_APPROVED_CANONICAL_XAU_EOD_DECISION_SOURCE`

Narrowed sub-state:

`TWELVE_XAUUSD_SYDNEY_EOD_SOURCE_CHANGE_APPROVAL_REQUIRED`

No `LIVE_PRODUCTION` promotion is authorized by this record.
