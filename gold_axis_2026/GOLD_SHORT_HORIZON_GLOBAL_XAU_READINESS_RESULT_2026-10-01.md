# GOLD SHORT-HORIZON GLOBAL XAU — Data Readiness Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / PASS**  
**Workflow:** Gold Short Horizon Global XAU Readiness  
**Run:** **36900860852**  
**Artifact:** **11181284118**  
**Artifact digest:** `sha256:3c07b25615d8c37c80257200231089688d74c9129c9c75276f6611259d9472f1`

## Target
Global XAU/USD daily spot-average research series:
- Gold: `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- underlying lineage: StakTrakr / MetalPriceAPI
- not BIST Metal Price.

## Coverage

| Horizon | Pre-DEV train | DEV 2022-2024 | Frozen 2025 |
|---|---:|---:|---:|
| H1 | **3,011** | **755** | **253** |
| H3 | **3,011** | **755** | **253** |
| H5 | **3,011** | **755** | **253** |

All readiness gates PASS.

DEV target characteristics:
- H1: UP 52.3%, median return +0.029%, SD 0.888%
- H3: UP 52.3%, median return +0.120%, SD 1.503%
- H5: UP 53.0%, median return +0.104%, SD 1.963%.

CORE3, CORE4 and CORE3+safe-external retain the full DEV population.

## Decision

Global XAU data are sufficient for H1/H3/H5 classical/boosting development.

2025 remains frozen.
