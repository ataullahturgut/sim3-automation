# GOLD H3 REACTION DECAY CONFIRMATION V1

**Date:** 2026-10-04
**Window:** 2025-07-01 .. 2025-09-30
**Status:** frozen confirmation test

## Frozen rule

Reaction decay is TRUE when:
- Gold's first ~2-hour post-release move has a non-zero sign;
- Gold's move from the end of that first-reaction window to 16:00 ET has the opposite sign;
- the total move from pre-release to 16:00 ET still has the original first-reaction sign.

No magnitude threshold is used.

## Event families

Only the same scheduled families used in the June discovery sample:
- JOLTS
- ADP
- NFP
- CPI
- PCE
- FOMC

The July 30 ADP and FOMC are treated as separate events because their release times differ.

## Confirmation targets

Primary:
- H3 reversal rate among reaction-decay events
- H3 reversal rate among non-decay events

Secondary:
- V5 missed reversals among decay events
- precision of decay as a reversal flag
- rescue/broken/net if decay were used as an incremental FLIP on V5-follows-momentum origins

No threshold or event-family exclusion may be introduced after results are opened.

## Clock

Use the frozen VAST hourly GC=F panel.
- pre-release proxy: last hourly observation at least 1 hour before scheduled release
- first-reaction proxy: last hourly observation by release + 2h
- event-day close proxy: last hourly observation by 16:00 ET

These are retrospective mechanism proxies, not exchange-authority timestamps.
