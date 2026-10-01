# GOLD SHORT-HORIZON TACTICAL FORECAST — Stage 6C Cross-Instrument Mapping Result

**Date:** 2026-10-01  
**Status:** **COMPLETE / MAPPING FAIL / NO INSTRUMENT FREEZE**  

**Primary workflow:** Gold Short Horizon Stage6C Instrument Mapping  
**Run:** **36895412116**  
**Artifact:** **11178394090**  
**Artifact digest:** `sha256:185a31b3cb01db3a38de22ab86269be8c9afbda0a676e2b0334347d9a3441f3f`

**Post-run timing diagnostic:**  
Run **36895839549**  
Artifact **11179492610**  
Digest `sha256:69e6c1092dfc9d74f391373ae6d154824bbe5814faf77aad3fc00b4961684a3c`

**Authority:** `GOLD_SHORT_HORIZON_TACTICAL_FORECAST_STAGE6C_AUTHORITY_2026-10-01.md`

## 1. Binding conclusion

Neither GLDM nor MGC maps closely enough to the current governed Borsa İstanbul Metal Price USD/oz H3 target to authorize tactical transfer.

Therefore:

- **GLDM mapping = FAIL**
- **MGC research mapping = FAIL**
- no execution instrument is frozen
- no 2025 tactical transport is authorized
- the current BIST-Metal-Price-based H3 forecast engine may remain a statistical/reporting engine for that target
- but it must **not** be treated as a validated signal for GLDM, MGC or another global Gold instrument.

The failure survives a post-run timing-lag diagnostic and therefore is not explained by a trivial one-session date shift.

## 2. Mapping results

Frozen mapping gate required:

- N >= 650
- Pearson >= 0.90
- Spearman >= 0.88
- beta in [0.85, 1.15]
- sign agreement >= 85%
- tracking-error SD <= 0.60%
- severe-divergence frequency <= 10%.

Actual:

| Metric | GLDM | MGC |
|---|---:|---:|
| N | 749 | 749 |
| Pearson | **0.5796** | **0.6244** |
| Spearman | 0.5837 | 0.6309 |
| OLS beta | **0.5063** | **0.5454** |
| Sign agreement | **71.2%** | **73.7%** |
| Tracking-error SD | **1.516%** | **1.435%** |
| Mean abs tracking error | 1.167% | 1.106% |
| Severe divergence >1% | **46.1%** | **44.2%** |
| Mean return difference | -0.005% | -0.002% |
| Mapping PASS | **NO** | **NO** |

The mapping failure is large, not marginal.

## 3. GLDM frozen U3 transfer

Frozen cost:
- **1.25 bp round-trip**.

Execution convention:
- entry at first U.S. equity market open on/after the forecast signal date
- exit at first U.S. open on/after the BIST H3 end date.

Result:

- trades: **184**
- total return: **+6.69%**
- CAGR: **+2.19%**
- max drawdown: **-12.22%**
- Sortino: **0.326**
- win rate: **48.9%**
- positive years: **1/3**.

Transfer PASS:
**NO**.

Even ignoring the mapping failure, the transferred GLDM implementation does not clear the frozen transfer-economics gate.

## 4. MGC delayed daily-data transfer stress

Frozen research cost:
- **1.00 bp round-trip**.

Because a CME daily-bar Open can belong to a Globex session beginning before the 00:30 Istanbul signal issue time, same-date Open was forbidden.

The daily-data stress therefore uses a deliberately delayed next-session Open.

Result:

- trades: **184**
- total return: **+25.72%**
- CAGR: **+7.95%**
- max drawdown: **-10.49%**
- Sortino: **1.656**
- win rate: **56.0%**
- positive years: **2/3**.

These economic numbers are interesting, but:

- MGC mapping gate fails badly
- daily secondary continuous data cannot establish same-origin execution
- therefore **MGC transfer PASS = NO** under the binding Stage-6C rule.

Do not interpret the MGC economics as authorization to trade the frozen BIST-target signal on MGC.

## 5. Independent GLDM source sanity

The preregistered Stooq cross-check was unavailable in the authoritative run.

Therefore:

- GLDM cannot satisfy the source-sanity production-freeze requirement even independently of the mapping failure.

This does not change the scientific decision because mapping already fails decisively.

## 6. Post-run timing diagnostic

Because Gold-vs-Gold H3 correlation appeared unexpectedly low, a separate post-run bug diagnostic checked one-observation daily returns over row lags -3..+3.

This diagnostic was explicitly **not allowed to promote an instrument or change Stage-6C mapping rules**.

Best observed daily-return correlations:

| Instrument | Best diagnostic row lag | Pearson |
|---|---:|---:|
| GLDM | +1 | **0.4695** |
| MGC | +1 | **0.3938** |

Positive lag here means the BIST daily return aligns most with an earlier instrument-return row after the diagnostic shift.

Interpretation:

- there is evidence of timing/market-microstructure offset
- but even the best post-run lag relationship remains far below a clean tradable-Gold mapping
- therefore the Stage-6C failure is **not** a simple one-day date-alignment bug.

## 7. Why the target mismatch is economically plausible

The governed project target is Borsa İstanbul **Metal Price USD/oz**.

Borsa İstanbul defines Metal Price as:

- the weighted-average price of T+0 transactions for the relevant metal / price type;
- when no qualifying transaction price is formed, the latest current international price in the system may be used at bulletin publication.

This is therefore a local precious-metals-market transaction statistic, not an international synchronous spot close.

Borsa İstanbul separately publishes a **BIST Spot Gold Index** specifically designed to reflect international spot commodity prices synchronously.

That distinction is now material to this project.

## 8. Scientific implication

Stages 0–5 answered:

> Can we forecast the next H1/H3/H5 movement of the BIST Metal Price series?

The answer was:
- modest predictive signal, strongest at H3.

Stages 6–6C asked a different and necessary question:

> Does that signal transfer to a realistically tradable global Gold instrument?

Current answer:
**NO**.

This does not invalidate the statistical H3 forecast for the original target.

It invalidates using that target as a direct proxy for GLDM/MGC tactical investment without redesign.

## 9. What must not be done

Do not:

- choose the +1 lag because it is better
- lower mapping gates
- select MGC because its delayed transfer economics look attractive
- use 2025 to find a better mapping
- retrofit GLDM/MGC thresholds
- claim BIST Metal Price and international spot are interchangeable.

## 10. Artifact hashes

Primary Stage 6C:

- `stage6c_mgc_yahoo_daily.csv`: `95a20b60d158e7ca1469cb52e37f16f52e6e5162a3def12c67018410f4066cd2`
- `stage6c_gldm_mapping.csv`: `b8b6a37541c5d4ed358f0c6fdd4c673a9804ee5cbb557e893a0f6e52e0711921`
- `stage6c_mgc_mapping.csv`: `e7d8bd5833d717c39879eccc6e2e68faf539eb822bcb267ea24405bb651b1728`
- `stage6c_gldm_u3_transfer.csv`: `23f851571c8ca64a995feb56844d380309b82624f5f946b4fc8e350ac6f4343f`
- `stage6c_mgc_delayed_u3_transfer.csv`: `ef99432eecae43eb9f87c23fe9e47db02f9f219e341edefc1dac2a8aaea3e815`
- `stage6c_instrument_decisions.csv`: `0eb642a9c82ccfc7738016a0f4e13d2c7b0cef5e8133492757b951dd8889ca36`
- `STAGE6C_RESULT.md`: `3119d8999ba1d554f1858ab803ef11a587ecf59f525bf2d30991c31f4d642847`.

Timing diagnostic:

- `stage6c_daily_return_lag_diagnostic.csv`: `2e4680c2281ff1cb2b932e386516165388ce1a40819efb90b20cf8d943fb8824`
- `stage6c_daily_return_best_lag.csv`: `ea73e26b2346fd0dde33922dcef00406471e235a62f4ff8b3397a51eb4e4502d`
- `TIMING_DIAGNOSTIC.md`: `ec9b764acaddb286ec8da3dd28cbc2cf73a0979faf41aa6b58c54cfb7cc061d3`.

## 11. Decision

**Stage 6C = COMPLETE / FAIL.**

Execution instrument:
**NONE FROZEN**

2025 tactical transport:
**BLOCKED**

Current H3 BIST-Metal-Price forecast engine:
**RETAIN FOR ORIGINAL-TARGET RESEARCH / REPORTING ONLY**

## 12. Exact next stage

**Stage 6D — Tactical Target Authority Redesign**

The tactical project must stop treating BIST Metal Price USD/oz as a universal investable-Gold proxy.

Before any new model fitting, compare and freeze a target authority appropriate to the actual investment objective.

Candidate target lanes:

### Lane A — International synchronous Gold target
- BIST Spot Gold Index / suitable origin-safe international spot representation
- purpose: instrument-agnostic Gold directional research.

### Lane B — GLDM-direct target
- predict the actual ETF return to be traded
- include ETF trading calendar / open timing explicitly.

### Lane C — MGC-direct target
- predict actual Micro Gold futures return
- requires official / timestamped CME data and explicit futures contract / roll authority.

The next target must be chosen **before** opening 2025.

The existing BIST-Metal-Price results remain archived and must not be mixed with redesigned-target performance.
