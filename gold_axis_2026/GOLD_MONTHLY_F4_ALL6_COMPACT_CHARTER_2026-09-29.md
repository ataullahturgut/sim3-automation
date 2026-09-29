# GOLD MONTHLY — F4 ALL6-COMPACT DIAGNOSTIC CHARTER

**Freeze date:** 2026-09-29  
**Status:** FROZEN BEFORE MODEL OUTCOME / BLOCKED UNTIL B0-B2 PASS  
**Purpose:** test whether a compact, processing-parity bundle of six daily external information families adds value to the retained ChHHO-ANFIS baseline when all are used together.

## 1. Baseline

Frozen baseline:
- CURRENT8 = Gold/Silver/Platinum/Palladium × {MR1, GPR-conditioned VW}
- lag architecture = L1 only
- target = next-calendar-month average Gold via Gold log-return
- DEV = 2022-04..2024-12, n=33
- canonical score = 1413.029779 / 23/33

## 2. Why one combined diagnostic first

The user requested a direct system-level check after data/processing repair:
"if Rates + FX + VIX + Nasdaq + WTI + Brent are all processed like the main model and added together, what does the model give?"

This is therefore a **diagnostic challenger**, not a final feature-selection model.

No family-wide promotion/rejection will be inferred from this one combined run alone.

## 3. Exact external inputs

All daily families use only origin-safe observations under their family cutoff.

### Rates — 4 inputs
1. NOM10_MR_ANALOG = mean nominal10[p] - mean nominal10[p-1]
2. NOM10_VW_ANALOG = GPR-conditioned weighted intramonth daily nominal10 first differences
3. REAL10_MR_ANALOG = mean real10[p] - mean real10[p-1]
4. REAL10_VW_ANALOG = GPR-conditioned weighted intramonth daily real10 first differences

### FX — 2 inputs
Canonical family representative: Broad USD index.
5. BROADUSD_MR1 = log(mean broadUSD[p] / mean broadUSD[p-1])
6. BROADUSD_VW = GPR-conditioned weighted intramonth daily broad-USD log returns

### VIX — 2 inputs
7. VIX_MR1 = log(mean VIX[p] / mean VIX[p-1])
8. VIX_VW = GPR-conditioned weighted intramonth daily VIX log returns

### Nasdaq-100 — 2 inputs
9. NDX_MR1 = log(mean NDX[p] / mean NDX[p-1])
10. NDX_VW = GPR-conditioned weighted intramonth daily NDX log returns

### WTI — 2 inputs
11. WTI_MR_ANALOG = mean WTI[p] - mean WTI[p-1]
12. WTI_VW_ANALOG = GPR-conditioned weighted intramonth daily WTI price differences

### Brent — 2 inputs
13. BRENT_MR1 = log(mean Brent[p] / mean Brent[p-1])
14. BRENT_VW = GPR-conditioned weighted intramonth daily Brent log returns

Total:
- internal CURRENT8 = 8
- external = 14
- total native inputs = **22**

No CNY, individual major-FX, CPI or Copper is included in ALL6-COMPACT.
Those are separate later decomposition lanes.

## 4. GPR weighting parity

For every VW analogue, use the exact frozen CURRENT8 age-weight formula:

- daily increments are ordered within completed origin month p;
- age = newest return 0, older observations increasing age;
- lambda = 0.1 × exp(-10 × clipped_GPR_z);
- weights = exp(-lambda × age), normalized to sum 1;
- governed GPR timing follows the same lagged PIT logic as CURRENT8.

No separate external-family weighting function may be invented.

## 5. Monthly representation parity

Price/index families use **monthly mean levels**, not month-end endpoints.

Rates use **monthly mean yield changes**, because yield levels can be negative and logarithms are inappropriate.

Both p and p-1 means are computed under the same family-specific historical availability rule.

## 6. Release cutoffs

Binding conservative cutoffs for the diagnostic:
- H.15 Rates: 2 calendar days
- H.10 Broad USD: 7 calendar days
- VIX: 1 calendar day
- Nasdaq-100: 1 calendar day
- WTI: 7 calendar days
- Brent: 7 calendar days

The same cutoff convention is applied historically to every month to prevent asymmetric hindsight.

## 7. L1 architecture

ALL6 uses the retained main-model lag architecture:
- only completed origin month **L1**
- no L2/L3 concatenation
- no distributed lag expansion beyond the within-month VW compression

## 8. Optimizer parity

5 fuzzy rules and 22 inputs:
- antecedent parameter dimension = 2 × 5 × 22 = **220**
- baseline dimension = 80
- baseline POP = 24

Population-density rule:
POP = ceil(24 × 220 / 80) = **66**

Frozen:
- POP = 66
- generations = 45
- repeats = 3

A diagnostic companion BASE run remains 8 inputs / POP 24 and must reproduce 1413.029779 / 23/33.

## 9. Gates before scoring

ALL6 score is not interpretable unless:
1. External Authority V2 PASS
2. transform parity audit PASS
3. no canonical-history shortening
4. all 14 external features finite for required samples
5. historical availability cutoffs logged
6. BASE parity PASS
7. optimizer population = 66
8. no target-month information
9. no 2025/2026 selection use
10. reconstructed forecasts finite

Pathological output => ARCHITECTURE_UNSTABLE, not "external data useless."

## 10. Evaluation

Primary:
- DEV ΣAE vs canonical BASE
- direction /33

Robustness:
- paired monthly wins/losses/ties
- median paired AE improvement
- 2022/2023/2024 ΔΣAE
- worst AE
- signed bias
- leave-one-origin total improvement

No 2025 transport is opened until the diagnostic specification and DEV decision are frozen.

## 11. Interpretation rule

If ALL6 improves robustly:
- external information is useful under processing parity;
- proceed to family decomposition and constrained compact selection.

If ALL6 does not improve:
- do **not** reject all six families;
- inspect dimensionality, redundancy and family decomposition before any family-wide conclusion.

## Kontrol ve Uyum Özeti

- outcome seen before charter freeze: NO
- CURRENT8 changed: NO
- L1 changed: NO
- external raw-level stuffing: NO
- endpoint-only shortcut: NO
- daily path preserved through VW: YES
- optimizer dimension parity: YES
- total inputs: 22
- ChHHO POP: 66
- authorized to run now: NO — requires B0/B1/B2 PASS
