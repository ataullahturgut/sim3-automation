# GOLD CONTROL — SQRT MEMORY POLICY STAGE 5–6 SUMMARY

**Date:** 2026-09-24  
**Identity:** `GOLD_CONTROL_SQRT_MEMORY_POLICY_2025_TRANSPORT_2026_STRESS_V1`  
**Stage 7:** NOT STARTED — reserved for joint decision.

## Stage 5 — Locked 2025 transport

Frozen primary policy: **W=500**.  
Frozen band: **475 / 500 / 525 / 550**.  
Comparator: **EXPANDING**.  
No post-open retuning occurred.

### 2025 primary comparison

| Policy | MSE | QLIKE | AUC | Coverage | Precision | Recall | Alerts |
|---|---:|---:|---:|---:|---:|---:|---:|
| Expanding | 3.54787e-8 | 0.318799 | 0.850657 | 0.4135 | 0.7347 | 0.7200 | 98 |
| W=500 | 3.48647e-8 | 0.365989 | 0.847962 | 0.4557 | 0.7870 | 0.7328 | 108 |

W=500 improves MSE by about **1.73%** versus expanding, preserves AUC within the frozen -0.02 guard, and improves precision/recall. However QLIKE is about **14.80% worse**. Therefore the preregistered transport rule classifies W=500 as **MIXED**.

### 2025 frozen-band result

None of W=475/500/525/550 satisfies the complete supportive rule because all four have QLIKE above expanding.

**Band supportive count: 0/4**  
**Band transport label: NOT_SUPPORTIVE**

Break-conditioned remains diagnostic only. It again selects **2020-03-20**, with lower coverage than expanding and no authority to replace the frozen primary policy.

## Stage 6 — 2026 stress/anatomy only

Data available through **2026-08-31** in the governed panel.

No selection, tuning, freeze change, or promotion is allowed from 2026.

| Policy | MSE | QLIKE | AUC | Coverage | Precision | Recall | Alerts |
|---|---:|---:|---:|---:|---:|---:|---:|
| Expanding | 6.49512e-8 | 0.385201 | 0.642885 | 0.9306 | 0.7950 | 0.9481 | 161 |
| W=500 | 7.04361e-8 | 0.431422 | 0.653523 | 0.7861 | 0.7059 | 0.8348 | 136 |
| Break-conditioned | 7.35220e-8 | 0.464384 | 0.716721 | 0.3353 | 0.7069 | 0.5325 | 58 |

In 2026 stress, W=500 has worse MSE and QLIKE than expanding, while AUC is modestly higher. The expanding comparator produces much higher alarm coverage and recall.

The origin-safe structural-break diagnostic selects a new last break at **2025-05-02** for the 2026 formation set. This is descriptive anatomy only; it cannot trigger reselection under the frozen contract.

## Binding interpretation before Stage 7

1. The pre-2025 rolling plateau was real on 2022–2024 evidence, but it **did not transport cleanly into locked 2025** under the preregistered multi-metric rule.
2. The failure is not repaired by choosing another member of 475–550; all four fail the full 2025 supportive rule.
3. 2026 stress further weakens the case for treating the frozen short-memory policy as universally stable.
4. Expanding remains the stronger loss-based comparator in 2025 QLIKE and in both 2026 MSE/QLIKE.
5. Break diagnostics indicate regime structure is real and evolving: 2020-03-20 was stable pre-2025; the 2026 formation set detects 2025-05-02. This does **not** authorize automatic break-conditioned deployment.
6. No Stage 7 experiment has been started.

## Governance

- 2025 was opened only after the freeze.
- W=500 and the 475–550 envelope were not changed after 2025.
- 2026 was used only as stress/anatomy.
- No random split.
- No production writes.
- No runtime promotion.
- Canonical manifest not changed by this research branch.
