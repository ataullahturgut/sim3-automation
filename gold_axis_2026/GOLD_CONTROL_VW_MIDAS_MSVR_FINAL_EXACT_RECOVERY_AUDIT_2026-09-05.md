# GOLD CONTROL — VW_MIDAS_MSVR FINAL EXACT-RECOVERY AUDIT

Date: 2026-09-05

## Question

Can the historical `VW_MIDAS_MSVR` identity now be recovered exactly enough to remove its current blocker and run it under its original identity?

## Repository evidence inspected

The historical recovery tree contains VW reconstruction/research implementations including:

- `gold_axis_2026/run_vw_direct_h1_h5.py`
- `gold_axis_2026/run_vw_direct_h1_h5_fast.py`
- `gold_axis_2026/run_vw_full_rebuild.py`
- `gold_axis_2026/run_vw_full_rebuild_v2.py`

The important point is that these files are rebuild/research implementations, not recovered proof of the original executable identity.

### `run_vw_full_rebuild.py`

The file itself marks exact replication as `BLOCKED` and records unresolved identity/definition problems, including:

- authors' processed dataset is not public;
- paper identifier `GPY` remains ambiguous and is not guessed;
- exact definitions of `long_term_trend` and generic `volatility` are not stated in the accessible paper text;
- `g_volatility` exact mapping is not explicitly stated, with `^GVZ` used only as a labeled proxy in an extension;
- reconstruction uses substitute public mappings rather than a proven original provider/PIT identity.

### `run_vw_full_rebuild_v2.py`

The second rebuild also states `exact_replication = BLOCKED` and preserves unresolved items. It additionally states that revision-safe/PIT status is `NOT_PROVEN` when current official history is used with publication lag and that the Barrick exchange/ticker is not explicit in the accessible paper text, requiring a labeled proxy.

These are not cosmetic gaps. They affect feature identity, source identity, point-in-time availability, and therefore model identity.

## Successor evidence

A separately named successor lane was already built and tested. `VW_MIDAS_SVR_XAU_SUCCESSOR_V2` was terminally rejected under its frozen validation contract. That rejected successor cannot be renamed to the archived `VW_MIDAS_MSVR` identity and cannot repair the missing original contract.

## Final recovery decision

`FINAL_EXACT_RECOVERY_NOT_PROVEN`

The archived current motor remains:

`VW_MIDAS_MSVR`

with blocker:

`BLOCKED_EXACT_REPLICATION_AND_PIT_SOURCE_CONTRACT_NOT_PROVEN`

No original-model parameters, ambiguous series identities, feature definitions, provider identities or vintages may be guessed merely to make the engine executable.

## Operational consequence

- no production forecast is issued by `VW_MIDAS_MSVR`;
- no direction vote is permitted;
- no selector/ensemble role is granted;
- no Decision Store or Forecast Store write is authorized;
- no rejected successor is promoted or relabeled;
- the 31-August month-open snapshot remains valid without a VW value.

## Closure

Unless new primary evidence is later recovered that resolves the missing original feature/source/PIT identities, further exact-recovery work on this archived identity is closed.

`PASS_FINAL_VW_EXACT_RECOVERY_AUDIT_BLOCKED_WITHOUT_GUESSING`
