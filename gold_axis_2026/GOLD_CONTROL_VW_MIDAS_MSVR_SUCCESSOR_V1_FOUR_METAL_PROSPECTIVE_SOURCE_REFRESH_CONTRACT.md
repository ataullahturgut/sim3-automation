# GOLD CONTROL — VW_MIDAS_MSVR_SUCCESSOR_V1 FOUR-METAL PROSPECTIVE SOURCE REFRESH CONTRACT

Frozen: 2026-09-06, before the first prospective origin.
Model: `VW_MIDAS_MSVR_SUCCESSOR_V1`
Scope: prospective shadow research input only.

## Source identity

Repository: `lbruton/StakTrakr`
Default branch observed at freeze: `main`
Annual payload path: `data/spot-history-2026.json`
Required metals: exactly `Gold`, `Silver`, `Platinum`, `Palladium`.

Historical R1 rows remain pinned historical reconstruction and are not mutated or silently extended.

New prospective identity:
`STAKTRAKR_FOUR_METAL_PROSPECTIVE_GIT_SNAPSHOT_V1`

## Snapshot rule at prospective issuance

At each prospective issuance attempt:
1. query the Git history for `data/spot-history-2026.json`;
2. choose the latest commit visible at retrieval time whose commit timestamp is not later than the actual retrieval/issuance time;
3. pin that exact commit SHA;
4. fetch the annual payload from that exact commit, never from an unpinned moving branch for model execution;
5. record retrieval timestamp, commit timestamp, commit SHA and payload SHA-256 in the research evidence;
6. filter the forecast information set to observations dated no later than the frozen forecast origin;
7. ignore any target-month rows that may already exist in the retrieved file;
8. do not backdate the retrieval time.

The currently observed file commit `429d8e612d504a964846ff6438dbdb28ace630c3` dated 2026-08-19 is current-state evidence only; it is NOT preselected as the September issuance snapshot. The actual issuance snapshot must be the exact commit observed and pinned at issuance.

## September 2026 completeness gate for the first prospective test

Before a 2026-09-30 information-set forecast may be issued:
- all four required metals must be present;
- use only dates where all four metals are simultaneously present;
- at least 20 common complete four-metal dates must exist in September 2026;
- latest common date must be >= 2026-09-27;
- no missing-metal imputation;
- no interpolation;
- no provider substitution;
- no mixing another metal source into the panel;
- observations after 2026-09-30 are excluded even if present in the snapshot.

If any gate fails: `WAITING_FOUR_METAL_SOURCE_DATA`.

## Persistence rule

This prospective snapshot is consumed directly as a research artifact. It does NOT authorize production Neon persistence and does not extend manifest v1.37 Broad R1 write authority.

Any future persistence into production Neon requires a separate manifest/change-control authorization and a separately named lineage.

## Governance

- model mathematics unchanged;
- no selector/ensemble activation;
- no forecast/decision production writes;
- no runtime mutation;
- no silent lineage reuse;
- exact snapshot identity must be preserved in the prospective forecast evidence.
