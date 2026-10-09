# ZN-VPT original author hypothesis → external focused critique → manifest novelty check → source-only STOP — Oct 9 2026
**Status:** Q/A workflow SUCCESS / INITIAL HARD-GATE FAIL / NO PRICE-DIRECTION TEST RUN ON THE SMALL COHORT.

## Author-first research
GPT-6 independently used academic gold price-discovery and news evidence (Hauptfleisch et al 2016 DOI 10.1002/fut.21775; Elder et al 2012 DOI 10.1016/j.jbankfin.2011.06.007; Sobti et al 2021 DOI 10.1016/j.irfa.2021.101893) to preregister `GOLD_ZN_VOLUME_CONDITIONED_NIGHT_SIGN_HYPOTHESIS_PREREG_20261009.md` BEFORE viewing conditional directions. ZN 10-year Treasury-futures signed return interacting with abnormal origin-safe hourly volume and contemporaneous gold price disagreement could signal late macro transmission to XAU. Intended target regular 17TR→next09TR; no gross PnL, no post-17 information. No assumption that ZN total volume identifies buyer/seller initiated orderflow.

## Focused DeepSeek, NOT open-ended brainstorming
One actual bounded **deepseek-flash** referee call; 2,129 prompt + 1,264 response = **3,393 tokens**, finished STOP; only prereg text/aggregate counts sent, NO raw market rows or API secrets. External text `GOLD_DEEPSEEK_ZN_VOLUME_FOCUSED_REFEREE_20261009_REVIEW.md`; token receipt `..._RESULT.json`. It argued correctly that total OHLCV volume is not signed orderflow, a triple interaction may proxy volatility or macro event intensity, and pre-16:15 exchange-native source readiness and roll maps require independent proof. Its verdict was **REVISE**, not promote, with source, sample, matched ablations and explicit falsification. Its formula shorthand should NOT be misrepresented as a proof of exogeneity, and source gate does not automatically fail solely because the bar time is start-labeled.

## Manifest direct duplication audit AFTER reviewing DeepSeek
- `GOLD_EXECUTION_2026_CME3_COMPLETENESS_NQ_ZN_CL_RFR_K25_PREREG_20261009.md` empirically tested **six returns only** (ZN/NQ/CL r1/r3), and 2026 K25 did not beat exact-date price-only RFR. **No ZN volume interaction**.
- `GOLD_EXECUTION_CONTINUATION_EXPANSION_RESEARCH_RESULT_2026-10-08.md` defines an **UNTRAINED CAVS** using GC volume/relative price in same-sign spot sessions, not a finished ZN participation study. Both are conceptual cross-market confirmation ideas; NOT a genuinely new literature family independent of CAVS. This follow-on is differentiated by a market instrument and an explicit volume-conditioned incremental test; do not inflate novelty.
- `GOLD_EXECUTION_20261009_CAUSAL_QUOTE_PRESSURE_AND_GC_SPOT_GAP_RESEARCH.md` tested XAU own quoted spread and separate GC return mismatch; no volume.
- Original PRAMV macro veto used realised published macro surprise, subject to archival vintage; not ZN volume.

## Actual label-blind read-only Neon source check
Source: signed 2020-25 source-qualified XAU BID/ASK + 2023-26 CME native ZN H1 two-hour fixed clock, same contract. Strict normal weekdays, a ZN prior20 SAME-local-hour volume median, disagreement `sign(rZN)≠sign(rXAU)`, high volume `volume>1.5*median_prior20`.
- 2023: basic ZN+spot eligible 173/198; prior20 ready **158**; disagreement **38**, high-volume disagreement **14**, low-volume disagreement24.
- 2024: eligible175/198; prior20 ready175; disagreement59, high-volume disagreement **18**, low41.
- 2025: eligible178/198; prior20 ready178; disagreement78, high-volume disagreement **27**, low51.

**Scientific disposition:** The prespecified strict D=1 ∧ H=1 cohort has only 14 and 18 DEV observations in 2023 and 2024, far below a credible balanced signed predictor sample, especially DOWN. These counts were obtained WITHOUT opening any new model target outcomes (the SQL projected ONLY group counts, despite joining an existing table with an unused target column). **STOP primary strict-cohort attempt BEFORE SCORE**. Never claim the yearwise 173/175 coverage is 173/175 actual decisions. Do not relax the 1.5 cutoff *based on label performance*. Any broad all-ready continuous-volume interaction is a SEPARATE exploratory pre-outcome revision; must be frozen anew and labeled a related mechanism rather than 'new independent discovery'.

## Next legitimately different minimal design
If pursuing ZN as an independent market family, drop the selective rare-cells hard rule based solely on **label-blind source coverage**, and pre-register continuous `signed rZN × centered log(volume/previous-20 same-hour median)` nested against **the identical** spot+rZN+|rZN|+volume baseline. Month-chronological 2023 fitting and 2024 development test, 2025 already-inspected transport, later untouched freeze; no 2025 tune. This is low-capacity and falsifiable; it is NOT a proof of causal 'informed volume', nor investment strategy. If the nested interaction fails exact-date Brier / BA / DOWN recall, close the ZN volume hypothesis.
