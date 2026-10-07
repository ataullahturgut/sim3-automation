# GOLD EXECUTION FSMR STAGE-4 RESULT — 2026-10-07

**Status:** COMPLETE / 2023-SELECTED FINITE-STATE MOMENTUM-REVERSAL MODEL

Model identity and abstention delta are selected on 2023 only. 2024 is confirmation; 2025 is retrospective transport.

Selected: **FSMR8**, delta **0.04**.

| Period | N | Coverage | Accuracy | BA | UP recall | DOWN recall |
|---|---:|---:|---:|---:|---:|---:|
| 2023 selection | 135 | 52.94% | 55.56% | 55.51% | 49.25% | 61.76% |
| 2024 confirmation | 137 | 52.90% | 49.64% | 49.37% | 53.42% | 45.31% |
| 2025 transport | 117 | 46.25% | 57.26% | 57.74% | 55.07% | 60.42% |

2024 confirmation pass: **False**.

FSMR4 uses four sign states (++,+-,-+,--). FSMR8 adds a label-free high/low normalized-impulse state. Posterior state probabilities are shrunk toward the historical global UP prevalence to reduce sparse-state overfit.
