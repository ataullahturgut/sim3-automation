# VW_MIDAS_MSVR_SUCCESSOR_V1 — PROSPECTIVE DESIGN NOTE

Date: 2026-09-06
Status: PRE-REGISTRATION SOURCE REVIEW

This note records source facts found before the prospective contract is frozen.

- A 2026-08-31 -> 2026-09 forecast cannot be labelled prospective when created on 2026-09-06. Any such output is reconstruction only.
- The first genuinely prospective monthly origin that can be preregistered now is 2026-09-30 for target 2026-10.
- Production Neon StakTrakr R1 four-metal rows currently end 2026-07-31.
- Current upstream StakTrakr 2026 file was observed to extend beyond the pinned R1 snapshot, but R1 is commit-pinned; future rows must not be appended under the old pinned lineage without a separately frozen source-refresh identity/contract.
- `CORE5_GOLD_USD_OZ_RESEARCH_R1` is a locked local snapshot from `IDMA_ALTIN_VERI_PANELI_V3_2026-07_TAM_CORE5.xlsx / Aylik_Panel`, ending 2026-07. It is not a proven automatically refreshable live target-anchor source.
- Production Neon does contain current XAU sources such as `XAU_EOD_TWELVE_NY17`, but using one of them in place of the frozen CORE5 monthly anchor would be a source/target-mapping change and is forbidden unless explicitly preregistered and validated.
- Manifest v1.37 authorizes the first Broad R1 persistence only under the frozen 71,075-row pre-write state; it does not silently authorize arbitrary future source refreshes.

Therefore the prospective contract must fail closed until both (a) the exact future four-metal source lineage and (b) an authorized current monthly XAU anchor/target-measurement contract are frozen before issuance.
