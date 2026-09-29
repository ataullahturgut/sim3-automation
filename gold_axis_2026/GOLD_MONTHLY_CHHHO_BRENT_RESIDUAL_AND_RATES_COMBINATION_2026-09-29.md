# GOLD MONTHLY — CHHHO BRENT RESIDUAL + RATES COMBINATION SCREEN

**Date:** 2026-09-29  
**Status:** COMPLETE  
**Selection authority:** DEV 2022-04..2024-12 only  
**2025/2026 role:** NOT USED FOR SELECTION

## 1. Brent isolated residual screen

Frozen BASE:
- ChHHO-ANFIS artifact **10989389723**
- DEV ΣAE **1413.0298545342782**
- Direction **23/33**

Predeclared Brent blocks:
- **BRENT_R1_MR1** = monthly Brent log mean change
- **BRENT_R2_VW** = GPR-weighted daily Brent log-return summary
- **BRENT_R3_MR1_VW** = both

Results:
- **BRENT_R1_MR1**: **1346.5024153590207 / 23/33**, improvement **66.52743917525754 USD**, robustness **PASS**
- **BRENT_R2_VW**: **1349.1809091408556 / 23/33**, improvement **63.84894539342258 USD**, robustness **PASS**
- **BRENT_R3_MR1_VW**: **1357.7061801731188 / 23/33**, improvement **55.32367436115942 USD**, robustness **PASS**

Selected Brent representation:
**BRENT_R1_MR1**

BRENT_R1 robustness:
- eligible BASE ΣAE **843.2884386436745**
- corrected **776.7609994684169**
- improvement **66.52743917525754 USD**
- improvement excluding single best month **49.835209255403925 USD**
- 2024 improvement **60.713525068055105 USD**

Execution:
- run **36590486319**
- head **f2eb03085e42005a3902dd278d94f17544675e1b**
- job **109481990464**
- artifact **11043268953**
- digest `sha256:014754f03dc8f754cce60d385f98146c0ef8094a760940d13564633706b77c27`

## 2. Rates + Brent combination

Controls:
- Rates exact strict-PIT residual: **1370.9203928352813 / 23/33**
- Brent winner: **1346.5024153590207 / 23/33**

Combined:
- **Rates + Brent = 1377.101415184695 / 23/33**
- robustness gate **PASS**
- eligible improvement vs BASE **35.928439349583186 USD**
- excluding single best month **10.59848464793231 USD**
- 2024 improvement **65.20620154107951 USD**

The combined block is worse than both components:
- worse than Brent alone by **30.59899982567436 USD**
- worse than Rates alone by **6.18102234941363 USD**

Therefore the combination adds no incremental value under the fixed Ridge residual protocol.

Execution:
- run **36590746098**
- head **b67b1dad7c816a3869f96e22661d4b44e50772c3**
- job **109482871506**
- artifact **11043503614**
- digest `sha256:d7d457fb82b5f55dedc9d1dbac50ba38271b0436be650424a0b486242ad86f81`

## Decision

- **Brent residual information is supported.**
- **BRENT_R1_MR1 is the selected Brent residual challenger.**
- **Rates + Brent is rejected as a combination**, despite passing the robustness gate, because it is dominated by both isolated components.
- Do not assume stacking useful residual blocks improves performance.
- Next clean step: freeze BRENT_R1_MR1 and transport unchanged to 2025/2026 reporting.
