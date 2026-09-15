# GOLD CONTROL — MACRO EVENT SUCCESSOR V4 RELIABILITY GATE PREREGISTRATION

**Date:** 2026-09-15  
**Identity:** `MACRO_EVENT_SUCCESSOR_V4_RELIABILITY_GATE`  
**Status:** `RESEARCH_CHALLENGER / PREREGISTRATION / NOT_RUNTIME_AUTHORITY`  
**Parent research lane:** `MACRO_EVENT_SUCCESSOR_V3` score families  
**Governed runtime identity remains:** `MACRO_EVENT_SUCCESSOR_V2`  
**Canonical project authority:** `gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md`

## 1. Purpose

V4 is a selective event-direction challenger. It does **not** relax the parent strong-event threshold and it does **not** replace the governed runtime Macro Event identity.

The research hypothesis is:

> Macro-event direction evidence should be issued only by event families that have demonstrated sufficiently stable historical gold-direction alignment; weaker families remain context-only rather than being forced into a directional vote.

The intended benefit is lower false-direction risk through explicit abstention, not higher signal frequency.

## 2. Governance boundary

V4 is research-only and has:

- no production/runtime promotion;
- no Forecast Store or Decision Store write authority;
- no BUY/SELL/HOLD/position mapping;
- no automatic selector/ensemble authority;
- no right to change `GOLD_CONTROL_PROJECT_MANIFEST.md`;
- no right to alter `MACRO_EVENT_SUCCESSOR_V2`;
- no right to rewrite V2/V3 historical evidence.

The current governed runtime inventory remains unchanged.

## 3. Evidence classification and freeze boundary

All results dated before this preregistration are `HISTORICAL_REPLAY` / researcher-visible evidence and must not be relabelled as fresh OOS evidence.

The 2025 retrospective challenge has already been inspected and therefore may not be used as untouched challenge evidence for V4.

The 2026-01-01..2026-08-31 period is a retrospective stress/transport check, not fresh blind OOS.

**Prospective Shadow T0** begins only after this preregistration is merged to the canonical `gold-r4-direction-engine` branch. The canonical merge commit timestamp is the authoritative T0.

No event whose release timestamp is earlier than T0 may count as prospective V4 evidence.

## 4. Parent score inputs

V4 consumes existing V3 research score states only:

- `MACRO_EVENT_V3_EMPLOYMENT_SCORE`
- `MACRO_EVENT_V3_FOMC_SCORE`
- `MACRO_EVENT_V3_INFLATION_SCORE`

V4 does not recompute or modify the underlying surprise models.

A parent event is `STRONG` only when the stored V3 state is exactly one of:

- `GOLD_ADVERSE_MACRO_SHOCK`
- `GOLD_SUPPORTIVE_MACRO_SHOCK`

`MACRO_MIXED_OR_SMALL` remains non-directional.

No post-freeze threshold search, percentile substitution, score rescaling, sign flipping or component reweighting is permitted under V4.

## 5. Frozen family reliability gate

The family roles are frozen as follows:

| Family | V4 role |
|---|---|
| `EMPLOYMENT` | `DIRECTIONAL` |
| `FOMC` | `DIRECTIONAL` |
| `INFLATION` | `CONTEXT_ONLY` |

Therefore:

- strong Employment event -> issue the parent V3 direction as V4 directional research evidence;
- strong FOMC event -> issue the parent V3 direction as V4 directional research evidence;
- strong Inflation event -> retain event severity/context, but **abstain from a direction vote**;
- mixed/small event -> `NO_SIGNAL`.

These roles may not be promoted/demoted within V4 after T0. Any change requires a separately named successor, e.g. V5, preregistered before its prospective outcomes are inspected.

## 6. Historical rationale for the frozen gate

This is method-development evidence, not blind validation.

The historical 5-minute corroboration set previously available in Neon contained 34 strong V3 events with 26 directional hits (76.47%). Family decomposition was:

- Employment: 7/8 = 87.50%;
- FOMC: 8/9 = 88.89%;
- Inflation: 11/17 = 64.71%.

A pre-2024 family diagnostic used in the V4 design produced:

- Employment: 6/7 hits; Beta(1,1)-posterior `P(p>0.5)=0.96484375`;
- FOMC: 5/6 hits; posterior `P(p>0.5)=0.9375`;
- Inflation: 8/13 hits; posterior `P(p>0.5)=0.78802490234375`.

The design threshold used for family authorization was `P(p>0.5) >= 0.90` together with positive median signed R15. This historical design choice is now frozen; it is not to be recalibrated inside V4.

Researcher-visible post-development replay:
- 2024-2025: V4 issued 4 directional events and all 4 aligned with R15; 4 of 8 parent strong events were abstained/context-only.
- 2026-01..08 stress check: V4 issued 2 directional events and both aligned with R15; one Inflation strong event remained context-only.
- Combined researcher-visible 2024..2026-08: 6/6 directional hits.

These figures are supportive historical evidence only and are **not** eligible to be labelled prospective OOS.

## 7. Prospective reaction contract

For a prospective strong event at release timestamp `t`:

Primary market source:
- Twelve Data `XAU/USD` research intraday lane already governed by the project;
- 1-minute bar timestamps are treated as bar-open timestamps.

Primary reaction:
- `P0` = close of the 1-minute bar with timestamp `t - 1 minute`;
- `P15` = close of the 1-minute bar with timestamp `t + 14 minutes`;
- `R15 = 100 * (P15 / P0 - 1)`.

Expected direction:
- `GOLD_ADVERSE_MACRO_SHOCK` -> `R15 < 0`;
- `GOLD_SUPPORTIVE_MACRO_SHOCK` -> `R15 > 0`.

Signed reaction:
- adverse -> `signed_R15 = -R15`;
- supportive -> `signed_R15 = +R15`.

Directional hit iff `signed_R15 > 0`. Exactly zero is a miss.

Inflation `CONTEXT_ONLY` events may have R15 recorded descriptively but may not enter the V4 directional hit/miss denominator.

No silent provider substitution is allowed.

## 8. Prospective eligibility gates

A row may enter the prospective V4 denominator only if all are true:

1. event timestamp is at or after canonical merge T0;
2. parent V3 row is itself legitimately issued as `PROSPECTIVE_SHADOW` before outcome inspection;
3. macro source/consensus availability is point-in-time valid for the event;
4. parent state is a frozen strong state;
5. family role is `DIRECTIONAL`;
6. exact required `P0` and `P15` bars exist and are unique;
7. both prices are finite and positive.

Otherwise the event is reported as `NOT_TESTABLE`, `PENDING_REACTION`, `BLOCKED_SOURCE`, `CONTEXT_ONLY` or `NO_SIGNAL` as appropriate and is excluded from the directional denominator.

## 9. Frozen prospective evaluation

No automatic promotion is permitted.

A formal V4 prospective evaluation may be opened only after at least **8 eligible directional prospective events** have matured.

The primary statistical evidence is:

- one-sided exact Binomial(0.5) sign-test on directional hits, requiring `p <= 0.10`;
- median `signed_R15 > 0`.

The report must also disclose:

- eligible directional event count;
- hit count and hit rate;
- family counts;
- Inflation context-only count;
- abstention rate among all parent strong events;
- missing-bar/source-blocked events;
- median signed R15;
- exact p-value.

Accuracy may not be reported without coverage/abstention.

Passing the prospective evidence gate means only `ELIGIBLE_FOR_PROMOTION_CHANGE_CONTROL`; it does not itself change runtime inventory.

## 10. Source and lineage locks

V4 must preserve source identity and lineage from its parent V3 rows.

Historical consensus rows whose exact provider update timestamp remains unproven must retain that limitation. Historical reconstruction cannot be relabelled prospective.

For new prospective events, consensus must be captured before release under the governed source process. If pre-release consensus capture cannot be proven, the event is `BLOCKED_SOURCE` for prospective V4 evaluation.

## 11. Prohibited changes inside V4

The following require a new successor identity:

- changing the ±1-like parent strong-state rule or any V3 family score formula;
- making Inflation directional;
- removing Employment or FOMC from the directional set;
- changing R15 to another primary horizon;
- changing source/provider;
- adding market-confirmation filters;
- adding GVZ/VIX/rate/dollar conditioning;
- learning new family weights from post-T0 outcomes;
- changing the minimum prospective sample;
- changing the statistical gate after observing prospective results.

## 12. Literature basis

The design is consistent with the event-study literature rather than derived from 2025 threshold fitting:

- Christie-David, Chaudhry & Koch (2000), *Journal of Economics and Business*: intraday gold/silver responses differ across macro announcement types; gold responds materially to CPI and unemployment-related releases.
- Elder, Miao & Ramchander (2012), *Journal of Banking & Finance*: intraday metal-futures responses to U.S. macro surprises are swift; 08:30 announcements, especially nonfarm payrolls, are particularly influential; unexpectedly stronger economic news tends to be negative for gold.
- Gürkaynak, Sack & Swanson (2004/2005), Federal Reserve FEDS: FOMC asset-price effects require at least target and future-policy-path factors rather than a single policy surprise.
- Goldberg & Grisse (2013), Federal Reserve Bank of New York Staff Report 626: asset-price responses to macro announcements vary over time with economic and risk conditions.

These sources motivate family-specific treatment and explicit abstention when directional reliability is not sufficiently stable.

## 13. Current research decision

`MACRO_EVENT_SUCCESSOR_V4_RELIABILITY_GATE = FROZEN_RESEARCH_CHALLENGER_PENDING_CANONICAL_MERGE`

Until canonical merge:
- prospective T0 has not started;
- no result may be labelled V4 prospective evidence.

After canonical merge:
- V4 prospective shadow may begin under this exact contract;
- runtime inventory remains unchanged until separate promotion change control.
