# DeepSeek independent technical critique of author-pre-registered ZN volume hypothesis

**External LLM text, not market evidence.**

**R3 hostile board. Three candidates vs PRAMV/RFR, TURN, M15 BSC8.** No claims from options-signed-variance are transferred to spot XAU.

**S1 — SSV4.** (a) Distinct only if PRAMV used unsigned semivariance or aggregate vol. If PRAMV already signed BPV, REJECT_DUPLICATE. (b) 09/17 Turkey closes are *valid only as fixed clock labels*, not as information endowments; Dukascopy XAU M15 timestamps often misalign with Istanbul FX/bank close liquidity. (c) Persistence if overnight inventory unloads in same direction as late-session volatility pressure; inversion if 16:30–16:45 close is dominated by dealer hedging/rebalancing. (d) Strongest negative control: **sign(Σr_i)** and **last1h sign** on same 17 rows; also sign(r_16) alone. (e) KEEP_FOR_FALSIFICATION only if not in prior PRAMV manifest.

**S2 — RCL4.** (a) Distinct from RFR iff RFR did not use normalized close rank over same 17 rows. (b) Same clock issue; 17:00 close in Turkey is not 17:00 New York, so “overnight” mislabels the actual macro window. (c) High-end exhaustion can persist upward in thin liquidity/weak USD or invert via stop-runs; 0.20/0.80 are arbitrary and create selection bias. (d) Strongest negative control: same-row last4 sign and sign(Σr_i); plus **shuffled c threshold** within day (placebo). (e) KEEP_FOR_FALSIFICATION, conditional on exact cutoff and no duplicate manifest hit.

**S3 — JDR4.** (a) Distinct from TURN iff TURN did not use max r_i²/Q. If TURN was already jump-reversal on signed r_j, REJECT_DUPLICATE. (b) Same clock invalidity for 09/17 as above. (c) Reversal plausible under temporary liquidity overshoot; inversion plausible under informed order flow into the jump. (d) Strongest negative control: **sign(r_j) continuation**, and max-|r_i| same-date sign without concentration. (e) KEEP_FOR_FALSIFICATION.

**Required exact controls (same-row, no alternative model):**
1. Last1h sign: sign(Σ_{i=13}^{16} r_i).
2. Last4h sign: sign(Σ_{i=1}^{16} r_i).
3. sign(r_16), sign(Σ_{i=1}^{12} r_i), max|r_i| sign.
4. Paired **false-DOWN detection**: for every acted DOWN, check whether same-date last1h/last4h also DOWN; McNemar exact two-sided on discordant pairs only.
5. Coverage audit: acted N vs eligible N; abstentions counted; no silent forcing.
6. Annual 2023, 2024, 2025 split; multiple-testing correction across 3 × 2 horizons.

**Verdicts:**
- S1: KEEP_FOR_FALSIFICATION if unsigned PRAMV; else REJECT_DUPLICATE.
- S2: KEEP_FOR_FALSIFICATION; arbitrary thresholds must be frozen and reported.
- S3: KEEP_FOR_FALSIFICATION if TURN unsigned; else REJECT_DUPLICATE.

No promotion without same-date control improvement in 2023 and 2024 and retained 2025. No P&L claims.
