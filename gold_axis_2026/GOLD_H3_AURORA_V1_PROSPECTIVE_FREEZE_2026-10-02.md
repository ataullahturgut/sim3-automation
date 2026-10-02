# AURORA-H3 V1 — PROSPECTIVE FREEZE / LIVE VALIDATION AUTHORITY

**Freeze timestamp:** 2026-10-02T19:10:36Z  
**Research branch:** `gold-midas-headswap-v1-20260925`  
**Frozen champion commit before live harness:** `20a0bd35f0c74bed6890378a3f95777e4be520ac`  
**Champion identity:** `AURORA_H3_V1_RESEARCH`  
**Prospective identity:** `AURORA_H3_V1_PROSPECTIVE`

## 1. Purpose

From this freeze onward, AURORA-H3 V1 is no longer retuned on newly observed H3 outcomes.

New eligible origins are written to a separate prospective ledger before their target is known. Outcomes are added only after three future retained XAU daily observations exist.

Historical / retrospective evidence and prospective evidence must never be pooled without an explicit label.

## 2. Frozen model definition

Experts:
- STRUCTURAL_IRIS = monthly expanding Logistic L2 on frozen A1 structural logit + frozen IRIS PATH features.
- PATH_GLOBAL = monthly expanding Logistic L2 on frozen IRIS PATH features only.

A1:
- expanding CORE3 Logistic L2;
- recent 252 matured CORE3 Logistic L2, class_weight=balanced;
- `p_A1 = 0.75*p_global + 0.25*p_recent252`.

IRIS PATH:
- 1h / 3h / 6h / 12h / 24h / 48h XAU hourly log returns;
- hourly lag2;
- same-day session return;
- anchor 16:00 America/New_York on feature cutoff date.

AURORA state:
- initial prospective state inherited from frozen historical ledger: **PATH_GLOBAL**.
- STRUCTURAL -> PATH:
  - latest 63 matured paired H3 outcomes;
  - at least 42 matured pairs;
  - net rescue >= +3.
- PATH -> STRUCTURAL:
  - at least 8 matured expert disagreements;
  - DART fixed-hazard posterior `Pr(PATH superior) <= 0.10`;
  - posterior predictive `q_path <= 0.40`.
- DART hazard remains fixed at **0.05**.
- No VISTA dynamic-hazard rule is active in the prospective champion.

## 3. Historical freeze boundary

Frozen retrospective expert ledger ends at:
- last feature cutoff: **2026-09-24**
- last forecast issue: **2026-09-25**
- last H3 target end: **2026-09-29**.

The public R2 history is frozen from StakTrakr commit:
- `54fdf1c8d39b7b6c7b874d0f30f784296e886044`
- frozen common-metal history through **2026-09-29**.

Any public-source updates after 2026-09-29 are append-only for prospective use. Historical rows through the frozen boundary are always reconstructed from the pinned commit, not from the latest mutable upstream history.

## 4. Prospective start

The first eligible prospective feature cutoff is:

**2026-10-02 at the completed 16:00 America/New_York hourly anchor or later.**

No feature cutoff before 2026-10-02 may enter the prospective ledger.

A row is prospective only if its forecast record is committed before the planned next-weekday issue deadline.

## 5. No backfill rule

A missed prospective origin is never reconstructed after its issuance window.

If required same-day public data / hourly anchor are unavailable before the deadline:
- record the origin as missed in status diagnostics;
- do not create a forecast row later.

This prevents outcome-aware backfilling.

## 6. Monthly refit rule

Expert coefficients are refit at the first eligible feature cutoff of each calendar month.

Training may include only:
- frozen historical origin rows with genuine frozen A1 probabilities;
- previously issued prospective rows whose H3 targets have matured by the monthly refit cutoff.

Post-freeze dates for which no genuine prospective forecast was issued are excluded from expert-level training even if their outcomes later become observable.

The daily A1 head may use all matured raw CORE3 daily labels available at its forecast cutoff because those labels are input history, not post-hoc expert predictions.

## 7. Settlement

For a prospective row with feature date D:
- retain the XAU price at D as target start;
- after three future retained common-metal/XAU daily dates are observed, set:
  - actual target end date = third future retained date;
  - `target_r3 = log(P_end/P_D)`;
  - `y_up = 1[target_r3>0]`;
  - correctness against the already-frozen AURORA forecast.

Forecast probability, direction, state and evidence columns are immutable after issuance.

## 8. Primary prospective metrics

Report only on settled prospective rows:
- N
- accuracy
- balanced accuracy when both classes are present
- Brier
- log loss
- UP recall
- DOWN recall
- monthly table
- cumulative comparison of AURORA vs its frozen active experts when available.

Do not claim statistical significance until a meaningful prospective sample accumulates.

## 9. Governance

Forbidden without a new version / new preregistration:
- changing AURORA entry/exit thresholds;
- changing DART hazard;
- changing IRIS PATH feature set;
- changing expert model class / C;
- changing A1 0.75/0.25 mixture or recent lookback;
- selecting a new champion from prospective outcomes.

Any such change must create a new research identity and leave this V1 ledger untouched.
