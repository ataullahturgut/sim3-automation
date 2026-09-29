# GOLD MONTHLY — EXTERNAL INFORMATION MULTI-MODEL SCREEN V1

**Date:** 2026-09-29  
**Status:** COMPLETE / ARTIFACT-ONLY / ZERO NEON READS  
**Run:** 36527575572  
**Artifact:** 11015042783  
**Commit:** 529dc3739673a8ff4787b803fc6e1446ae7355d7

This stage measures incremental external information on eight frozen strong models using the same chronology-safe prequential residual-correction protocol. It is **not** native architecture retraining.

## 1. Cross-family summary

| Model | Base ΣAE | Base dir | Best external block | Corrected ΣAE | Corrected dir | ΔΣAE |
|---|---:|---:|---|---:|---:|---:|
| **ChHHO-ANFIS** | 1413.0299 | 23/33 | **INFLATION_HEADLINE** | **1343.6354** | 23/33 | **69.3945** |
| **DE-ABC-RBFNN** | 1415.8371 | 25/33 | **RATES_PIT** | **1373.5811** | 25/33 | **42.2560** |
| **PLS1-V1-ALL4** | 1420.0291 | 20/33 | **RATES_PIT** | **1379.3835** | 19/33 | **40.6456** |
| **FULL7-ANN** | 1428.8590 | 22/33 | **FX_CNY_PIT** | **1391.1359** | 23/33 | **37.7231** |
| **REDUCED4-ANN** | 1431.4587 | 24/33 | **FX_CNY_PIT** | **1398.7775** | 24/33 | **32.6812** |
| LMC2_RBF_M32 | 1424.1711 | 19/33 | BASE | 1424.1711 | 19/33 | 0.0000 |
| **CATBOOST_PRICE** | 1460.4339 | 20/33 | **FX_CNY_PIT** | **1428.4187** | 20/33 | **32.0153** |
| EPSILON_RBF_DAILY12 | 1449.1874 | 19/33 | BASE | 1449.1874 | 19/33 | 0.0000 |

Result:
- **6/8 strong models** have at least one external block that passes the robustness gate.
- **2/8** — LMC2_RBF_M32 and EPSILON_RBF_DAILY12 — do not show a robust external improvement under this correction protocol.
- The useful external channel is **model-specific**, not universal.

## 2. Block results

### ChHHO-ANFIS
- CPI headline surprise: **1343.6354**, ΔΣAE **+69.3945 / +4.91%**, 23/33 — PASS.
- Rates PIT: 1370.9204, ΔΣAE +42.1095 / +2.98%, 23/33 — PASS.
- USD/CNY PIT: 1355.7558, ΔΣAE +57.2741 / +4.05%, 23/33 — PASS.
- H.10 broad USD: 1370.5743, ΔΣAE +42.4555 / +3.00%, **24/33** — PASS.
- H.10 major FX: 1363.7485, ΔΣAE +49.2814 / +3.49%, 23/33 — PASS.
- **Winner: headline CPI surprise.**

### DE-ABC-RBFNN
- CPI headline surprise: 1393.8337, ΔΣAE +22.0035 / +1.55%, 24/33 — PASS.
- Rates PIT: **1373.5811**, ΔΣAE **+42.2560 / +2.98%**, 25/33 — PASS.
- USD/CNY PIT: 1400.5230, ΔΣAE +15.3141 / +1.08%, 25/33 — PASS.
- H.10 broad USD: FAIL.
- H.10 major FX: FAIL.
- **Winner: rates PIT.**

### PLS1-V1-ALL4
- CPI: FAIL.
- Rates PIT: **1379.3835**, ΔΣAE **+40.6456 / +2.86%**, direction 20/33 → **19/33** — PASS.
- USD/CNY PIT: FAIL.
- H.10 broad USD: FAIL.
- H.10 major FX: FAIL.
- **Winner: rates PIT**, with a one-month direction trade-off.

### FULL7-ANN
- CPI: 1397.6160, ΔΣAE +31.2430 / +2.19%, **23/33** — PASS.
- Rates PIT: 1394.6265, ΔΣAE +34.2325 / +2.40%, **23/33** — PASS.
- USD/CNY PIT: **1391.1359**, ΔΣAE **+37.7231 / +2.64%**, **23/33** — PASS.
- H.10 broad / major FX: FAIL.
- **Winner: USD/CNY PIT.**

### REDUCED4-ANN
- CPI: 1406.0072, ΔΣAE +25.4515 / +1.78%, 24/33 — PASS.
- Rates PIT: FAIL.
- USD/CNY PIT: **1398.7775**, ΔΣAE **+32.6812 / +2.28%**, 24/33 — PASS.
- H.10 broad / major FX: FAIL.
- **Winner: USD/CNY PIT.**

### LMC2_RBF_M32
- CPI: FAIL.
- Rates: FAIL.
- USD/CNY: FAIL.
- H.10 broad: FAIL.
- H.10 majors: FAIL.
- **Decision: BASE retained.**

### EPSILON_RBF_DAILY12
- All tested external blocks: **FAIL**.
- **Decision: BASE retained.**

### CATBOOST_PRICE
- CPI: 1437.8013, ΔΣAE +22.6327 / +1.55%, 20/33 — PASS.
- Rates PIT: 1429.3816, ΔΣAE +31.0523 / +2.13%, **21/33** — PASS.
- USD/CNY PIT: **1428.4187**, ΔΣAE **+32.0153 / +2.19%**, 20/33 — PASS.
- H.10 broad / major FX: FAIL.
- **Winner: USD/CNY PIT.**

## 3. Scientific interpretation

The result strengthens the earlier external-information finding:

- ChHHO is most sensitive to **inflation surprise**, with FX also strongly useful.
- DE-ABC and PLS1 are most sensitive to the **rates / monetary-regime channel**.
- Both ANN ensembles and CatBoost gain most from the strict PIT **USD/CNY** channel.
- LMC2-GPR and DAILY12-SVR show no robust benefit from these blocks under the prequential correction design.
- Therefore the missing external information is not one universal factor; different model architectures leave different residual information channels unexplained.

## 4. Important boundary — native integration

This result is an **external-information value screen**, not native model retraining.

Native input integration is not yet scientifically authorized because the current CPI/rates/FX compact snapshots do not cover the full historical training range used by the base models. Filling pre-2022 history with zeros or present-day revised series would invalidate the causal contract.

Before native integration:
1. build a governed long-history origin-safe external snapshot,
2. prove availability/revision rules,
3. reproduce each base under the same usable training window,
4. then compare BASE vs native external input,
5. keep 2025 outside selection.

## 5. Execution / data governance

- Base forecasts loaded from frozen GitHub Actions authority artifacts.
- Neon connection: **disabled**.
- Neon reads: **0**.
- CPI and rates/CNY: governed compact snapshots already stored in repo.
- H.10 FX: official Federal Reserve Board H.10 with conservative 7-day origin cutoff; available successfully in final run.
- Random split: NONE.
- DEV selection authority: 2022-04..2024-12 only.
- 2025 used in this screen: NO.
- All eight base-model metric parity checks: PASS.

## 6. Next stage

Priority for long-history backfill / native external integration:
1. ChHHO + CPI.
2. DE-ABC + Rates.
3. PLS1 + Rates.
4. FULL7 ANN + USD/CNY.
5. REDUCED4 ANN + USD/CNY.
6. CATBOOST_PRICE + USD/CNY.
7. LMC2 and DAILY12-SVR remain BASE controls unless a new external-information family is justified.

## Kontrol ve Uyum Özeti

- Eight-model frozen base parity: PASS.
- External screen without Neon: PASS.
- 6/8 models with robust external improvement: YES.
- 2025 tuning/selection: NONE.
- Random split: NONE.
- Hindsight bad-month feature picking: NONE.
- Native integration claim: NO / NOT YET.
