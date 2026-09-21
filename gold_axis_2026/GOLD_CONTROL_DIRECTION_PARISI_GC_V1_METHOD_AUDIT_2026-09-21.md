# GOLD CONTROL — PARISI ROLLING-WARD GC_V1 METHOD AUDIT

**Date:** 2026-09-21  
**Trigger:** user challenged whether the 2025 Parisi test was truly faithful to the published method.  
**Audit status:** `PRIOR_GC_V1_RESULT_RETAINED_AS_DIAGNOSTIC_ONLY / PARISI_SOURCE_METHOD_NOT_YET_FAITHFULLY_TESTED`

## 1. Primary-source facts rechecked

Primary authority: Parisi, A., Parisi, F. & Díaz, D. (2008), *Forecasting gold price changes: Rolling and recursive neural network models*, Journal of Multinational Financial Management 18(5):477–487, DOI 10.1016/j.mulfin.2007.12.002.

Primary/source-supported facts recovered:
- weekly gold-price change / first difference is the target;
- one-step-ahead direction;
- inputs are four lags of Gold first differences plus four lags of DJIA first differences;
- rolling and recursive neural networks are compared;
- network weights are recalculated period-by-period;
- the paper explicitly reports that a Ward network with **2 hidden layers and 21 neurons** reached the best activation/scaling combination and 57.94% sign hits at the architecture-selection stage;
- the rolling Ward family is reported as the strongest overall dynamic approach;
- block-bootstrap validation reports average sign prediction 60.68% with sd 2.82%.

## 2. Material mismatches in GC_V1

The executed `DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH` was explicitly an adaptation, but the post-run interpretation was too strong. The following differences are material enough that GC_V1 cannot be used to judge the published Parisi method itself:

### A. Architecture mismatch

Published gold-paper architecture:
- Ward network;
- **2 hidden layers**;
- **21 neurons**;
- best combination of activation and scaling functions selected in the paper.

GC_V1:
- one 21-neuron hidden bank;
- 7 Gaussian + 7 Gaussian-complement + 7 tanh units;
- logistic output.

Therefore GC_V1 did **not** reproduce the published two-hidden-layer Ward architecture.

### B. Activation/scaling substitution

GC_V1 borrowed Gaussian / Gaussian-complement / tanh Ward slabs from a different 2006 paper by the same authors. That related paper used an explicit **three-hidden-layer 5/5/5 Ward architecture**, not the 2008 gold paper's two-hidden-layer / 21-neuron winning architecture.

Using the related paper was defensible for an adaptation, but it is not proof of the exact 2008 gold-network implementation.

### C. Rolling-sample-size substitution

The 2008 paper explicitly studies different sample sizes.

GC_V1 invented a small frozen candidate set `{50,75,100}` because the exact gold-paper sample-size grid was not recovered.

That is a project adaptation, not a reproduction of the paper's rolling design.

### D. Training algorithm substitution

The proprietary learning-rate / stopping / initialization details of the 2008 gold paper were not recovered.

GC_V1 used:
- full-batch Adam;
- lr=0.01;
- max 2000 epochs;
- patience 200;
- deterministic seeds.

These choices are not source-proven.

### E. Data-history choice was unnecessarily short

GC_V1 used `XAU_NY17_HOURLY_DERIVED_DAILY_RESEARCH_V1`, yielding only:
- 201 weekly rows total;
- 143 pre-2025 eligible samples.

The project already holds a much longer research-only daily XAU history and DJIA history sufficient to construct roughly 2016–2025 common weekly observations. Earlier read-only audit showed about 488 common XAU/DJIA weeks and 431 eligible pre-2025 four-lag origins using the long-history XAU research surface.

Using the shorter 2022–2025 source was conservative for clock semantics, but it materially reduced the training sample for a 21-neuron neural network and was not required by the original Parisi method.

## 3. What was correct in GC_V1

The execution was not a chronology bug:
- target/features were lagged correctly;
- each forecast used only prior observations;
- rolling retraining was period-by-period;
- 2025 did not select the window/config;
- no random split;
- 2025 was scored only after the pre-2025 config was frozen;
- no database/forecast-ledger/decision-store writes.

Thus the numerical 2025 output is valid **for GC_V1 as implemented**, but not as a faithful test of the published Parisi model.

## 4. Corrected interpretation

Do NOT state:
> "Parisi (2008) failed on 2025 Gold Control data."

Correct statement:
> "The first transparent GC_V1 adaptation of the Parisi signal family failed to show 2025 direction edge, but the published Parisi rolling-Ward architecture has not yet been faithfully replicated because material network/sample/training details differ."

Binding status:
- `DIRECTION_PARISI_ROLLING_WARD_GC_V1_RESEARCH = DIAGNOSTIC_ONLY / NO_PROMOTION_FOR_GC_V1 / NOT_SOURCE_FAITHFUL_ENOUGH_TO_JUDGE_PARISI`
- `DIRECTION_PARISI_ROLLING_WARD_V1_RESEARCH = SOURCE_METHOD_REOPENED / EXACT_REPLICATION_NOT_YET_PROVEN / 2025_FAITHFUL_TEST_PENDING`

## 5. Required next step before another 2025 run

Before opening a corrected Parisi V2:
1. obtain the complete 2008 paper/full method text, preferably the author-uploaded full PDF;
2. recover the exact two-hidden-layer / 21-neuron allocation;
3. recover the exact winning activation functions and scaling functions;
4. recover the exact rolling sample-size grid / selected window rule;
5. recover training/stopping/initialization details if stated;
6. recover the original weekly gold-price source/observation convention;
7. freeze a new pre-2025 identity before re-running 2025.

If one or more details remain unavailable, any V2 must again be labelled an adaptation, and differences must be explicit before scoring.
