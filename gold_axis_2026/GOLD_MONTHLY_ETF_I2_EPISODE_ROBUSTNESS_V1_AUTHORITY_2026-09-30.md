# GOLD MONTHLY — ETF I2 Episode Robustness V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED ROBUSTNESS / REQUIRED BEFORE PROMOTION
**Scope:** de-cluster I2 historical recurrence. No routing/model switching.

## Motivation

The I2 historical recurrence test counts every month that remains inside a simultaneous GLD+IAU redemption streak. Long streaks create serially dependent repeated event months.

To avoid pseudo-replication, evaluate **episode entries** only.

## Frozen I2 episode-entry definition

I2 base state remains unchanged:
- GLD and IAU both contract for at least 2 consecutive months.

An **I2_EPISODE_ENTRY** occurs only when:
- current month I2 = TRUE; and
- prior month I2 = FALSE.

Therefore a multi-month redemption run contributes one event, at the first month the 2-month persistence threshold is reached.

No threshold is changed.

## Outcome

Same pre-registered next-month GLD absolute-log-return outcomes:
- MOVE_3 >= 3pp
- MOVE_5 >= 5pp
- MOVE_8 >= 8pp

Report mean/median next-month absolute move, event rates, Fisher one-sided enrichment versus non-entry months, and deterministic bootstrap mean-uplift CI.

Primary historical block:
- 2010-01..2020-12

Secondary descriptive blocks:
- 2021-01..2024-12
- 2025-01..2026-08

No combination with I1 is tested.
