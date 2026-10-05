# GOLD H3 — Databento LLRS Mapping Sensitivity (2025) — 2026-10-05

**Status:** **LABEL_FREE_SOURCE_BRIDGE_REQUIRES_REVIEW**  
Estimated Databento cost: **USD 1.5681** (cap USD 1.60).  
**Mapping selection is label-free: only Yahoo↔Databento LLRS/Handoff source agreement is used.**

## One-channel sensitivity grid

| Config | Handoff matched | New/Old | Jaccard | Added | Missing | Leadlag corr | LLRS pressure corr |
|---|---:|---:|---:|---:|---:|---:|---:|
| SI_n | 28 | 33/30 | 80.0% | 5 | 2 | 0.7377 | 0.9246 |
| NQ_n | 28 | 33/30 | 80.0% | 5 | 2 | 0.7207 | 0.9221 |
| BASE | 28 | 33/30 | 80.0% | 5 | 2 | 0.7205 | 0.9227 |
| ZN_v | 28 | 33/30 | 80.0% | 5 | 2 | 0.7129 | 0.9231 |
| CL_v | 28 | 34/30 | 77.8% | 6 | 2 | 0.7315 | 0.9248 |
| GC_n | 27 | 32/30 | 77.1% | 5 | 3 | 0.7181 | 0.9275 |
| NQ_c | 27 | 32/30 | 77.1% | 5 | 3 | 0.6928 | 0.9088 |

## Label-free winner: SI_n

- Mapping: **{'GC': 'v', 'SI': 'n', 'NQ': 'v', 'ZN': 'n', 'CL': 'c'}**
- Handoff: **28 matched**, Databento 33 vs Yahoo 30, Jaccard **80.0%**.
- Added: **2025-04-17, 2025-08-05, 2025-08-06, 2025-09-26, 2025-10-31**.
- Missing: **2025-05-29, 2025-08-11**.

## Post-freeze DPTC transport

| Variant | DB actions | Yahoo actions | Matched | Jaccard | DB R/B/net |
|---|---:|---:|---:|---:|---:|
| Q95 | 10 | 9 | 9 | 90.0% | 4/6/-2 |
| Q99 | 9 | 8 | 8 | 88.9% | 3/6/-3 |

## Governance

- No competence outcome, RESCUE/BROKEN label or forecast correctness is used to pick the mapping.
- Only single-channel substitutions around the raw-source winner are tested; this is a source-lineage diagnosis, not model tuning.
- DPTC outcomes are inspected only after the source mapping is frozen.
- Passing this audit supports a source-bridged reconstruction, not a claim that Databento bars are byte-identical to Yahoo.
