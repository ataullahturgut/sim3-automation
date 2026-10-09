# DeepSeek independent technical critique of author-pre-registered ZN volume hypothesis

**External LLM text, not market evidence.**

**REFEREE REPORT — JDR4, XAU 15m, DAY horizon**

**Verdict: REJECT_NOW as established detection. Not even KEEP_AS_PROSPECTIVE_CANDIDATE is warranted in the current form.** The prospective arm, if the authors insist, must be re-registered as a *new, differently specified* hypothesis with source-verifiable 5m/tick data, a locked date, and deterministic gating rules — i.e., not a continuation of JDR4.

**(1) JDR4 is not gold jump detection at 15m.**
A 15m sampled midpoint cannot resolve a jump. A single 15m squared return dominating 50% of the prior 4h sum of squares is mathematically indistinguishable from a volatility burst, an illiquid quote, a stale or crossed-quote correction, a rollover/thin-book print, or a news-triggered micro-rupture aggregated across the interval. Bajgrowicz et al. (2016, Mgmt Sci, 10.1287/mnsc.2015.2234) show exactly this failure mode: false jump detections are the default at coarse sampling; "jump" requires finer resolution and continuity tests, not a share-of-sum-of-squares threshold. No signed orderflow, no cross-venue confirmation, no realized-jump trio (Lee–Mykland or Andersen–Bollerslev–Diebold), no Barndorff-Nielsen–Shephard bipower separation is offered. The label "JDR4" is therefore a misnomer: it is a *dominant-interval-reversal*, not a jump.

**Concrete 5m native falsification.** Using the same upstream source and the same Istanbul 17:00→09:00 / 09:00→17:00 windows, resample at native 5m. Define a *confirmed* jump as: a 5m return whose standardized magnitude exceeds the BNS bipower threshold at the same instants, with the numerator interval's squared return still ≥50% of the prior-4h sum of squares *and* at least one contiguous 5m sub-interval carrying ≥60% of that interval's variance. Reject the "jump" label if ≥2 of the sub-intervals contribute roughly equally (volatility burst). Then re-run JDR4 on 5m-confirmed jumps only. If sign-reversal skill vanishes once confirmation is imposed, JDR4 is a volatility-burst artifact, not jump detection.

**(2) Why naive month-block CIs and pooled McNemar are invalid.**
Both are nominal. They condition on a model that was *selected* after inspecting 2023–2026 outcomes across a 3×2 family plus prior attempts. The correct reference distribution is the maximum of the family under the null (White 2000, Econometrica, 10.1111/1468-0262.00152), not the single-threshold chi-square. Bonferroni over 3 hypotheses × 2 horizons × previously tried models already moves p≈.045 to non-significance; the true family-wise null is larger still. Pooled McNemar 50/31 and 59/35 violates the exchangeability assumption because 2025 and 2026 outcomes were already inspected — they are not independent draws. Month-block bootstrap with unequal 2026 months also inflates effective N. These numbers cannot confirm novelty.

**(3) 43% single-day share.**
If one calendar day supplies 43% of the favorable gross delta (top two = 63%), then the claimed ``incremental skill'' is a heavy-tail event. Under a plausible null with stable µ and fat-tailed daily contributions, this concentration is exactly what luck looks like. It also destroys any claim that BA gains reflect a stable conditional edge rather than one realized path. Combined with zero bid-ask, zero shorting cost, zero fee, zero impact modeling, the "money delta" is a mid-price fiction, not tradable PnL.

**(4) Two strict negative controls + locked prospective registration.**
- NC1 *Time-shuffled dates*: permute day labels within year by 5m-block-preserving circular shift; JDR4 must not exceed its observed BA lift in ≥95% of shuffles. 
- NC2 *Volatility-burst twin*: replace the JDR4 trigger with a matched-magnitude non-jump volatility burst (same 4h variance, no single dominant interval); if skill survives, the "jump" is not the identification.
Prospective lock: register a single forecast point at 08:55 Istanbul each DAY, for dates 2026-10-12 → 2027-04-09, frozen sign/threshold, no peeking, decision by 16:45. Endpoint must include recall and false-alarm rate, paired BA and Brier vs the same-date baseline, and a *bank spread gate* (forecast must exceed a pre-specified bid-ask friction implied by the source's spread distribution). Locked hash of ruleset required.

**(5) Verdict.**
JDR4 fails jump identification, fails family-wise novelty, and its economic case rests on one fat day of mid-price arithmetic. **REJECT_NOW.** No prospective extension of JDR4 should be launched; any replacement must be a new, prespecified, 5m/tick-confirmed, spread-gated hypothesis.
