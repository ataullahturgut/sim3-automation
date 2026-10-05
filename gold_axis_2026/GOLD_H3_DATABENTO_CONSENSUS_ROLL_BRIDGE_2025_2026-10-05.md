# GOLD H3 — Databento Consensus Roll Bridge (2025) — 2026-10-05

**Status:** **CONSENSUS_SOURCE_BRIDGE_REQUIRES_REVIEW**  
Estimated Databento cost: **USD 1.5681**.

Rule: choose the instrument_id supported by at least 2 of calendar/open-interest/volume continuous aliases; when all three differ, use a root-specific priority learned only from Yahoo price identity.

## Tie-break rules

| Root | Priority | Tie hours | c wins | n wins | v wins | Median price error bps | P95 bps |
|---|---|---:|---:|---:|---:|---:|---:|
| GC | v > n > c | 421 | 1 | 10 | 410 | 0.00018 | 0.67904 |
| SI | v > n > c | 645 | 2 | 14 | 629 | 0.00024 | 1.31925 |
| NQ | c > n > v | 0 | 0 | 0 | 0 | 0.00000 | 0.96819 |
| ZN | c > n > v | 0 | 0 | 0 | 0 | 0.00000 | 0.00000 |
| CL | c > n > v | 0 | 0 | 0 | 0 | 0.00023 | 108.47008 |

## Derived agreement

- IFBC score: corr=0.96319, MAE=0.0300523
- LLRS pressure: corr=0.92370, MAE=0.055279
- LLRS incremental: corr=0.91943, MAE=0.0547809
- leadlag_score_premax: corr=0.75171, MAE=0.143208
- internal_now: corr=0.99433, MAE=0.0133999
- internal_d1: corr=0.99275, MAE=0.0236959

## Decision invariance

- Handoff: 27 matched; Databento 33 vs Yahoo 30; Jaccard **75.0%**.
- Added: 2025-04-17, 2025-05-19, 2025-06-05, 2025-08-06, 2025-09-26, 2025-10-31
- Missing: 2025-05-29, 2025-08-11, 2025-08-13

| Variant | DB actions | Yahoo actions | Matched | Jaccard | DB R/B/net |
|---|---:|---:|---:|---:|---:|
| Q95 | 10 | 9 | 9 | 90.0% | 4/6/-2 |
| Q99 | 9 | 8 | 8 | 88.9% | 3/6/-3 |

## Governance

- Tie-break priorities are selected solely from source-price identity in 2025; DPTC correctness is not consulted.
- The same deterministic rule can therefore be applied unchanged to 2023–2024.
- Passing supports a source-bridged historical reconstruction, not byte-identical Yahoo lineage.
