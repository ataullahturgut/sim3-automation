# GOLD CONTROL — VW_MIDAS_MSVR_SUCCESSOR_V1 FOUR-METAL PROSPECTIVE SOURCE REFRESH CONTRACT

Frozen: 2026-09-06, before the first genuinely prospective origin.
Model: `VW_MIDAS_MSVR_SUCCESSOR_V1`
Scope: prospective shadow research input only.

## 1. Source identity

Repository: `lbruton/StakTrakr`
Default branch observed at freeze: `main`
Annual payload path: `data/spot-history-2026.json`
Required metals: exactly `Gold`, `Silver`, `Platinum`, `Palladium`.

Historical R1 rows remain pinned historical reconstruction and are never mutated or silently extended.

New prospective snapshot identity:
`STAKTRAKR_FOUR_METAL_PROSPECTIVE_GIT_SNAPSHOT_V1`

The current upstream `main` commit observed on 2026-09-06 is `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`; its release evidence states spot-bundle coverage only through 2026-08-19. It is current-state evidence only and is not preselected as the 30-Sep issuance snapshot.

## 2. Snapshot rule at prospective issuance

At each prospective issuance/readiness attempt:
1. resolve the latest Git commit affecting `data/spot-history-2026.json` that is actually visible at retrieval time;
2. pin that exact commit SHA before parsing model inputs;
3. fetch the annual payload from that pinned commit, never from an unpinned moving branch for model execution;
4. record actual retrieval timestamp, commit timestamp, commit SHA, and payload SHA-256;
5. parse only the `metal`, `timestamp`, `spot`, and provenance/provider fields required by the historical V1 source semantics;
6. filter forecast features to observations dated no later than the frozen origin;
7. ignore all target-month rows even if the retrieved annual file already contains them;
8. never backdate retrieval or availability timestamps.

No production Neon persistence is required for this prospective snapshot. The exact pinned source artifact itself is the research evidence source.

## 3. Historical-lineage continuity gate

Because historical V1 used the pinned StakTrakr R1 reconstruction through 2026-07-31, the prospective snapshot must prove that it has not silently redefined the source history.

Before issuance:
- compare every common July 2026 date/metal available in both the frozen R1 panel and the new pinned prospective snapshot;
- require the same four metal identities and same row semantics;
- any conflicting same-date value or material historical revision fails closed;
- no revised July value may be silently accepted merely to make the new snapshot executable.

Failure status:
`BLOCKED_STAKTRAKR_PROSPECTIVE_HISTORY_REVISION_OR_SEMANTIC_DRIFT`.

A separately preregistered bridge would be required to override this failure; post-result acceptance is forbidden.

## 4. August + September completeness gates for first prospective test

The October 2026 feature vector requires:
- `MR_m(2026-09) = log(M_m(2026-09) / M_m(2026-08))`;
- within-September weighted daily returns.

Therefore both months are required. The old R1 endpoint at 2026-07-31 is not enough.

Before a 2026-09-30 information-set forecast may be issued:
- all four required metals must be present;
- use only dates where all four metals are simultaneously present;
- August 2026 must contain at least 20 common complete four-metal dates;
- September 2026 must contain at least 20 common complete four-metal dates;
- latest common September date must be >= 2026-09-27;
- observations after 2026-09-30 are excluded from issuance features even if present in the retrieved snapshot;
- no missing-metal imputation;
- no interpolation;
- no provider substitution;
- no mixing another metal source into one leg of the four-output panel.

If source semantics/continuity pass but month coverage is incomplete:
`WAITING_FOUR_METAL_SOURCE_DATA`.

## 5. Source payload discipline

For duplicate rows within the exact pinned payload:
- an exact same-date/same-metal duplicate with the same value may be deterministically de-duplicated;
- conflicting values for the same metal/date fail closed;
- provider labels are retained as provenance and must not be used to silently choose a preferred value after seeing outcomes.

The payload does not formally encode a unit contract, so this prospective contract does not invent a unit claim that was absent from the historical StakTrakr research source.

## 6. Persistence / authority rule

This prospective snapshot is consumed directly as a research artifact.

It does NOT authorize:
- production Neon source writes;
- extension of the historical `*_STAKTRAKR_RESEARCH_DAILY_R1` identities;
- production forecast writes;
- decision writes;
- runtime mutation.

Any future production persistence requires a separate manifest/change-control authorization and separately named lineage.

## 7. Governance locks

- model mathematics unchanged;
- frozen V1 features/grid/nested selection unchanged;
- `AUTO_SELECTOR=OFF`;
- `AUTO_ENSEMBLE=OFF`;
- no backdated issuance;
- no target-month information in issuance;
- exact snapshot identity must be frozen in prospective forecast evidence.
