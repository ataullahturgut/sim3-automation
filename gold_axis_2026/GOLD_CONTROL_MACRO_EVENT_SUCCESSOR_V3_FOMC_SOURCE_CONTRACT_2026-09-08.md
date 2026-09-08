# Gold Control — Macro Event Successor V3 FOMC Source Contract

Date: 2026-09-08
Engine: `MACRO_EVENT_SUCCESSOR_V3`
Family: `FOMC`
Status: **SOURCE CONTRACT / FAIL-CLOSED / RESEARCH CHALLENGER ONLY**

## 1. Scope

This contract implements only the already-preregistered V3 FOMC family:

- `target_surprise`
- `path_surprise`

No analyst-calendar consensus, EFFR-only proxy, textual sentiment model, Treasury-yield proxy, SOFR substitution, or other event family is introduced by this contract.

## 2. Required authority sources

### Official FOMC event clock and realized target

Authority: Federal Reserve Board official FOMC meeting calendar, statement and implementation note.

The statement release timestamp is the governed event time. For the September 15–16, 2026 meeting, the Federal Reserve calendar identifies the FOMC release at 2:00 p.m. ET on September 16 and the press conference at 2:30 p.m. ET. The press conference is not silently merged into the statement event.

### Market-implied expectation

Authority candidate: CME Group `FedWatch API`.

CME states that FedWatch probabilities are derived from 30-Day Fed Funds futures and that the REST API provides both real-time/intraday and end-of-day access, with history back to 2015.

V3 requires licensed/authenticated project access. No undocumented endpoint is guessed and no webpage scrape substitutes for the API.

## 3. Methodological basis

- Kuttner (2001), Journal of Monetary Economics, DOI `10.1016/S0304-3932(01)00055-1`: policy actions must be decomposed into anticipated and unanticipated components using Fed funds futures expectations.
- Gürkaynak, Sack & Swanson, Federal Reserve FEDS `Do Actions Speak Louder Than Words?`: one target-rate factor is insufficient; a second future-policy-path factor is needed, associated with FOMC communication.
- Gürkaynak (2005), Federal Reserve FEDS `Using Federal Funds Futures Contracts for Monetary Policy Analysis`: futures at different horizons can measure changes in expectations of policy after future FOMC meetings.

## 4. Required capture objects

For each governed FOMC statement event, V3 requires:

### Pre-release snapshot

Captured strictly before the official FOMC statement timestamp:

- provider = CME FedWatch API
- `captured_at`
- `official_release_at`
- current meeting probability distribution over target ranges
- at least one subsequent meeting probability distribution over target ranges
- provider response/payload fingerprint
- provider/request lineage

### Post-release diagnostic snapshot

Captured after the statement within the V3 primary 10-minute window:

- same provider and probability schema
- `captured_at`
- current and subsequent meeting probability distributions
- immutable response/payload fingerprint

The post-release snapshot is used only to measure the change in the expected future policy path. It does not change the Market Shock event clock.

### Realized target

From the official FOMC statement/implementation note:

- target range lower bound
- target range upper bound
- target midpoint
- official availability timestamp
- source fingerprint/lineage

## 5. Target surprise

The pre-release current-meeting probability distribution must first be converted to an expected target midpoint:

`E_pre_current = sum(probability_i * target_midpoint_i)`

After the official FOMC statement is released:

`target_surprise_bps = 100 * (realized_target_midpoint_pct - E_pre_current_pct)`

This is the V3 market-implied unexpected target component. It is not the raw announced rate change.

No strong-event threshold is authorized by this source contract. Threshold/normalization belongs to the V3 development contract and must be frozen before locked evaluation.

## 6. Path evidence and path-surprise boundary

The source layer must compute expected target midpoints for subsequent meetings from the CME probability distributions both immediately before and after the statement:

`E_pre_future[k] = sum(prob_pre[k,i] * target_midpoint_i)`

`E_post_future[k] = sum(prob_post[k,i] * target_midpoint_i)`

and expose the vector:

`future_path_shift_bps[k] = 100 * (E_post_future[k] - E_pre_future[k])`

This source contract deliberately does **not** collapse that vector into a single scalar `path_surprise` or choose factor weights. A scalar path-factor construction must be separately preregistered from development/literature before locked V3 results are inspected.

Therefore, until that scalar method is frozen:

`FOMC_PATH_STATE = BLOCKED_PATH_FACTOR_METHOD_NOT_FROZEN`

This prevents an arbitrary post-result weighting of future meetings.

## 7. Fail-closed states

- API credential/config absent -> `BLOCKED_CME_FEDWATCH_API_NOT_CONFIGURED`
- authenticated source inaccessible -> `BLOCKED_CME_FEDWATCH_API_ACCESS`
- current-meeting distribution missing -> `BLOCKED_CURRENT_MEETING_EXPECTATION_MISSING`
- subsequent-meeting distribution missing -> `BLOCKED_FUTURE_PATH_EXPECTATION_MISSING`
- pre-release capture not strictly before release -> `BLOCKED_PRE_RELEASE_PIT`
- post-release capture outside primary window -> `BLOCKED_POST_RELEASE_WINDOW`
- official realized target source absent -> `BLOCKED_OFFICIAL_TARGET_SOURCE`
- scalar path method not preregistered -> `BLOCKED_PATH_FACTOR_METHOD_NOT_FROZEN`

No fallback provider is permitted.

## 8. Governance

- no production database write
- no Market Shock threshold modification
- no raw Market Shock episode deletion
- no BUY/SELL or position mapping
- no V2 mutation
- no canonical merge/promotion
- no 2026 locked result inspection until source and method gates permit it
