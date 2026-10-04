# GOLD H3 — JUNE 2025 MACRO REPRICING WINDOW V1B

**Date:** 2026-10-04  
**Window:** 2025-06-01 .. 2025-06-30  
**Status:** exploratory mechanism finding from six scheduled macro/Fed events.

## Key correction

The original V1 definition of a "failed first reaction" required the Gold move to reverse sign completely before 16:00 ET. That was too strict and produced zero cases.

A more informative descriptive quantity is **reaction decay**:

> the first ~2-hour Gold move remains the same sign by 16:00 ET, but the move partially retraces after the first-reaction window.

Formally:
- first reaction > 0 and post-first return < 0, or
- first reaction < 0 and post-first return > 0.

No threshold is used.

## Six-event result

| Date | Event | First ~2h | Post-first to 16ET | H3 reversal? |
|---|---|---:|---:|---|
| 2025-06-03 | JOLTS | +0.06% | +0.14% | No |
| 2025-06-04 | ADP | +0.92% | **-0.12%** | **Yes** |
| 2025-06-06 | NFP | -0.98% | -0.53% | No |
| 2025-06-11 | CPI | +0.15% | +0.51% | No |
| 2025-06-18 | FOMC | -0.50% | 0.00% | No |
| 2025-06-27 | Core PCE | -0.26% | **+0.05%** | **Yes** |

Thus:
- reaction decay events: **2**
- H3 reversal among decay events: **2/2**
- no-decay events: **4**
- H3 reversal among no-decay events: **0/4**

Both reversals were also V5 missed reversals.

## Interpretation

This is a much more specific mechanism than "macro surprise causes reversal."

The sequence is:

1. macro release creates a directionally coherent rates/Gold reaction;
2. Gold initially moves strongly in that repricing direction;
3. before the H3 origin, that impulse begins to lose strength / partially retrace;
4. the following H3 then reverses the event-day momentum.

Examples:

- **Jun-04 ADP:** very weak labor surprise, 2Y -9 bp, Gold +0.92% first reaction; by 16ET part of the move had already been given back; subsequent H3 reversed DOWN.
- **Jun-27 Core PCE:** hotter core inflation, 2Y +3 bp, Gold -0.26% first reaction; part of the decline was recovered by 16ET; subsequent H3 reversed UP.

By contrast:
- Jun-06 NFP: hawkish surprise, 2Y +12 bp, Gold decline intensified after the first reaction -> continuation.
- Jun-11 CPI: dovish surprise, 2Y -7 bp, Gold rise intensified after the first reaction -> continuation.

## Scientific status

This is **not yet a validated rule**:
- only six events;
- the decay concept was identified after inspecting this sample.

It is nevertheless a high-value candidate because it directly distinguishes both reversal events from all four continuation events in the chosen window without using the future H3 path in the feature itself.

The next valid test should freeze this qualitative rule and evaluate it on a non-overlapping later event window before any threshold tuning.
