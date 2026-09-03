# Gold Control — September 2026 Historical Replay and Current Context Contract

**Freeze date:** 2026-09-03  
**Parent manifest:** v1.27  
**Canonical branch after acceptance:** `gold-r4-direction-engine`  
**Contract marker:** `FROZEN_SEPTEMBER_2026_HISTORICAL_REPLAY_AND_CURRENT_CONTEXT_V1`

## 1. Problem and non-negotiable separation

Gold Control did not issue a governed prospective H=1 expert forecast for September 2026 at the required prior-month-end origin. The absence of that prospective record must not make the September screen appear empty, but it also must never be repaired by backdating a forecast.

The September display therefore contains three explicitly separate states:

1. **Official prospective H=1 status** — `NOT_ISSUED_MISSED_2026_08_31_ORIGIN`. This remains historical fact and is never rewritten.
2. **September Historical Replay** — a reconstruction executed after the origin using only information whose market/source period ended no later than the frozen 31-August information cutoff. It is evidence class `HISTORICAL_REPLAY`, never prospective evidence.
3. **Current September Context** — already-persisted Monthly Direction / FAST / SLOW / GVZ state as of the current governed context timestamp. This is intramonth context, not an H=1 expert forecast.

No row or UI label may merge or relabel these three states.

## 2. Frozen target and time semantics

- target month: `2026-09`;
- target variable: frozen H=1 target, September 2026 calendar-month average XAU/USD price;
- missed official forecast origin: prior completed month-end, 31-August-2026;
- historical replay information cutoff: `2026-08-31T21:00:00Z`, corresponding to the completed 17:00 ET precious-metals trade-date boundary used by the project;
- replay `as_of`: the actual execution timestamp after 31 August; it must not be forged to equal the historical origin;
- retrieval timestamps are the real archival retrieval timestamps and may therefore be after the information cutoff;
- `prospective_claim=false` is mandatory on every replay artifact.

The replay may use archival data retrieved after the origin only when the source observation/period itself is proven to end no later than the information cutoff. Retrieval after the origin must be explicitly marked `retrieved_post_origin=true`; it must never be represented as proof that Gold Control possessed the row at the historical origin.

## 3. Historical replay track

New normalized expert track:

`HISTORICAL_REPLAY`

Allowed evidence class for this track:

`HISTORICAL_REPLAY`

Binding invariants:

- `forecast_origin = information_cutoff`;
- `as_of = actual replay execution time`, therefore `as_of >= forecast_origin`;
- all replay input source periods/observations must end `<= forecast_origin`;
- no September 2026 market observation, realized September target value, later outcome, or future-period feature may enter an input fingerprint;
- replay expert rows remain `canonical_authority=false`;
- runtime `direction_vote_permitted=false`;
- selector status remains `NOT_PROVEN_EXPERT_SELECTION_RULE`;
- `AUTO_SELECTOR=OFF`;
- `AUTO_ENSEMBLE=OFF`;
- no write to `monthly_forecast_contracts`;
- no write to Decision Store;
- no action/position mapping.

Historical replay is excluded from every prospective/live scorecard and model-selection calculation.

## 4. Expert eligibility frozen before replay result

### Random Walk R2 — ELIGIBLE FOR REPLAY

Identity:

`RW_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`

Source:

`SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2`

For target September 2026:

`forecast_RW = L[2026-08]`

where `L[m]` is the frozen source-bound completed-calendar-month measurement.

### 3M Momentum R2 — ELIGIBLE FOR REPLAY

Identity:

`MOMENTUM_3M_R2_NY17_HOURLY_MONTHLY_MEAN_SOURCE_BOUND`

Required completed input months are exactly:

`2026-05, 2026-06, 2026-07, 2026-08`

Formula is unchanged from the already-frozen V2 source-binding contract:

`forecast_MOM = L[Aug] * (1 + mean(Jun/May-1, Jul/Jun-1, Aug/Jul-1))`

### Causal Patch — CONDITIONAL / FAIL-CLOSED

Patch may enter the September replay only if its exact 31-August information set can be reconstructed under the frozen V7 feature semantics without reading September data and without inventing historical macro vintages. Its October-first-issuer hard-coded September feature construction is not permission to shift dates by assumption.

If the exact replay input set cannot be proven before result inspection, status is:

`BLOCKED_REPLAY_INPUT_SET_NOT_REPRODUCIBLE_FOR_2026_08_31`

and no Patch replay value is persisted.

### VW-MIDAS-MSVR — BLOCKED

Status remains:

`BLOCKED_NOT_PROVEN_EXECUTABLE`

No historical analytical artifact may be relabelled as a September replay issuance.

## 5. Frozen Simple Expert replay source construction

For Random Walk and Momentum, replay inputs use the already-authorized V2 source semantic without modification:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval: `1h`;
- requested timezone: `America/New_York`;
- select only returned bars whose `datetime` ends in `16:00:00`;
- treat selected close as the end-of-16:00–17:00 ET hourly value;
- monthly level = arithmetic mean of positive finite selected closes within each completed calendar month;
- at least 15 unique selected trading dates per required month;
- duplicate selected dates = hard failure;
- no interpolation;
- no forward fill;
- no provider substitution;
- no September input;
- no result-dependent threshold changes.

Only counts, hashes, period boundaries and pass/fail metadata may be logged; raw source prices and replay forecast values are not printed to CI logs.

## 6. Database Evidence Spine binding

Every persisted replay expert must be represented by the complete normalized chain:

source retrieval lineage
→ immutable `forecast_input_snapshots`
→ `forecast_input_sets`
→ `forecast_input_set_members`
→ `monthly_expert_forecasts` with track/evidence `HISTORICAL_REPLAY`
→ `engine_execution_runs` with evidence `HISTORICAL_REPLAY`
→ exactly one `engine_execution_expert_outputs` link.

Replay-specific input validation must prove both:

1. real retrieval time `retrieved_at <= replay as_of`; and
2. source observation/period end `<= historical forecast_origin`.

For monthly aggregate snapshots the precise source-period start/end and selected observation count are stored in metadata. `source_period_end` must be no later than the historical information cutoff.

The existing append-only UPDATE/DELETE guards remain unchanged.

## 7. UI contract

The Tahmin page must visibly show, in this order:

### EYLÜL 2026 — RESMÎ H=1

`ÜRETİLMEDİ`  
`31 Ağustos 2026 prospective origin kaçırıldı; sonradan backdate edilmedi.`

### 31 AĞUSTOS BİLGİ KESİTİ — HISTORICAL REPLAY

For each eligible replay expert, show:

- expert label;
- replay forecast value in USD/oz;
- target `Eylül 2026`;
- information cutoff `31 Ağustos 2026 17:00 ET`;
- actual replay execution timestamp;
- explicit pill: `REPLAY · PROSPECTIVE DEĞİL`;
- optional display-only delta sign versus the August source anchor, only under Section 8.

Blocked experts remain visible with their exact replay blocker instead of a fabricated number.

### GÜNCEL EYLÜL CONTEXT

Show the persisted current values independently:

- Monthly Direction 3M;
- FAST;
- SLOW;
- GVZ value/regime.

Label: `GÜNCEL CONTEXT · RESMÎ H=1 DEĞİL`.

Also show:

`Sonraki resmî origin: 30 Eylül 2026 → hedef Ekim 2026`.

## 8. Display-only replay direction marker

Because the frozen Simple Expert outputs are price levels rather than governed gold-direction votes, any arrow shown beside a replay value is only a deterministic display comparison to the August source anchor:

- forecast > August anchor → `↑ ABOVE_AUG_ANCHOR`;
- forecast < August anchor → `↓ BELOW_AUG_ANCHOR`;
- exact equality → `→ EQUAL_AUG_ANCHOR`.

This marker is stored in provenance, is `direction_vote_permitted=false`, and must never feed Monthly Direction, selector, ensemble, Decision Store, or action mapping.

## 9. Production display snapshot coordination

The deployment display snapshot contract is extended only to carry display-safe historical replay rows after they exist in production. Snapshot fallback must preserve:

- track/evidence `HISTORICAL_REPLAY`;
- target/origin/as_of;
- expert/model identity;
- replay forecast value;
- input fingerprint;
- display-only anchor comparison marker;
- canonical/selector/ensemble locks.

It must not include raw replay input market observations.

The scheduled read-only snapshot refresh continues to mirror production display state after replay persistence.

## 10. Acceptance gates

Before any production replay write:

1. schema migration passes on a temporary Neon branch;
2. `HISTORICAL_REPLAY` is accepted only on the replay track and cannot become a governed canonical forecast;
3. replay input validation rejects any source period ending after 31-August-2026 21:00Z;
4. September source data are absent from all replay input sets;
5. required V2 source months are complete with >=15 unique dates and zero duplicates;
6. deterministic rerun gives identical replay values/fingerprints;
7. no raw source/replay price is logged;
8. selector/ensemble/position locks pass;
9. Patch is persisted only if its 31-August input-set reproducibility gate passes independently;
10. VW remains blocked;
11. official September prospective row remains absent;
12. canonical forecast and Decision Store row counts remain unchanged;
13. UI browser QA proves the separation among official H1, replay and current context;
14. DB-backed and snapshot-fallback screens show the same governed replay/context state.

No threshold, formula, source rule, eligibility rule or label may be changed after observing the replay result merely to obtain a preferred direction or value.
