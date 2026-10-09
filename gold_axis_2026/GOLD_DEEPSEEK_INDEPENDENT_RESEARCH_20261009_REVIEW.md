# DeepSeek independent scientific research exchange (unverified hypotheses)

This is untrusted external LLM output. NO market backtest has been run by DeepSeek; mathematical claims and literature must be checked separately. Not trading instructions, an audited model result, or a guaranteed improvement.

Model: deepseek-flash

Brief SHA256: bd889cfa8f7cbd1494bd22dd55ad784ec939f223a885fc7464a0761c53dad98b

## Independent Round 1: Three candidate architectures

# Three New Scientific Architectures for XAU/USD DAY/OVN Signed Direction

**Constraint reminder:** everything below is a hypothesis with a falsifiable test, not demonstrated evidence. No fabricated citations. 2026 is already-inspected stress only; any "confirmatory" claim requires prospectively frozen later dates.

---

## Approach A — Pre-Opening Quote-Repair Hazard (PQRH)

**Signed information hypothesis.** The 2026 DOWN-recall collapse is caused less by regime shift than by *state contamination*: stale/carry-forward candles near 00:00–01:00 TRT (416 quarantined 2026 stale M15 candles) corrupt the pre-09:00 micro-state estimate, so the model sees a "flat" tape where the true last-quoted displacement already encodes directional pressure. The signed signal is the **sign** of the last quarantined-or-repaired price displacement relative to its own prior-21-session distribution, *conditional* on whether the overnight path reached the first barrier before staleness began.

**PIT observables (strictly before origin).** At 08:55 TRT: (i) last *valid* quote timestamp and price (stale flag = zero-motion run ≥2 bars); (ii) repaired last-valid displacement \(d = \log(P_{\text{last valid}}/P_{17:00\,\text{prev}})\); (iii) prior-21 matured realized displacement dispersion \(\sigma_{21}\); (iv) time since last valid quote \(\tau\).

**Mathematical structure.** Define repaired z-score \(z_A = d/\sigma_{21}\). Signed probability:
\[
\pi_A^{DAY} = \Phi\!\left(\alpha_0 + \alpha_1 z_A + \alpha_2 \mathbf{1}[\tau>\tau_0]\cdot \text{sign}(d)\right)
\]
No HGB/logistic main head; a small parametric sign-hazard. OVN uses the same at 16:55 with \(d\) measured from 09:00.

**Prediction/target issued.** Signed direction only (UP/DOWN), with abstention when \(|\pi_A-0.5|<\epsilon\). Target: sign of 09→17 and 17→next09 return.

**Training cutoff / label maturity.** Train on 2023–24 only, freeze parameters through 2025/2026. Labels mature at 17:00 (DAY) and next 09:00 (OVN).

**Negative controls.** (i) Same \(z_A\) computed with staleness *ignored*; (ii) shuffled stale flags preserving marginal rate; (iii) matched-date frozen 2026 CBR/HGB decisions. Falsification: if repaired-\(z_A\) balanced accuracy ≤ unrepaired on the same dates with overlapping CIs, hypothesis dies.

**Cross-year plan.** 2023/24 DEV → 2025 retrospective → 2026 stress (inspected). Prospective freeze on later dates only.

**Failure modes.** Stale flags not deterministic across sources; repair may reintroduce look-ahead if last-valid timestamp is late. Missing macro-calendar overlay could dominate.

**Data.** Available: M15 quotes with staleness flags (audit required). Not known available: true last-trade at 08:55 across all sources.

**Minimal decisive experiment.** Same-date paired McNemar on repaired vs unrepaired \(z_A\) signed decisions in 2025 and 2026 mirror, with 95% CI on ΔDOWN recall.

---

## Approach B — Macro-Release Hazard Interaction in Event Time (MRHIE)

**Signed information hypothesis.** Signed DOWN misses cluster around ex-ante *macro calendar hazard windows* (known advance schedule) interacting with overnight duration, not around volatility alone. This is a marked point-process view: the *hazard of a signed barrier crossing* depends on (release-type, time-to-release, prior displacement sign).

**PIT observables.** At 16:55 (OVN) / 08:55 (DAY): (i) forward-looking release schedule from official advance calendars (release type, scheduled time, known 2026 vintage — never post-release surprise); (ii) prior-session realized downward/upward move asymmetry; (iii) session duration to next origin (excludes Fri→Mon).

**Mathematical structure.** Competing-risks hazard with two marks:
\[
\lambda_\pm(t\mid \mathcal{F}_t) = \lambda_0(t)\exp\!\big(\beta_\pm X^{\text{cal}}_t + \gamma_\pm z_{\text{disp}}\big)
\]
Signed probability of DOWN = \(\int \lambda_-(t)S(t)\,dt\). Predict \(\text{sign}(\hat\mu_- - \hat\mu_+)\). Parameters estimated by partial likelihood, causal, per origin.

**Prediction/target.** Signed direction + selective coverage (release-day vs non-release-day stratification).

**Training/label maturity.** Train 2023–24; freeze; 2025 retrospective; 2026 stress. Labels mature exactly at window close.

**Negative controls.** (i) Hazard with calendar features removed (pure duration); (ii) calendar features randomized within same week; (iii) frozen CBR at exact 2026 dates.

**Failure modes.** Release schedules revised; DST shifts misalign windows; small N per release type. If signed accuracy equals duration-only baseline, calendar interaction is rejected.

**Data.** Available: official advance calendars (auditable). Not known: whether all release times archive pre-origin for 2023–24.

**Minimal decisive experiment.** Stratified same-date test: does \(\Delta\)DOWN recall from calendar features exceed 0 with 95% CI in 2025 and 2026 mirror?

---

## Approach C — Opportunity-Cost Asymmetric Game Against a Reference Policy (OCAG)

**Signed information hypothesis.** Signed information is not in price but in the *asymmetry between violating a no-trade reference policy and following it*. If the pre-origin cost-adjusted expected loss of a DOWN is systematically higher than the UP loss under a frozen reference policy, DOWN direction can be predicted from the *policy-differential*, not the price.

**PIT observables.** Before origin: (i) reference policy's current position and its pre-committed next action; (ii) estimated BID/ASK proxy spread from last M15; (iii) prior-21 session loss asymmetry for UP vs DOWN under the policy.

**Mathematical structure.** Let \(\mathcal{P}\) be a frozen non-directional reference (e.g., always-UP). Define pre-origin expected cost differential:
\[
\Delta C = \mathbb{E}[L_{\text{DOWN}}\mid \mathcal{F}_t] - \mathbb{E}[L_{\text{UP}}\mid \mathcal{F}_t]
\]
Predict DOWN iff \(\Delta C > \kappa\). \(\Delta C\) is estimated from past-only loss functionals. It is signed because losses are asymmetric under the policy and spread.

**Prediction/target.** Signed direction; explicit abstention when \(|\Delta C|<\kappa\). Coverage reported honestly.

**Training/label maturity.** 2023–24 fit of loss functionals only; frozen 2025/2026.

**Negative controls.** (i) Replace \(\Delta C\) with random sign preserving coverage; (ii) symmetric-loss control (should collapse to coin-flip); (iii) matched CBR/HGB dates.

**Failure modes.** Loss functionals strongly coupled to reference policy choice; spread proxy unreliable; risk of relabeling old consensus if reference is poorly chosen.

**Data.** Available: M15 quotes for spread proxy. Not known: true BID/ASK for 2023–24.

**Minimal decisive experiment.** Same-date paired test of \(\Delta C\)-sign vs symmetric-loss control on 2025 + 2026 mirror, reporting BA, DOWN recall, and coverage with CIs.

---

## Ranking by Credible Incremental Signed Information (not accuracy)

1. **A (PQRH)** — highest feasibility; directly addresses a documented contamination channel; small parameter count; clear negative control. Weakness: staleness flag audit needed.
2. **B (MRHIE)** — strong economic prior; medium feasibility; needs calendar archive audit; small-N per release.
3. **C (OCAG)** — most novel; highest risk of relabeling; depends on reference-policy choice; feasibility medium-low.

All three preserve the existing magnitude head unchanged. None may claim superiority until same-date paired advantage with confidence bounds is shown on prospectively frozen later dates. The established 2026 DOWN-recall failure is treated as a symptom to be explained, not as evidence any of these works.

## Independent Round 2: Hostile scientific referee / minimum experiment

# Hostile Referee Report on PQRH, MRHIE, OCAG

I act as an adversarial methodological referee against my own proposals. I do not assume the brief's aggregates are sufficient for any claim of signed skill.

## Technical weaknesses

**A — PQRH.** Signal novelty is modest: repaired z-score is a sign-of-displacement statistic, which is a *rebranded* price-momentum feature. The brief explicitly warns that naive price-only baselines matched or beat NQ/ZN/CL-enhanced RFR analogues (2026 mirror K25 BA 58.76 vs baseline 60.33). PQRH's only genuine novelties are (i) a stale-run indicator and (ii) conditional interaction with last-valid time. Neither is demonstrated to carry *signed* information — the brief already shows quarantine changed observed RV but not signed probabilities. So the hypothesis may collapse to relabeled displacement. Worse: the last-valid quote may be hours before origin on thin sessions, which injects timing leakage risk if the repair pulls the price forward. The sign-hazard form also ignores the documented **volatility-scale shift** (median barrier 0.54565% → 1.34465%) — a fixed \(\epsilon\) abstention and fixed \(\sigma_{21}\) become miscalibrated precisely in 2026, the year of interest.

**B — MRHIE.** This is the most vulnerable to hidden data provenance. I asserted "forward-looking release schedules (official advance calendars)" are PIT-available, but the brief states the opposite kind of warning: **"Source-vintage QC mandatory"** and **"no retroactively reconstructed consensus."** Advance calendars are public, but the *content* of what the market expected (consensus) is not in scope, and without consensus the hazard marks collapse to a dummy for "release scheduled." A calendar dummy interacting with duration is essentially a **session-time feature**, not a new signed signal. Small-N per release type is fatal: with ~200 OVN nights/year and maybe 3–5 relevant release types, cell counts are in the low tens; DOWN recall CIs will swamp any point estimate. This is a *design* weakness, not a tuning issue.

**C — OCAG.** The reference policy \(\mathcal{P}\) is arbitrary. If \(\mathcal{P}\) is always-UP, \(\Delta C\) is a signed transform of expected UP/DOWN loss under a specific loss — which is the definition of a directional proxy. The "game-theoretic" framing does not add independent information; it adds a relabeling of an asymmetric-loss classifier. The spread proxy from last M15 is not actual BID/ASK, so the loss functional is misspecified; a mismatched loss flips signs non-monotonically. This risks reproducing the PRAMV pathology: selection reliability inversion (2026 accepted 31/130 at BA 48.32, rejected 62.07% — the worse cohort was accepted).

## Missing cross-market observations

All three approaches are single-asset in essence. The brief documents GC/SI 1h jointly missing at origin and forbids assuming Gold futures M15 availability. Without a **cross-market signed anchor** (e.g., real yields, DXY, or funding-market state) the "independent signed information" claim reduces to a within-price transformation. That is not independent — it is an *inference from the same tape* the target is drawn from. A referee should treat PQRH, MRHIE, OCAG as **derived features of the target's own source**, not independent signed factors.

## US macro first-print and consensus availability

The brief is explicit: official release timestamp and advance schedule are OK; post-release surprises are not; retroactively reconstructed consensus is not assumed public. This kills MRHIE's strongest version. Any appeal to "expected" macro state requires a PIT consensus archive that the brief does not certify as available. I must therefore strike MRHIE's information-theoretic claim and demote it to a calendar-dummy ablation.

## Statistical selection bias and DOWN false alarms

- **Multiple testing.** Three architectures × multiple controls × cross-year windows is a large researcher-degrees-of-freedom surface. Without pre-registration of the precise metric, any "improvement" is selection-biased.
- **Down-recall metric gaming.** Optimizing DOWN recall invites false DOWN alarms. The brief already flags the magnitude head enriching severe-DOWN at 0.73× (worse). A new signed head could mimic this by over-firing DOWN. Any candidate must report **precision at fixed DOWN-recall**, not recall alone.
- **Base-rate drift.** 2026 first-passage event rates 95.28% raw vs 44.88% ex-ante-scaled show the label distribution is volatility-confounded. Signed direction training on raw labels inherits this confound.

## Why this is not a boosted/logistic rerun

Only PQRH is *arguably* not a GLM/GBM rerun, and only if the stale-flag interaction is genuinely exogenous. MRHIE reduces to a calendar dummy; OCAG reduces to a loss-weighted linear score. Neither survives the referee's novelty test.

## Ranking by credible incremental *signed* edge

1. **PQRH** — the only candidate with a potentially exogenous, pre-origin observable (staleness flag) not already in the frozen models. Modest but nonzero novelty.
2. **OCAG** — signed by construction but policy-dependent; novelty mostly rhetorical.
3. **MRHIE** — strongest *a priori* story, weakest *PIT* implementation; likely collapses to a time-dummy ablation.

## One feasible minimum decisive historical experiment

**Name:** PQRH same-date paired test.

**Inputs, all known before 17:00 TRT:**
- `t_last_valid` — timestamp of last non-stale M15 close before 16:55.
- `P_last_valid` — its close.
- `P_0900_prev` — prior 09:00 close.
- `stale_run_len` — consecutive zero-motion M15 bars immediately before 16:55.
- `sigma21` — prior-21 matured OVN RMS log-vol, strictly ex-ante.
- `frozen_CBR_decision` — archived 17:00 decision on same date.
- `signed_return_target` — sign of 17:00→next09 (label, matured later).

**Model:** two-parameter sign-hazard, parameters fit only on 2023–24, frozen thereafter.

**Pass conditions (all must hold):**
1. On 2025 and 2026-mirror same dates, paired McNemar for PQRH vs *unrepaired* z-score rejects null at α=0.05 favoring PQRH.
2. ΔDOWN recall ≥ +5 percentage points with 95% CI lower bound > 0.
3. ΔDOWN precision not worse than −2 pp (false-DOWN alarm guardrail).
4. Balanced accuracy strictly greater than frozen CBR on identical dates.
5. Stale-flag-shuffle control degrades ΔBA by ≥ 50% of the observed gain.

**Fail conditions:** any of 1–5 violated, or abstention coverage < 20% (insufficient actionable nights).

## The LLM limitation, stated plainly

An LLM cannot prove forecast skill. Skill claims require (i) frozen code, (ii) frozen PIT inputs, (iii) matured labels, (iv) paired same-date evaluation with CIs, (v) out-of-sample holdout *not already inspected*. This report produces none of these. The brief's aggregates are second-hand summaries; the LLM cannot verify their underlying bars, cannot check staleness flags, cannot reproduce McNemar counts, and cannot estimate coverage-dependent variance. Any narrative "edge" here is a hypothesis template, not evidence. I must therefore treat all three architectures as *unproven*.

## Binding source-gate requirement

If the following are not obtainable before 16:55 TRT with archival proof: (a) per-bar staleness/missing-print flags, (b) `t_last_valid` as an explicit field, (c) an audited 2023–24 OVN series without 60-vs-64 candle artifacts at the decision boundary — then PQRH is not even *evaluable*, and no signed architecture above can be tested. Absent that gate, the honest position is that the 2026 DOWN-recall breakdown remains **unexplained by any of these designs**, and the binding blocker is source-integrity, not model class.

## Conclusion

Ranked by credible incremental *signed* edge: **PQRH > OCAG > MRHIE**. Only PQRH has a plausibly exogenous pre-17 observable. MRHIE depends on consensus timing the brief does not certify; OCAG is a loss-weighted relabeling. The single feasible minimum decisive historical experiment is the PQRH same-date paired McNemar with the pass/fail block above. If the source-gate conditions are unmet, no LLM-authored architecture — including mine — can establish improved signed skill, and the correct scientific action is to state that binding data requirement rather than to propose further models.
