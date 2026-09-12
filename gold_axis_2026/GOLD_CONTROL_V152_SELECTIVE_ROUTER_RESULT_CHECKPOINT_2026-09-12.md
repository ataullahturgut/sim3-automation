# Gold Control V1.52 — Selective Event Router Result Checkpoint

**Run:** GitHub Actions `34703322008`  
**Artifact:** `10300901232`  
**Artifact digest:** `sha256:1bfd98f0bdde2ed8b9e9966300f51f92be4845ce47a19b6404e750c665312947`  
**Status:** research-only; no production authority.

## Frozen hypothesis

The V1.52 contract was committed before successor scoring. The primary short-horizon event specialist contains only `EMPLOYMENT` and `INFLATION`. `FOMC` remains separate diagnostic because the literature and pre-2025 formation logic imply different timing/information/asymmetry. General 1D/3D remains `NO_SIGNAL` until separately proven.

## Main result

### Primary Employment + Inflation router

| Period | R5 | R15 (primary) | R30 |
|---|---:|---:|---:|
| 2023–2024 formation | 33/41 = **80.49%**, p=0.0000561 | 31/41 = **75.61%**, p=0.000725 | 31/41 = **75.61%**, p=0.000725 |
| 2025 retrospective validation | 15/20 = **75.00%**, p=0.02069 | 15/20 = **75.00%**, p=0.02069 | 12/20 = 60.00%, p=0.2517 |
| 2026 retrospective test (available event bars only) | 8/9 = **88.89%**, p=0.01953 | 7/9 = **77.78%**, p=0.08984 | 7/9 = **77.78%**, p=0.08984 |

Median signed returns are positive for all primary-router R5/R15 cells above.

### Why routing helps

In 2025 the pooled all-event R15 result was 19/28 = 67.86%, while the pre-frozen Employment+Inflation router was 15/20 = 75.00%. The FOMC diagnostic lane was only 4/8 = 50.00% at R15 in 2025, supporting the decision not to dilute the data-release specialist with FOMC.

In 2026 FOMC happened to perform well on the currently observable subset; this is **not** used to revise the frozen family rule. Re-adding FOMC because it helps the already-seen 2026 result would be hindsight selection.

### High-confidence strong-state tier

Formation Employment+Inflation strong-state events were 4/4 at R5/R15/R30, but `n=4` is below the frozen minimum `n=5`; therefore the high-confidence gate is **FAIL / INSUFFICIENT_SAMPLE**, not promoted. 2025 has only three such observed events and 2026 has no mature primary strong-state target in the current 1-minute cache.

## Scientific interpretation

The strongest Gold Control directional result is now not an unconditional daily classifier. It is a **selective event-conditioned specialist**:

- normal day: no forced 1D/3D direction claim;
- Employment/Inflation event with nonzero Macro Event score: event-direction signal is eligible;
- R15 remains the primary thesis endpoint;
- R5 is a strong secondary endpoint and currently the highest observed hit rate;
- FOMC stays a separate specialist/diagnostic lane;
- Market Shock V3 may confirm transmission after it becomes observable, but may not backdate the initial signal;
- FAST/SLOW/Monthly Direction/BOCPD/Emergency/GVZ remain context/risk/regime engines rather than equal votes.

The 2025–2026 successor diagnostics are not fresh blind confirmation because those years were already researcher-visible in predecessor work. The result is nevertheless coherent across formation and retrospective years and justifies a newly frozen prospective shadow study.
