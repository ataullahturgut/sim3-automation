# Gold Control — VW Successor V2 GPR PIT Source Identity Amendment

**Freeze date:** 2026-09-05  
**Parent:** `GOLD_CONTROL_VW_MIDAS_SVR_XAU_SUCCESSOR_V2_CHANGE_CONTROL_2026-09-05.md`  
**Timing:** frozen before any V2 model score.

## Binding clarification

Historical PIT reconstruction rows from the authors' official Git archive must **not** be written under the current/final-vintage operational series identity `GPR_OFFICIAL`.

The separate governed series identity is:

`GPR_OFFICIAL_GIT_PIT`

Reason:

- `GPR_OFFICIAL` is the current official workbook retrieval lane and intentionally uses a first-retrieval availability floor when historical publication timing is not proven;
- `GPR_OFFICIAL_GIT_PIT` is a historical replay/reconstruction lane whose exact vintage identity and earliest official Git archive-add timestamp are separately proven per origin;
- keeping them separate prevents `canonical_latest` or any current-data consumer from silently mixing a historical reconstructed vintage with the current/final-vintage operational lane;
- this follows the Gold Data rule that provider/source/availability semantics are part of series identity.

The V2 source window remains unchanged:

`2022-03` through `2026-08` = 54 exact monthly origin vintages.

All other V2 feature, model, grid, minimum-fit, validation, benchmark and promotion gates remain unchanged.

No model score has been observed or used to make this source-identity separation.
