# Gold Control — Macro Event Successor V2 Event-Reaction Validation Result

Date: 2026-09-05
Engine: `MACRO_EVENT_SUCCESSOR_V2`
Validation: `MACRO_EVENT_SUCCESSOR_V2_EVENT_REACTION_VALIDATION_V1`
Evidence class: `HISTORICAL_REPLAY_RECONSTRUCTION`

## Result

Final reproducible workflow run: `33980279756`
Validated HEAD: `5636d003cb7e0fc69da01ebbaa2a7ac705e00846`
Workflow conclusion: `SUCCESS`
Validation status: `PASS_EVENT_REACTION_EVIDENCE`
Promotion status: `ELIGIBLE_FOR_PROMOTION_CHANGE_CONTROL`

The reaction methodology was frozen before the corresponding gold returns were inspected. The final workflow uses the preregistered 15-minute primary reaction window from the close of the 08:29 ET bar to the close of the 08:44 ET bar around the 08:30 Employment Situation release.

## Frozen VAL+LOCK event evidence

Eight V2 strong-shock events were evaluated. Seven moved in the preregistered gold direction over the primary 15-minute window.

| Reference month | Release date | V2 macro state | R15 % | Directional hit |
|---|---|---|---:|---|
| 2021-02 | 2021-03-05 | GOLD_ADVERSE_MACRO_SHOCK | +0.085486 | NO |
| 2021-04 | 2021-05-07 | GOLD_SUPPORTIVE_MACRO_SHOCK | +1.068453 | YES |
| 2021-07 | 2021-08-06 | GOLD_ADVERSE_MACRO_SHOCK | -1.090097 | YES |
| 2022-01 | 2022-02-04 | GOLD_ADVERSE_MACRO_SHOCK | -0.846016 | YES |
| 2022-07 | 2022-08-05 | GOLD_ADVERSE_MACRO_SHOCK | -0.849710 | YES |
| 2023-01 | 2023-02-03 | GOLD_ADVERSE_MACRO_SHOCK | -1.352256 | YES |
| 2023-04 | 2023-05-05 | GOLD_ADVERSE_MACRO_SHOCK | -1.251172 | YES |
| 2024-01 | 2024-02-02 | GOLD_ADVERSE_MACRO_SHOCK | -0.675211 | YES |

Aggregate result:
- directional hits: `7/8` = `87.5%`;
- exact one-sided Binomial(0.5) sign-test p-value: `0.03515625`;
- preregistered p-value gate: `<= 0.10` → PASS;
- median signed R15: `+0.9590818647119803%`;
- preregistered median signed R15 gate: `> 0` → PASS.

The sole 15-minute miss is reference month `2021-02` / release date `2021-03-05`: the V2 state was adverse but R15 was `+0.085486%`. The same event's descriptive R5 was `-0.363774%` and R30 was `-0.154470%`; these secondary windows were preregistered as descriptive only and do not alter the primary-window result.

## Engineering and governance checks

- exact frozen 8-event set used;
- exact governed macro source run `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a` used;
- Twelve Data `XAU/USD`, 1-minute, `America/New_York` source used with no fallback;
- all 8 events had the required frozen bars;
- unit/compile tests: PASS;
- governance assertions: PASS;
- derived evidence artifact uploaded successfully;
- raw vendor payloads were not committed;
- production database write: false;
- model result persisted to Neon: false;
- direction vote: false;
- Forecast/Decision writes: false;
- production authority-store counts remained 0/0/0/0.

Artifact ID: `9973539516`
Artifact ZIP SHA256: `e6eaf9c2f5e80ad5b82fa909a8695940e6819bc342365ce617a916db1f7c4b4f`

## Interpretation and stop point

This validation supports the narrow claim that preregistered V2 strong macro shocks showed statistically non-random directional consistency with immediate gold reaction in the frozen VAL+LOCK sample and 15-minute window.

It does **not** establish H=1 monthly forecast skill, trading profitability, automatic BUY/SELL authority, selector/ensemble eligibility, or position mapping.

`MACRO_EVENT_SUCCESSOR_V2` is therefore eligible to enter a **separate promotion change-control**. No production/runtime promotion is performed by this result document.
