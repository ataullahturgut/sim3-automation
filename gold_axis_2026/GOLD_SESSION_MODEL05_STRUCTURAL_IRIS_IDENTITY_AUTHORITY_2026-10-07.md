# SESSION MODEL-05 — STRUCTURAL_IRIS / A1_PLUS_PATH — IDENTITY AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / CANONICAL BASELINE IDENTITY ACCEPTED

## Canonical identity

SESSION Model-05 is the governed S1.4 canonical Structural-IRIS model:

**fresh NOVA A1 structural signal + 1h XAU PATH**

Canonical id:
`S14_A1_PLUS_1H_FULL`

This identity is distinct from:
- A1_DIRECT_MATCHED — structural-only comparator;
- S14_A1_PLUS_15M_FULL — 15m path challenger;
- S14_A1_PLUS_15M_SELECT — 15m selected challenger;
- S14_A1_PLUS_15M_SELECT_BAL — balanced 15m selected challenger.

## Governance / chronology

- 2022: governed training / warm-up only
- 2023–2024: scored development
- 2025: one-time frozen transport
- 2026: unopened

The S1.4 model was rebuilt with fresh upstream inputs:
- fresh A1 probability from raw daily Gold/Silver/Platinum lineage;
- fresh XAU path features derived from governed XAU intraday data;
- no archived H3 A1/IRIS prediction file consumed as model input.

## Warm-up authority

Authority:
- `GOLD_SESSION_STRUCTURAL_IRIS_S14_V2_WARMUP22_SUMMARY_2026-10-07.json`

Sources:
- pinned Stak raw daily metals for CORE3/A1;
- governed 2022 XAU15 warm-up;
- governed 2023–2025 XAU15 buffer;
- 1h XAU deterministically derived from the combined XAU15 source.

A1:
- recent window = 252
- structural minimum matured A1 rows = 80
- block size = 5

## 2023–2024 development interpretation

Canonical 1h Structural-IRIS is heterogeneous across windows.

Notable development evidence:
- Sobti Asia Morning: BA 49.91% on matched S1.4 sample;
- Sobti NY/London: BA 53.26%, versus matched A1 48.54%;
- WGC Europe: BA 52.28%, approximately matched A1 52.22%;
- WGC US: BA 50.28%, versus matched A1 43.82%;
- WGC Asia: raw accuracy rises but class balance is weak in canonical 1h form.

The Stage-1 development freeze therefore retained:
- canonical A1+1h Structural-IRIS as a global control;
- Sobti Asia Morning 15m Structural-IRIS as a window-specific challenger;
- WGC Asia balanced 15m Structural-IRIS as a window-specific challenger.

## Frozen 2025 canonical 1h transport

Authority:
`GOLD_SESSION_S14_FROZEN_2025_TRANSPORT_SUMMARY_2026-10-07.json`

| Window | N | Accuracy | BA | UP recall | DOWN recall | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Sobti Asia Afternoon | 137 | 48.91% | 48.92% | 51.47% | 46.38% | 0.2777 |
| Sobti Asia Morning | 140 | **60.71%** | **60.86%** | **64.18%** | **57.53%** | 0.2557 |
| Sobti Europe | 144 | 50.69% | 45.71% | 78.31% | 13.11% | 0.2631 |
| Sobti NY/London | 144 | 50.00% | 51.15% | 41.98% | 60.32% | 0.2726 |
| Sobti Late-US | 107 | 59.81% | 53.30% | 79.10% | 27.50% | 0.2478 |
| WGC Asia | 104 | 55.77% | 51.80% | 86.21% | 17.39% | 0.2792 |
| WGC Europe | 145 | 51.72% | 49.90% | 67.50% | 32.31% | 0.2686 |
| WGC US | 140 | 41.43% | 44.83% | 26.51% | 63.16% | 0.2998 |

## Binding identity decision

1. The canonical Model-05 baseline is `S14_A1_PLUS_1H_FULL`.
2. No duplicate baseline rerun is required.
3. Sobti Asia Morning is the strongest clean 2025 canonical transport result.
4. Canonical 1h Structural-IRIS is not a universal session champion.
5. The existing 15m branches remain separate preregistered window-specific challengers; they must not be silently relabelled as the canonical Model-05 baseline.
6. Model-specific feature analysis may now test whether the canonical A1+1h representation can be reduced/improved using development only.
7. 2026 remains unopened.
