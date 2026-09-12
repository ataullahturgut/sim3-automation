# Gold Control V1.60 — Final Regime Selector Method Memo

**Frozen before scoring:** yes  
**Purpose:** final normal-day retrospective architecture experiment  
**Production authority:** none

## Why V1.60 exists

V1.51–V1.59 repeatedly showed that adding another global direction learner does not produce stable cross-regime evidence. The recurring failure was not merely model capacity: one-class success, regime flips, horizon dependence, unstable trust models and routing loss all appeared under stricter evaluation.

V1.60 therefore does **not** train another gold-direction model. It asks a narrower question: can the system decide, using only matured past evidence from the current market regime, whether either of the two already-frozen H20 RTQ experts is trustworthy enough to use?

## Frozen expert set

- `LEGACY_RTQ_R126`
- `DRIVER_RTQ_R126`

No other normal-day H20 direction expert may be added after scoring. Event-time and monthly engines are excluded because they have different targets and clocks.

## Causal regime state

At each origin, the regime is formed only from information observable at that origin:

1. Volatility: current `vol20` versus the median of the previous 126 origin-observable values.
2. Structural risk: current BOCPD reset fraction versus the prior-126 75th percentile, plus Emergency alert-onset/reversal state.
3. Role consensus: whether at least two nonzero signs among FAST, SLOW and Monthly Direction agree.

This yields a transparent regime key such as `VOL_HIGH|STRUCT_RISK|ROLE_MIXED`.

## Causal expert reliability

For each expert at current origin `t`, V1.60 looks only at prior rows from the **same regime** whose H20 outcomes have already matured (`j+20<=t`). The history is capped at 126 signals.

An expert is not eligible unless its same-regime matured history contains:

- at least 24 signals,
- at least 5 realized UP and 5 realized DOWN targets,
- at least 3 predicted UP and 3 predicted DOWN signals.

This explicitly prevents the V1.56/V1.59 one-class failure from being mistaken for skill.

Eligible reliability is the past same-regime balanced accuracy. The minimum is frozen at 0.55. If both experts are eligible and currently emit a signal, the expert with the higher causal reliability is selected. Exact ties go to the legacy RTQ benchmark. If neither qualifies, output is `NO_SIGNAL`.

## What V1.60 is forbidden to do

- no H1 reopening,
- no new direction classifier,
- no probability meta-model,
- no reversal direction flip,
- no equal voting of context engines,
- no feature search,
- no threshold sweep,
- no post-score repair,
- no production writes.

## Evaluation

Primary metrics remain coverage, selective accuracy, selective balanced accuracy, MCC and two-direction signal counts. The frozen gate requires improvement over the one-class 2025 legacy RTQ and preservation of the strong 2026 H20 behavior, with both directions represented.

2025 and 2026 are explicitly researcher-visible retrospective diagnostics. Even a gate pass is not prospective proof and cannot authorize production. Future prospective shadow evidence remains mandatory.

## Thesis interpretation

V1.60 is a stopping-rule experiment. If it passes, the thesis has evidence for regime-conditioned selective expert use. If it fails, the thesis closes the normal-day retrospective search with the conclusion that H20 directional skill is not sufficiently stable for promotion under the frozen evidence rules, while event-time and monthly specialist lanes remain separate findings.
