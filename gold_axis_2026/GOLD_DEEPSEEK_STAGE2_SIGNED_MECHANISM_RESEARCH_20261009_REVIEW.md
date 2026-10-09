# DeepSeek independent scientific research exchange (unverified hypotheses)

This is untrusted external LLM output. NO market backtest has been run by DeepSeek; mathematical claims and literature must be checked separately. Not trading instructions, an audited model result, or a guaranteed improvement.

Model: deepseek-flash

Brief SHA256: 3cf68e393e7715eb94342b6461560ed56c0d3b5ebaf75487bf97cc6ece204888

## Stage2 independent candidate mechanism

**BLOCK.** With the source-audit posture you have specified, no new signed directional mechanism is defensible. I am not going to invent a sixth rebranding after eight measured failures. Below I state the strongest *conditional* mechanism that would be admissible, the exact audit gate, and why that gate currently fails.

## 1. The audit gate (must be cleared before any hypothesis exists)

The experiment is **blocked unless** the following four sources are independently verifiable, vintage-timestamped, and complete on the exact eligible origin dates:

- **(S1)** GC same-contract H1 bars with exchange-native timestamps and a documented roll map, no carry-forward, no resampling, no provider back-fill.
- **(S2)** A USD/FX or yield instrument with true event-time stamps and archival release vintages (not retroactive consensus or revised macro prints).
- **(S3)** XAU BID+ASK M15 with both sides, no midpoint synthesis from a single side.
- **(S4)** A written provenance file per source stating ingestion timestamp, revision history, and known gaps.

Your brief states S1 coverage is nonuniform and the five-root population was source-gated for missing bars. That alone is the failure. **Source existence is not PIT suitability.** Until S1–S3 pass an as-of audit on every candidate origin date, any equation I write is numerology.

## 2. Conditional mechanism (only if §1 clears) — signed cross-asset residual, not a trend

Define, on exact eligible origin *d*, using only data timestamped strictly before the issue cutoff:

- *r*_XAU(d) = log(mid(d, pre-cutoff) / mid(d−1, 17:00)) — own-path **control**, never a regressor of interest.
- *r*_GC(d) = log(GC(d, pre-cutoff) / GC(d−1, close)) — same contract, audited roll.
- *β* estimated **only on 2020–22** by OLS of *r*_XAU on *r*_GC over non-origin days.
- **Innovation:** *z*(d) = *r*_XAU(d) − *β̂* *r*_GC(d). This is the XAU move *not* explained by contemporaneous gold-futures repricing.
- **Signed endpoint:** *y*(d) = 1{close(d,17:00) > open(d,09:00)} for DAY; the OVN analogue with the 17:00→next09:00 interval, Fri→Mon separate.

Hypothesis to test: *z*(d) carries signed information about *y*(d) after conditioning on *r*_XAU(d) and on a calendar/macro-schedule dummy. Under the null, *z* is orthogonal to *y*.

This is **not** a rebrand of own-price trend (the own move is subtracted out), **not** calendar volatility (schedule is a control, not the signal), **not** a confidence gate, **not** a generic HGB/logit rerun (no tree, no learned gate; it is a single pre-registered residual coefficient). It also does not restate GC-minus-XAU signed gaps: that failed test used a *level gap*; this uses a *leadership residual* and is falsifiable within one parameter.

## 3. Fatal flaw in my own proposal

The most likely identification failure is **asynchronous clock alignment**. GC H1 bars and XAU M15 bars have different close times; the "pre-cutoff" boundary is not simultaneous. If GC's last pre-cutoff bar ends before XAU's, *z* embeds a stale futures print and *β̂* is biased. The second failure is **vintage contamination**: revised GC or FX prints will silently make *z* look informative. The third is **regime drift in β** — a 2020–22 fit applied to 2023–25 is exactly the transport error you have already measured repeatedly.

## 4. Null controls (mandatory, same eligible dates)

- **Price-only control:** *r*_XAU(d) alone, no cross-asset term.
- **Calendar-only control:** day-of-week, hour, DST flag, known macro-schedule dummy — no prices.
- **Placebo residual:** *z* computed from a *shifted, non-overlapping* GC window (e.g. yesterday's residual versus today's label). If placebo matches *z*, *z* is noise.
- **Sign-flip control:** −*z*. Both signs must be reported.

Reject the mechanism if any control matches or exceeds *z* on the same dates.

## 5. Sample and completeness, conceptually

For a signed binary endpoint you need enough *eligible, fully observed* origin dates per regime so the standard error of the signed rate is small relative to the effect under test. I will not give a number: the required N depends on the true effect, which you have not established. Conceptually, the binding constraint is **matched coverage**: every origin date must have complete S1, S2, S3 with no imputation. Partial-coverage dates are dropped, not filled. If dropping them leaves too few dates per year to separate regimes, the mechanism is untestable — another reason to block.

## 6. Falsification guardrails for false-DOWN alerts

Because your prior DOWN recall was the weakest link (roughly 10–14%), a signed mechanism that only fires UP is useless. Require, pre-registered:

- Report signed accuracy *and* DOWN recall separately.
- A DOWN alert must be defined by an explicit threshold on *z* fixed before seeing labels.
- If DOWN recall is not materially above the same-date base rate, the mechanism is falsified regardless of aggregate accuracy.

## 7. What is actually required

You need a **new data-quality artifact**, not a new equation: an audited, vintage-stamped, same-contract, complete-coverage cross-asset feed aligned to your exact M15 cutoffs, with a written provenance file. Absent that, state it plainly: **no signed novelty is defensible on current sources.** Do not conjure the source. Do not name a performance number. The honest scientific output of this brief is a block plus a precisely specified data-acquisition requirement.

## Stage2 hostile data/PIT/scientific referee

**HOSTILE REVIEW. Decision: REJECT the proposal as written; BLOCK execution on currently approved sources.**

You asked for a hostile reading. The prior proposal is not implementable on the audited corpus you actually hold. Below I attack each load-bearing claim.

## 1. Synchronization is asserted, not demonstrated

The proposal hinges on a "pre-cutoff" boundary being simultaneous across GC, SI, FX/yields, and XAU M15. It is not. Exchange-native GC/SI prints, FX spot convention, and yield vintages have different close conventions and revision schedules. Your own brief admits GC 1H coverage is nonuniform and five-root populations were source-gated for missing bars. A residual *z = r_XAU − β r_GC* built on two clocks that close at different instants is not a leadership measure; it is a timestamp artifact. **Fatal.**

## 2. Timestamp / horizon leakage

The OVN origin cutoff is 16:45; DAY is 08:45. GC H1 bars do not naturally terminate at those boundaries. If the last GC bar used overlaps the target window — even by minutes — the residual has already absorbed post-origin information. No amount of "we checked" substitutes for an as-of audit proving every feature timestamp is strictly before the issue moment. The proposal supplies no such proof. **Fatal.**

## 3. Roll artifacts contaminate β

Same-contract GC with a roll map is claimed. Roll splicing changes the return's variance and mean at each roll; *β* estimated 2020–22 will not transport across roll regimes. If the roll map is provider-inferred rather than exchange-native, the residual is a splice residual. **Fatal unless roll map is exchange-native and audited.**

## 4. PIT macro consensus is not historically perfect

The design conditions on a macro-schedule dummy and implicitly on release timing. Historical consensus and release vintages are revised. Using a current vendor's back-history is retroactive consensus — forbidden by your own brief. Without original PIT vintages, the macro control is contaminated. **Fatal for the macro-conditioned variant; survivable only for the schedule-only dummy.**

## 5. Sparse, gated samples

Every "eligible origin date" requires S1+S2+S3 complete. Your brief already shows coverage collapses under exactly this requirement. Dropping incomplete dates is correct; but it leaves samples too small to separate regimes, and the proposal gives no count. A sign test on tens of dates per year cannot distinguish *z* from noise. **Statistically underpowered.**

## 6. Endogeneity masquerading as price discovery

*r_XAU* and *r_GC* are two prices for the same underlying metal. Their correlation is mechanical contemporaneous co-movement, not independent leadership. Regressing XAU on GC and calling the residual "innovation" assumes GC leads; the opposite (XAU spot driving futures basis) is equally plausible and untested. The residual is endogenous by construction. **Conceptually unsound unless leadership direction is independently established.**

## 7. Class imbalance

DOWN is the minority and the failure mode you care about. A coefficient on *z* can be significant in aggregate while DOWN recall stays near base rate. The proposal reports sign accuracy; that is not enough. Without a pre-registered DOWN threshold and a base-rate benchmark, the mechanism is unfalsifiable on the endpoint that matters. **Inadequate.**

## 8. Multiple testing and burned holdouts

2025 and 2026 are already inspected. Any "test" on them is descriptive, not confirmatory. You have now proposed a sixth family after eight measured failures. The pre-registered coefficient is one parameter, but the *family* has been selected across many attempts; the effective multiplicity is large. Without a genuine lockbox, p-values are theater. **Disqualifying.**

## Minimal implementable negative control

The only control that survives your data constraints:

**Same-date placebo residual.** On each eligible origin *d*, compute *z_shift(d) = r_XAU(d) − β̂ · r_GC(d−δ)*, where *δ* is a shift larger than any plausible leadership horizon (e.g. one full session, non-overlapping), with *β̂* frozen from 2020–22. Compare signed accuracy of *z* versus *z_shift* on identical dates, identical labels, identical coverage filter.

If *z* does not beat *z_shift* by a margin pre-registered before labels are seen, the mechanism is noise. This control is cheap, uses only approved sources, and directly tests whether any "innovation" exists beyond mechanical co-movement.

## Exact early-stop FAIL criteria (pre-register before any look)

1. **Coverage fail:** eligible dates per regime-year < the minimum needed for a binomial sign test to reject the null at the pre-set α, given the observed control rate — stop.
2. **Synchronization fail:** any origin date lacking an as-of proof that all features precede the issue moment — drop that date; if dropped fraction exceeds a pre-set cap, stop.
3. **Control fail:** *z* does not exceed *z_shift* on signed accuracy by the pre-registered margin — stop, falsified.
4. **DOWN fail:** DOWN recall not clearly above same-date base rate — stop, falsified even if aggregate accuracy looks fine.
5. **Sign-flip fail:** −*z* performs comparably — stop, no directional content.
6. **Roll fail:** results change materially under any plausible roll-map alternative — stop, artifact.

Any single trigger ends the experiment. No post-hoc rescue, no reweighting, no gate.

## What genuinely prospective evidence would require

- An **untouched lockbox** with a stated unlock date, untouched by any prior inspection.
- **Vintage-stamped, exchange-native, same-contract** GC/SI plus FX/yield feeds with documented roll maps and revision histories.
- An explicit **leadership-direction test** (e.g. asymmetric lead-lag on non-overlapping windows) establishing that GC actually leads XAU before any residual is called "innovation."
- Enough complete-coverage dates per regime to power a DOWN-recall test, not just an aggregate sign test.

Absent all four, the honest output is a block.

## Final decision

**REJECT** the proposal. **BLOCK** execution on currently approved sources. No fabricated market gain is asserted or implied. The correct next step is a data-provenance artifact, not another equation.
