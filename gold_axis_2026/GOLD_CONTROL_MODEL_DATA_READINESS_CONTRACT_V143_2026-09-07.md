# GOLD CONTROL · MODEL DATA READINESS CONTRACT V1.43

Date: 2026-09-07
Scope: production data plane, point-in-time model inputs, live intramonth context freshness, and fail-closed operational readiness.

## 1. Purpose

`ACTIVE` means that a governed engine identity is present on the current production surface. It does **not** by itself prove that the engine has consumed the newest eligible source observation or that its displayed state is live-fresh.

V1.43 therefore separates four concepts:

1. `CURRENT_SURFACE_REGISTERED` — the governed engine/feature inventory is present.
2. `MONTHLY_REFERENCE_VALID` — H=1 monthly references retain their frozen forecast origin and point-in-time information cutoff.
3. `INTRAMONTH_DATA_READY` — each live tactical/risk context has consumed all eligible source observations required by its frozen contract.
4. `PROSPECTIVE_MODEL_READY` — a model that claims prospective operation has an independently valid prospective input contract and persisted point-in-time input evidence.

No stale or missing input may be converted into a fresh/live label merely because a runtime row remains `ACTIVE`.

## 2. External authority basis

This contract adopts the following engineering principles as authority benchmarks, without asserting that banking supervisory rules legally apply to this project:

- Federal Reserve / OCC / FDIC, *Revised Guidance on Model Risk Management* (SR 26-2, 17 Apr 2026): model inventories, fit-for-purpose validation, ongoing monitoring, outcome analysis, vendor/third-party data understanding, and documentation of limitations.
- NIST AI 800-4 (Mar 2026), *Challenges to the monitoring of deployed AI systems*: post-deployment monitoring is needed because real-world inputs and operating conditions change after pre-deployment evaluation.
- Hyndman & Athanasopoulos, *Forecasting: Principles and Practice*, time-series cross-validation: each forecast origin may use only observations available before that origin; rolling-origin evaluation prevents future leakage.
- CME Group EBS regular trading hours: Spot FX & Precious Metals use a 17:00 ET trade-date roll. This supports Gold Control's internal NY17 session boundary but does not make a Twelve Data price an official CME settlement.
- Twelve Data API documentation: intraday bar `datetime` denotes the opening time and the timezone parameter accepts IANA zones for intraday intervals. Therefore Gold Control's `16:59 America/New_York` 1-minute bar close is an internal end-of-minute 17:00 ET decision reference, not an official close/settlement claim.

## 3. Source-to-model binding

| Component | Governed source/input | Timing rule | Freshness / PIT gate |
|---|---|---|---|
| `MONTHLY_DIRECTION_3M` | `XAU_EOD_TWELVE_NY17` | completed prior months only | frozen at month origin; must not be refreshed with target-month observations |
| `FAST` | `XAU_EOD_TWELVE_NY17` | completed NY17 trade-date observations | latest feature input must not predate the latest eligible canonical XAU availability |
| `SLOW` | `XAU_EOD_TWELVE_NY17` | completed weekly states built only from completed NY17 observations | same source-freshness gate as FAST; incomplete week must not be treated as completed week |
| `GVZ_RISK` | `GVZ_CBOE` | released/available observation only | latest GVZ-derived context must not predate the latest eligible `GVZ_CBOE` availability |
| `EMERGENCY_LEVEL` / `EMERGENCY_REVERSAL` | accepted target-month XAU + an explicitly permitted monthly reference | intramonth | a month-open `NO_*OBSERVATION` placeholder becomes stale once an eligible target-month XAU observation exists; no live Emergency reference may be fabricated from an ineligible replay expert |
| `RANDOM_WALK` | `SIMPLE_EXPERT_XAU_TWELVE_NY17_HOURLY_MONTHLY_MEAN_V2` | H=1, prior completed month | source-bound R2 input set, origin-bounded; no target-month refresh |
| `MOMENTUM_3M` | same source-bound R2 monthly-mean series | H=1, prior completed months | source-bound R2 input set, origin-bounded; no target-month refresh |
| `CAUSAL_PATCH` | frozen Patch contract inputs | H=1 | historical replay and prospective issuance are distinct evidence classes |
| `VW_MIDAS_MSVR_SUCCESSOR_V1` | four-metal + GPR PIT contract | H=1 | historical replay success does not imply prospective readiness; prospective four-metal, GPR-vintage and target-anchor gates must pass separately |
| `BOCPD_RETURN_SUCCESSOR_V1` | frozen return/regime input contract | regime/break context | source and cutoff lineage must remain explicit; not a direction generator |
| `MACRO_EVENT_SUCCESSOR_V2` | release-aware macro/event inputs | event-risk context | release timestamp / vintage safety; revised macro values cannot be backdated into prior origins |

## 4. Canonical XAU ingestion contract

`XAU_EOD_TWELVE_NY17` remains the canonical daily tactical XAU reference.

Required invariants:

- provider: Twelve Data;
- symbol: `XAU/USD`;
- interval used for the reference: `1min`;
- requested timezone: `America/New_York`;
- accepted source bar: unique exact `16:59:00` bar for the trade date;
- stored timestamp: the corresponding `17:00 ET` boundary converted to UTC;
- accepted value: source bar `close` after positive OHLC/range validation;
- fallback: none;
- interpolation: forbidden;
- forward fill: forbidden;
- silent substitution: forbidden;
- official-settlement claim: forbidden.

### Gap resilience

The production collector must reconcile a bounded recent window rather than persisting only the single latest bar. A prior missed trade date must therefore be recoverable on a later successful run if Twelve Data subsequently provides the exact validated 16:59 bar.

A missing date is not automatically an error solely because it is a weekday; holidays and provider session availability must be respected. However, when an accepted independent daily XAU crosscheck has a later trade date than the canonical NY17 series, the current tactical data plane is `NOT_READY` until the canonical series catches up or the discrepancy is explicitly adjudicated.

## 5. Release-lag and vintage rules

Wall-clock recency is not a universal freshness rule.

- Market/session series: freshness is evaluated against completed eligible sessions.
- Scheduled macro series: freshness is evaluated against the provider's release calendar / availability timestamp, not against observation date alone.
- Revision-prone macro series: prior-origin replay must use a vintage that was available at that origin where a vintage source exists (for example ALFRED/FRED real-time periods); current revised values must not be injected backward.
- Monthly GPR inputs: the model's frozen publication-lag/vintage rule remains binding.

## 6. Required lineage for model consumption

Every model or derived feature that is promoted as current/fresh must be traceable, directly or through an immutable input set, to at least:

- `series_id` / semantic identity;
- source/provider identity and symbol when applicable;
- observation timestamp;
- `available_as_of` and `retrieved_at`;
- quality status;
- lineage ID or immutable snapshot/input-set member IDs;
- input fingerprint;
- model/feature version and Git commit;
- forecast origin / target context where applicable.

If a component cannot prove those fields, its output may remain historical/display evidence but must not be labelled live-fresh.

## 7. Fail-closed readiness rules

The read-only V1.43 readiness audit must fail when any of the following is true:

- canonical NY17 XAU is behind an accepted later XAU daily crosscheck;
- FAST/SLOW were computed before the latest eligible canonical XAU became available;
- FAST/SLOW lineage is not bound to `XAU_EOD_TWELVE_NY17`;
- GVZ context predates the latest eligible `GVZ_CBOE` availability;
- Emergency still claims `NO_SEPTEMBER_EOD_OBSERVATION` (or equivalent month-open no-observation state) after an accepted target-month XAU observation exists;
- H=1 monthly references use information after their frozen origin;
- RW/Momentum current H=1 identities are not the source-bound R2 versions;
- an historical replay is relabelled prospective;
- selector/ensemble/canonical authority is silently enabled.

Failing this audit does not delete history and does not mutate forecasts. It means only that the live current-data path is not ready.

## 8. September 2026 interpretation

September H=1 references are frozen to the 31 Aug 2026 origin/information boundary and must **not** be recomputed from September observations. Their replay evidence class remains unchanged.

Intramonth FAST/SLOW/GVZ/Emergency contexts are different: they are expected to evolve as their own eligible observations arrive. A stale intramonth context must therefore be exposed as stale rather than being inferred fresh from a 12/12 `ACTIVE` inventory count.

## 9. Production-write boundary

The V1.43 readiness auditor is read-only. It may block/flag readiness but may not write forecast, decision, selector, ensemble, or authority state.

A live intramonth feature writer is a separate governed change. Until its persistence, replay equivalence, idempotency, lineage, and fail-closed tests pass, the scheduler must not create new decision/authority rows merely to make the surface look current.
