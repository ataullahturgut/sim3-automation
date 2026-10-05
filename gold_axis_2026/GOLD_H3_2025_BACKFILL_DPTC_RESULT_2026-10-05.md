# GOLD H3 — 2025 Source Backfill + DPTC Replay V1

**Status:** SOURCE_REPRO_MISMATCH_REVIEW_REQUIRED

## Source reconstruction QA

- IFBC raw overlap rows: **280**
- LLRS overlap rows: **332**
- raw-source reproduction pass (<1e-8): **False**
- reconstructed VAST first origin: **2024-10-14**
- reconstructed IFBC score first origin: **2025-01-29**
- reconstructed LLRS first origin: **2024-12-02**
- first complete extended Handoff state: **2025-03-03**

## 2025 full-year replay

- origins: **248**
- combined V5+frozen SAGE+RuleFlow baseline: **171/248 = 68.95%**, BA **67.13%**
- reconstructed canonical Handoff alarms: **30**, rescue/broken **8/22**

| Variant | Actions | Rescue | Broken | Net | Precision | Entry | Correct/N | Accuracy | BA |
|---|---:|---:|---:|---:|---:|---|---:|---:|---:|
| Q95 | 9 | 4 | 5 | -1 | 44.4% | 2025-03-26 | 170/248 | 68.55% | 67.17% |
| Q99 | 8 | 3 | 5 | -2 | 37.5% | 2025-03-26 | 169/248 | 68.15% | 66.65% |

## Action chronology

### Q95
- 2025-03-26 — TRUST — RESCUE — SELLR=True
- 2025-03-28 — TRUST — BROKEN — SELLR=False
- 2025-03-31 — TRUST — BROKEN — SELLR=False
- 2025-04-24 — PHASE — RESCUE — SELLR=False
- 2025-04-25 — TRUST — RESCUE — SELLR=True
- 2025-04-30 — TRUST — BROKEN — SELLR=True
- 2025-05-09 — TRUST — BROKEN — SELLR=False
- 2025-10-24 — PHASE — RESCUE — SELLR=False
- 2025-10-28 — PHASE — BROKEN — SELLR=False

### Q99
- 2025-03-26 — TRUST — RESCUE — SELLR=True
- 2025-03-28 — TRUST — BROKEN — SELLR=False
- 2025-03-31 — TRUST — BROKEN — SELLR=False
- 2025-04-25 — TRUST — RESCUE — SELLR=True
- 2025-04-30 — TRUST — BROKEN — SELLR=True
- 2025-05-09 — TRUST — BROKEN — SELLR=False
- 2025-10-24 — PHASE — RESCUE — SELLR=False
- 2025-10-28 — PHASE — BROKEN — SELLR=False

## Interpretation discipline

- Missing 2025 hourly source history is reconstructed from the same Yahoo futures identities and the same original VAST/IFBC/LLRS equations.
- Frozen post-start IFBC and LLRS snapshots are retained; reconstructed rows are used only before their original first dates.
- Handoff ranks are recomputed over the extended history, because the purpose of this audit is explicitly to test the model after filling the missing historical state.
- SAGE is not back-activated into 2025 H1; its original maturity boundary is preserved.
- This is a historical reconstruction/backfill replay, not prospective validation.
