# IFBC-H3 V1 — INTRADAY FLOW BREAKDOWN CONSENSUS

**Date:** 2026-10-04  
**Identity:** `IFBC_H3_V1`  
**Branch:** `gold-h3-ifbc-v1-20261004`  
**Evidence class:** retrospective development; first clean evidence must be prospective.

## 1. Origin of the hypothesis

VAST-H3 V1 failed as a multivariate logistic reversal model.

However, its block-by-block anatomy showed six microstructure variables with the same reversal direction in every scored block (2025 H2, 2026 H1, 2026 H2):

1. higher Gold opposite-direction volume share over 12h;
2. lower momentum-signed Gold flow over 12h;
3. lower momentum-signed Silver flow over 12h;
4. higher joint Gold/Silver opposition share over 12h;
5. higher Gold-minus-Silver signed-flow gap over 12h;
6. lower Gold 12h path efficiency.

IFBC tests whether a rank-based consensus across only these sign-stable mechanisms is more transportable than a fitted multivariate classifier.

All historical 2026 outcomes are development data; no clean historical holdout claim is possible.

## 2. Inputs

Reuse origin-safe VAST V1 origin features.

Define reversal-oriented raw variables:

- `x1 = gc_opp_vol_share_12`
- `x2 = -gc_flow_12`
- `x3 = -si_flow_12`
- `x4 = joint_opposition_share12`
- `x5 = gc_si_flow_gap12`
- `x6 = 1 - gc_efficiency_12`

No additional feature may be introduced in V1.

## 3. Origin-safe empirical ranks

For every origin and every xi:

- calibration set = previous **120** eligible origins;
- minimum calibration size = **60**;
- only origins with `feature_cutoff_date < current feature_cutoff_date`;
- target outcomes are not used in rank calibration.

Empirical percentile:
`rank_i = (1 + count(hist_xi <= current_xi)) / (n + 1)`.

This adapts thresholds to changing scale/regime without fitting outcome-conditioned coefficients.

## 4. Consensus score

- `IFBC_score = median(rank_1 ... rank_6)`
- `IFBC_count60 = count(rank_i >= 0.60)`

Candidate requires:
- `IFBC_count60 >= 4`
- `IFBC_score >= q`

Frozen q grid:
`[0.65, 0.70, 0.75, 0.80]`

No learned model is used.

## 5. Target and action

Universe:
- V5 follows 12h momentum.

Target:
- `rescue_target = 1[V5 wrong]`.

Candidate action:
- flip V5.

## 6. Historical development robustness

Scored blocks:
- 2025 H2
- 2026 H1
- 2026 H2 through available September history.

A q is development-eligible if:
- total candidates >=10
- net rescue >0
- precision >=0.55
- at least 2 of 3 blocks have net rescue >0
- no block net < -2.

Selection:
1. maximum net rescue
2. higher precision
3. more rescued
4. fewer candidates
5. higher q.

No eligible threshold => `NO_ELIGIBLE_IFBC_V1_MECHANISM`.

## 7. Prospective freeze

A historical pass is development evidence only.

If a q passes:
- freeze the selected q before post-freeze use;
- run IFBC as a shadow challenger;
- production use requires authoritative hourly GC/SI volume data.

Promotion evidence requires at least:
- 20 prospective accepted candidates;
- 6 calendar months;
- cumulative net rescue >0;
- precision >=0.60.

## 8. Governance

- Historical 2026 is development only.
- No post-result feature additions or sign changes under V1.
- Rank calibration never uses target outcomes.
- HELIOS V5-DCE remains binding champion.
