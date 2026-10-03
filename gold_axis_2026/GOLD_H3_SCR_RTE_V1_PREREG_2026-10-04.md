# SCR-RTE-H3 V1 — SUPPORT-CONSTRAINED SPECIALIST REVERSAL ENGINE

**Freeze date:** 2026-10-04  
**Identity:** `SCR_RTE_H3_V1`  
**Branch:** `gold-h3-scr-rte-v1-20261004`  
**Intended first clean prospective origin:** 2026-10-05  
**Status:** **FROZEN BEFORE PROSPECTIVE USE**

## 1. Scientific status

The 2026 historical holdout has already been spent by RC-RTE V2. Therefore:
- 2022–2026-09 historical outcomes are now development/stress-test data;
- no retrospective 2026 improvement may be called a clean holdout result;
- the first clean evidence for SCR-RTE begins prospectively after this freeze.

## 2. Core hypothesis

Hard regime labels are insufficient because KMeans always assigns an origin to some cluster, even when the origin lies outside the historical support of successful reversal states.

SCR-RTE replaces hard regime permission with **specialist-specific local support and local competence**.

The decision is not:
> which regime is this?

It is:
> does this origin lie inside the historical support of this exact reversal specialist, and have nearby historical states shown positive rescue competence?

## 3. Frozen reversal specialists

No specialist thresholds are changed.

### SB — slow-burn
`p_rte >= 0.75 AND prev_p_rte >= 0.60 AND dp_rte <= 0.05`

### OPT — option-confirmed
`p_rte >= 0.65 AND p_inst >= 0.50 AND signed_opt_pressure > 0`

### MAT — material-reversal
`p_material >= 0.70`

A candidate may activate one or more specialists.

## 4. Frozen state geometry

Use the same four origin-available axes:
- persistence
- fragility
- option_opposition
- participation_shock

Raw inputs and axis formulas are identical to RC-RTE.

At each decision/refit:
- standardization parameters are estimated using matured historical eligible rows only.

## 5. Specialist-specific conformal support

For each active specialist separately, create a library of its matured historical proposal states.

Minimum library size:
- **15 proposals**

Nonconformity score:
- Euclidean distance in the standardized 4-axis state space to the **5th nearest** proposal state from the same specialist.

Calibration:
- for every historical specialist proposal, compute its leave-one-out distance to its own 5th-nearest same-specialist proposal;
- candidate support p-value:
  `p_support = (1 + count(calibration_score >= candidate_score)) / (n + 1)`.

Support gate:
- **p_support >= 0.10**

Thus the most outlying ~10% of specialist states are fail-closed without using target labels.

## 6. Local specialist competence

Among the same-specialist historical library:
- take the **15 nearest** proposal states to the candidate;
- rescue label = 1 if flipping V5 was correct, 0 otherwise.

Require both:
- local rescue precision >= **0.60**
- one-sided 80% Wilson lower confidence bound for rescue precision > **0.50**

This makes specialist permission depend on nearby historical outcomes rather than global cluster utility.

## 7. Specialist arbitration

For each active specialist that passes:
- conformal support;
- local competence;

compute trust score:
`trust = WilsonLower80 * p_support`.

If more than one specialist passes:
- select the specialist with highest trust;
- ties: higher local precision, then higher p_support, then fixed order SB > OPT > MAT.

If no specialist passes:
- KEEP V5.

## 8. Online safety

Specialist-specific, not regime-specific.

For each selected specialist:
- at most one accepted unresolved H3 event at a time;
- matured accepted utility = +1 rescue, -1 broken;
- live specialist score starts at 0 at a scheduled refit boundary;
- if live specialist score becomes negative, that specialist is closed until the next scheduled refit.

Scheduled refit boundary:
- first eligible origin of each calendar month.

At monthly refit:
- all matured history is incorporated;
- support/competence libraries are refreshed;
- live specialist score resets to 0.

## 9. Historical development replay

Because the architecture was designed after seeing the prior 2026 holdout, all historical replay is explicitly **retrospective development evidence**.

Sequential blocks:
- 2024 H2
- 2025 H1
- 2025 H2
- 2026 H1
- 2026 H2 through available September history

Metrics:
- accepted candidates
- rescue / broken / net
- precision
- V5 vs assisted accuracy
- specialist identity
- conformal-support suppression
- competence suppression
- overlap/fuse suppression

No retrospective result changes the prospective frozen constants above.

## 10. Prospective success criterion

Beginning with the first eligible post-freeze origin:

Primary:
- cumulative net rescue > 0.

Promotion evidence is not considered sufficient until at least:
- **20 accepted prospective candidates**, or
- **6 calendar months**, whichever occurs later.

Interim safety:
- if cumulative prospective net rescue <= -3, SCR-RTE enters fail-closed shadow mode pending a separately governed review.

## 11. Governance

- Historical 2026 is development only from this point forward.
- No post-freeze prospective outcome may alter K=5 support distance, p_support=0.10, local K=15, 0.60 precision floor, Wilson-80 >0.50, monthly refit, or online fuse without creating a new version.
- HELIOS V5-DCE remains the binding production/champion forecast.
- SCR-RTE initially runs as a shadow challenger.
