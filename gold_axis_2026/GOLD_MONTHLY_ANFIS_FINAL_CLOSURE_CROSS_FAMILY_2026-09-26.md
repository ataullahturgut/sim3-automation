# GOLD MONTHLY FORECAST — ANFIS FINAL CLOSURE & CROSS-FAMILY RE-AUDIT

Date: 2026-09-26
Status: ANFIS FAMILY COMPLETE / CROSS-FAMILY ACTIVE-METRIC UPDATE COMPLETE

## 1. Binding protocol
- Target: H=1 next-calendar-month average XAU/USD price.
- Inputs: frozen governed 8-feature VW-MIDAS contract.
- Outputs: Gold/Silver/Platinum/Palladium returns jointly; Gold price primary.
- DEV authority only: 2022-04..2024-12, n=33.
- 2025: locked retrospective transport, never selection.
- 2026 Jan-Jul: retrospective stress, never selection.
- Random split: none.
- Target-month leakage: none.
- DB: READ_ONLY.
- Active selection metrics: DEV cumulative absolute error (ΣAE, lower better) + monthly direction (higher better).

## 2. ANFIS program completed

### Vanilla anchor
Vanilla ANFIS V3 checked:
- DEV ΣAE 1852.0465
- direction 21/33 = 63.64%
- canonical checking-data early stopping
- no metaheuristic

### Broad screen
32/32 metaheuristic ANFIS hybrids executed.
27 passed scientific gate.
Five broad-screen candidates were scientific-gate rejects due pathological forecast magnitude and were ineligible as parents: ABC, WOA, FPA, HGS, AOA.

Stage-2 frozen parents:
- MFO-ANFIS: DEV ΣAE 1630.3325; 20/33
- HHO-ANFIS: DEV ΣAE 1646.1336; 23/33

### Stage-3 parity refinements
PASS but no new Pareto:
- MPA-CPA: 1918.5637 / 18/33
- PSO-TLBO Hybrid: 3156.9979 / 19/33
- TLBO-tuned PSO: 3465.1623 / 20/33

Scientific-gate FAIL:
- Adaptive PSO
- Adaptive TLBO
- Adaptive Crow
- DE-tuned PSO
- MPA-SCA
- MPA-GA

### Stage-3C literature-specific ANFIS
#### ChHHO-ANFIS — PASS / NEW FAMILY CHAMPION
Successful rerun evidence:
- GitHub Actions run 36251783712
- CHHHO job 108431053726
- scientific gate PASS

DEV:
- ΣAE 1413.0297794085
- direction 23/33 = 69.70%
- MAE 42.8191
- MAPE 2.10768%
- RMSE 54.8274
- relative MAE vs RW 0.80377
- worst APE 6.0975%

Year breakdown:
- 2022 Apr-Dec: ΣAE 397.8794; direction 7/9
- 2023: ΣAE 395.7140; direction 7/12
- 2024: ΣAE 619.4364; direction 9/12

Reporting only:
- 2025: ΣAE 1252.0542; direction 9/12; MAE 104.3378
- 2026 Jan-Jul: ΣAE 1178.1395; direction 5/7; MAE 168.3056

#### MVO-ANFIS — PASS / REJECT
The first MVO attempt was implementation-blocked by a vector-to-scalar assignment bug. The bug was fixed and MVO was rerun successfully in run 36251783712.
Final valid MVO:
- DEV ΣAE 2057.3973
- direction 17/33
- MAE 62.3454
- 2025 ΣAE 1378.2897 / 9/12
- 2026 ΣAE 5600.4172 / 4/7
Decision: valid experiment, rejected.

## 3. ChHHO robustness

Signed-error correlation:
- ChHHO vs FULL7 ANN ≈ 0.9084
- ChHHO vs REDUCED4 ANN ≈ 0.8887

Leave-one-origin sensitivity:
- Against FULL7 ANN, ChHHO retains lower remaining DEV ΣAE in 24/33 leave-one-origin deletions.
- Against REDUCED4 ANN, ChHHO retains lower remaining DEV ΣAE in 26/33 leave-one-origin deletions.
- Therefore the price advantage is not driven by a single isolated origin, although some individual deletions can reverse the ordering.

Year stability:
- ChHHO is not dependent on one DEV year; it records finite and competitive error in all three DEV year blocks.
- 2024 is the hardest DEV block but remains controlled; no pathological tail event appears in accepted ChHHO output.

## 4. Controlled ensemble audit

Two-model blend tested:
- ChHHO + FULL7 ANN
- ChHHO + REDUCED4 ANN
- fixed weight grid 0.00..1.00 by 0.05.

### Full-DEV fit — NOT honest evidence
The same-DEV optimized blends look attractive:
- ChHHO 35% + REDUCED4 65%: ΣAE 1384.7022 / 23/33.
- ChHHO 25% + REDUCED4 75%: ΣAE 1396.4995 / 24/33.
- ChHHO 20% + FULL7 80%: ΣAE 1403.0230 / 21/33.
These are in-sample meta-fits and are NOT eligible for promotion.

### Honest expanding-prequential DEV
Protocol:
- first 6 DEV origins use 50/50;
- afterward, weight chosen only from earlier DEV origins by minimum prior ΣAE;
- fixed 0.05 grid;
- no 2025/2026 involvement.

Results:
- ChHHO + FULL7 prequential: ΣAE 1453.2991 / 22/33.
- ChHHO + REDUCED4 prequential: ΣAE 1460.8086 / 23/33.

Both are worse in price error than ChHHO alone (1413.0298).

Decision:
- No ANFIS+ANN weighted ensemble promoted.
- Same-small-sample optimized weights show meta-overfit.
- ChHHO remains primary price model.

## 5. Updated cross-family active-metric table

| Model | Family | DEV ΣAE | Direction |
|---|---|---:|---:|
| ChHHO-ANFIS | ANFIS | 1413.03 | 23/33 |
| FULL7 ANN | ANN | 1428.86 | 22/33 |
| REDUCED4 ANN | ANN | 1431.46 | 24/33 |
| AOA-ELM | ELM | 1474.10 | 20/33 |
| ABC-ELMFIS | ELMFIS | 1524.89 | 21/33 |
| SMA-ELMFIS | ELMFIS | 1651.45 | 25/33 |
| TLBO-ELM | ELM | 1758.75 | 23/33 |
| Vanilla ANFIS | ANFIS | 1852.05 | 21/33 |

## 6. Updated global DEV Pareto frontier

Nondominated active-metric set:
1. ChHHO-ANFIS — 1413.03 / 23/33
2. REDUCED4 ANN — 1431.46 / 24/33
3. SMA-ELMFIS — 1651.45 / 25/33

Consequences:
- FULL7 ANN is now globally dominated by ChHHO-ANFIS.
- ChHHO is the new price-error extreme and best primary monthly price candidate.
- REDUCED4 remains the strongest near-price-leader directional challenger.
- SMA-ELMFIS remains pure direction extreme / auxiliary direction specialist.

## 7. Final family roles

### ANFIS
PRIMARY MONTHLY PRICE FAMILY.
- ChHHO-ANFIS = primary price model.
- HHO/MFO = internal ANFIS broad-screen benchmarks.
- Vanilla = architecture anchor.
- MVO = rejected.
- unstable adaptive/meta-on-meta variants = rejected by scientific gate.

### ANN
SECONDARY / BALANCED ENSEMBLE FAMILY.
- REDUCED4 = balanced price-direction challenger.
- FULL7 = retained benchmark but no longer global Pareto.

### ELMFIS
AUXILIARY DIRECTION FAMILY.
- SMA-ELMFIS = direction extreme / confirmation signal.
- hard direction override remains not promoted.

### ELM
SINGLE-MODEL BENCHMARK FAMILY.
- AOA-ELM = price benchmark.
- TLBO-ELM = direction benchmark within ELM.

## 8. Final project decision
Current primary monthly price candidate:
- ChHHO-ANFIS.

Current balanced challenger:
- REDUCED4 ANN.

Current direction specialist:
- SMA-ELMFIS.

No learned cross-family ensemble is promoted because honest prequential DEV does not beat ChHHO alone.

## 9. Control and compliance summary
- DEV-only selection authority: PASS.
- 2025 excluded from selection: PASS.
- 2026 excluded from selection: PASS.
- Random split: NONE.
- Target-month leakage: NONE.
- DB READ_ONLY: PASS.
- Scientific instability gate: ACTIVE.
- MVO implementation bug corrected before evaluation: PASS.
- In-sample blend optimization treated as non-honest evidence: PASS.
- Honest prequential blend audit completed: PASS.
- ANFIS family process: COMPLETE.
- Cross-family active-metric update: COMPLETE.
