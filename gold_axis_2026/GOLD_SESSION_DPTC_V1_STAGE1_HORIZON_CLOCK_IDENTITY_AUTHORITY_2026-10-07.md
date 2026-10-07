# GOLD SESSION — DPTC V1 STAGE-1 HORIZON / CLOCK / IDENTITY AUTHORITY

**Date:** 2026-10-07  
**Status:** **PARTIAL PASS / FULL DPTC BLOCKED BY SESSION-NATIVE SELLR IDENTITY**

## 1. Historical identity audited

Historical DPTC H3 V1 combines four distinct mechanisms:

1. canonical Handoff alarm;
2. label-free dependence-phase gate;
3. SELLR catalyst for TRUST entry;
4. hysteretic TRUST persistence, exiting after two consecutive matured acted BROKEN outcomes.

Historical H3 DPTC was explicitly a post-hoc development challenger. Its 2026 result is not independent validation.

## 2. SESSION portability verdict by component

### A. Handoff alarm — PASS

The canonical Handoff concept can be rebuilt at exact SESSION origin using the already-audited BOCPD/Handoff raw-source chain.

Required SESSION rules:
- origin = exact session `start_utc`;
- every intraday source input must be known before that origin;
- no target-window input;
- Handoff state independent by partition/window.

The old H3 Handoff timeline must not be consumed directly.

### B. Dependence phase — CONDITIONAL PASS

The dependence-phase mechanism is label-free and conceptually horizon-independent:

- rolling Gold/Nasdaq daily-return correlation;
- rolling Gold/VIX daily-return correlation;
- strong-pro-risk topology;
- persistence run length;
- correlation-vector shift.

However, the historical implementation is indexed by one H3/daily origin per date. In SESSION the topology process must remain a **daily state process**, not a per-session event process.

Binding SESSION mapping:
- daily market state is calculated once per NY calendar date;
- only observations whose daily availability is safe before a session start may be used;
- absent proven intraday publication timing, use the last completed prior NY calendar day;
- attach the latest safe daily topology state to each session;
- do **not** increment `strong_run` multiple times merely because several session windows occur on the same date.

Historical threshold values (run q95/q99 and shift q95) may be reused only after exact raw-source reproduction proves that the same daily state process is being reconstructed. If reproduction fails, thresholds must be recalibrated only on pre-2025 development data under a new SESSION-specific identity.

### C. SELLR catalyst — FAIL / HARD BLOCKER

Historical DPTC uses:
- `sellr_score >= 2.3677413378977423`;
- historical baseline must follow historical momentum;
- threshold was selected on H3 2025 before H3 2026 stress.

Current repository evidence contains the imported artifact:

`GOLD_H3_COMPETENCE_TRANSITION_V1_SELLR_SCORES_SOURCE_2026-10-05.csv`

with columns including:
- H3 `y_up`;
- H3 `momentum_up`;
- H3 `baseline_pred`;
- H3 `reversal_target`;
- `sellr_score`.

No canonical raw-source SESSION-capable SELLR producer/formula is present in the audited repository lineage.

Therefore:
- the imported H3 SELLR scores are **forbidden SESSION inputs**;
- the numeric H3 threshold **2.3677413378977423 must not be applied to a newly invented SESSION score** without identity/scale proof;
- full DPTC V1 cannot be run honestly on SESSION targets at this stage.

This is a **target/horizon identity blocker**, not merely missing data.

### D. TRUST hysteresis — PASS

The persistence rule is event-based and can be mapped safely:

- TRUST state independent for each partition/window;
- current session decision is made before current outcome is known;
- only previously acted outcomes with `end_utc <= current start_utc` mature;
- RESCUE resets broken streak to 0;
- BROKEN increments broken streak;
- exit TRUST after 2 consecutive matured acted BROKEN outcomes.

This rule does not require H3 target duration and is portable once a valid SESSION TRUST-entry catalyst exists.

## 3. Baseline identity

Historical DPTC baseline was:

`HELIOS V5-DCE + SAGE/OCS exception-only + RuleFlow V3-TG`.

That baseline is not valid for the current SESSION project:
- SESSION HELIOS is complete but not promoted;
- historical H3 RuleFlow/OCS outputs are not SESSION authorities;
- the current session project has window-specific frozen balanced bases.

Therefore historical combined H3 baseline outputs must not be used.

Any SESSION DPTC successor must act on a preregistered SESSION baseline, currently the same development-frozen per-window balanced base family used for BOCPD unless a later governance document changes that before results are opened.

## 4. What is safe to preserve

Safe algorithmic lineage:
- Handoff concept;
- label-free dependence topology concept;
- Q95/Q99 reporting as named sensitivity identities **only if daily-state threshold reproduction passes**;
- SELLR as the abstract idea of a structural TRUST-entry catalyst;
- two-consecutive-matured-BROKEN TRUST exit.

Unsafe direct reuse:
- H3 Handoff timeline CSV;
- H3 dependence panel as session state;
- imported H3 SELLR score CSV;
- H3 SELLR numeric threshold on an unverified SESSION score;
- H3 combined baseline predictions;
- H3 target-end dates or H3 competence labels.

## 5. Stage-1 verdict

| Component | Verdict |
|---|---|
| SESSION target identity | PASS requirement defined |
| Handoff reconstruction | PASS |
| Dependence topology concept | CONDITIONAL PASS |
| Daily-state/session attachment rule | PASS |
| Q95/Q99 threshold reuse | CONDITIONAL on exact reproduction |
| TRUST hysteresis | PASS |
| Historical H3 combined baseline reuse | FAIL / prohibited |
| Historical H3 SELLR score reuse | FAIL / prohibited |
| SESSION-native SELLR producer | **MISSING / HARD BLOCKER** |
| Full DPTC SESSION replay readiness | **FAIL / BLOCKED** |

## 6. Correct next action

Do **not** run DPTC Stage-2 yet.

Next action is a narrow **DPTC Stage-1B SELLR lineage/reconstruction task**:

1. recover or reconstruct the original SELLR scoring formula and raw feature lineage;
2. determine whether the score itself is horizon-independent or contains H3 target-trained components;
3. if horizon-independent, rebuild it at exact SESSION origins and prove numerical/source equivalence on historical overlapping dates before any SESSION test;
4. if horizon-dependent, define a new preregistered SESSION-SELLR successor using only 2022 warm-up + 2023–2024 development; the old H3 threshold cannot be reused;
5. only after a valid SESSION catalyst exists may full DPTC Stage-2 be preregistered and run.

## 7. Governance

2025 must remain closed during SELLR reconstruction and SESSION DPTC Stage-2 design.

No 2025/2026 SESSION outcome may be used to choose:
- SELLR features;
- SELLR threshold;
- Q95 versus Q99;
- TRUST exit rule;
- baseline membership.

## Historical authorities

- `GOLD_H3_DPTC_V1_DEVELOPMENT_FREEZE_2026-10-05.md`
- `GOLD_H3_DPTC_V1_RESULT_2026-10-05.md`
- `GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_PREREG_2026-10-05.md`
- `GOLD_H3_DEPENDENCE_PHASE_SHIFT_V1_RESULT_2026-10-05.md`
- `GOLD_H3_COMPETENCE_TRANSITION_PROGRAM_V1_PREREG_2026-10-05.md`
- `GOLD_H3_COMPETENCE_TRANSITION_PROGRAM_V1_RESULT_2026-10-05.md`
- `GOLD_H3_DPTC_2023_2024_DATABENTO_SOURCE_ROBUST_REPLAY_2026-10-05.md`
- `GOLD_SESSION_HORIZON_CLOCK_MATURITY_AUDIT_2026-10-07.md`
