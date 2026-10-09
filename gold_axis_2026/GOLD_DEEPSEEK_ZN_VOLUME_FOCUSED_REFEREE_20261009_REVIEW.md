# DeepSeek independent technical critique of author-pre-registered ZN volume hypothesis

**External LLM text, not market evidence.**

**Review of ZN-VPT preregistration (max 950w)**

**(1) Incremental information / precise falsifiable null.** Possibly, but the current design does not isolate it. The stated object is a triple interaction: signed ZN return × volume surprise × disagreement versus contemporaneous XAU. Conditional on rZN, rXAU, |rZN| and a volatility proxy, the only falsifiable incremental claim is:

**H0 (VPT):** In the eligible overnight endpoint regression/probability model,
β(D × v × sign(rZN)) = 0
after conditioning on rZN, rXAU, |rZN|, realized/absolute XAU volatility, day-of-week/DST, and same-contract state; equivalently, P(sign(rXAU_overnight)=sign(rZN) | D=1,H=1) = P(sign(rXAU_overnight)=sign(rZN) | D=1,H=0) after those controls.
Reject H0 only if the incremental coefficient carries stable sign in 2023 **and** 2024 and survives 2025 retrospective without sign reversal.

This null is legitimate as far as it goes, but it is not automatically a “Treasury information” null. Because H=1 is defined by total ZN volume, the interaction can be nonzero merely because high-volume periods proxy for higher macro-event intensity, wider rates volatility, or better-measured rZN. The economic label “pricing-discovery innovation not yet incorporated in spot XAU” is not separately identified.

**(2) Leaks, rollovers, seasonality, correlation, rarity.**
- **Source-clock/PIT:** The 14:00/15:00 ZN hour bars are timestamped `ts_event`. If 15:00 local = 16:00 Istanbul, publication latency and Dukascopy M15 close alignment must be verified. The stated 16:15 local availability is an assumption; without native exchange/vendor timestamp audit it is a theoretical leak until proven.
- **Trade-volume semantics:** ZN OHLCV volume is total contracts, not aggressor-signed. It cannot distinguish buyer-initiated rate pressure from seller-initiated. This is a real semantic failure for any “signed information innovation” language, though not necessarily fatal to the predictive test.
- **Rollover:** Requiring same `instrument_id` and no cross-roll is correct. But continuous `ZN.c.0` existence does not guarantee the native 14/15 bars map to one liquid contract; front-month roll windows can thin volume before the official roll. Real risk.
- **Volume seasonality:** The prior-20 same-hour median partially handles intraday seasonality, but not month-end/quarter-end Treasury settlement, auction cycles, CPI/FOMC/NFP clustering, or DST shifts. Real.
- **Asset correlation:** rXAU and rZN are both US-macro/real-rate sensitive. Conditioning on same-date rXAU and |rZN| removes levels but not contemporaneous common shocks. The D=1 subset is explicitly disagreement, so selectivity is severe: disagreement nights may be exactly those where the 15→16 ZN move is noise or liquidity-driven. Real.
- **Rarity/DOWN collapse:** 73/173, 75/175, 76/178 DOWN in ZN-ready subsets is not itself collapse, but after D=1 ∧ H=1 ∧ valid prior20 the joint cell may be far smaller. If DOWN count falls below ~30 per development year, DOWN precision/recall will be unstable. Real practical risk.

**(3) Novelty versus CME3-K25, PRAMV, BSC8, CAVS.** Conceptually distinct from CME3-K25 because it adds volume-conditioned signed ZN and disagreement; from PRAMV because no RFR/PSF signature; from BSC8 because no XAU spread/sign-reversal feature. But it is **not** independent of CAVS’s cross-venue confirmation logic, and it partially overlaps any previously inspected ZN price feature. Material novelty is conditional, not architectural. If the interaction collapses after controlling for rZN and |rZN|, it is redundant with CME3-K25’s price-only negative result.

**(4) Minimum decisive study on 2023/2024 and inspected 2025.** Use exactly the same eligible dates as the source-readiness screen: 2023: 173, 2024: 175, 2025: 178, with identical contract/positive-volume/normal-weekday filters. Precompute v from prior20 only. Build four cells: D=1,H=1; D=1,H=0; D=0,H=1; D=0,H=0. Report N, coverage, balanced accuracy, UP/DOWN recall, **DOWN precision**, false alarms, and actual signed return, for each year and each cell. Compare the D=1,H=1 cohort against: (a) sign(rZN) on the identical cohort without volume filter; (b) same-date rZN-only prediction; (c) spot trend; (d) price-only RFR. Add a **month-shuffle negative control**: shuffle v across months within year, preserving hour and D, recompute the interaction; the observed effect must exceed the shuffled distribution. Correct for the selected H threshold and cohort via a pre-registered block bootstrap over months, and report the interaction coefficient with CIs. Do not fit any parameter on 2025.

**(5) Verdict.** **REVISE, do not execute as-is.** Reason: the signed economic content is not identified by total ZN volume; the test can reject H0 but cannot attribute rejection to aggressor-signed Treasury information. Minimum revision: freeze the exact regression/likelihood specification, add a volatility proxy and event-date indicator before scoring, and predefine DOWN-precision minimum and month-shuffle p-value. If those fail, the honest outcome is that the volume-conditioned disagreement effect is indistinguishable from ZN price/volatility and should be dropped.
