# GOLD MONTHLY — F4 FX + RATES DIRECT FEDERAL RESERVE DDP HARD DATA RE-AUDIT

**Date:** 2026-09-29  
**Status:** COMPLETE / PASS  
**Purpose:** Resolve whether poor Rates/FX native-input model results could be caused by corrupted, incomplete, shifted, or incorrectly transformed source data.

## 1. Authority

Frozen research source:
- External Authority V2 payload: `fb779f1f1a3f5689f9f631aadc7e6e6e0c8cf5e50ec7730a233b80e8789438bc`
- artifact: **11028494060**

Fresh official re-fetch:
- source: **Federal Reserve Board Data Download Program (DDP)**
- H.10: Broad USD package
- H.15: nominal 10Y and inflation-indexed real 10Y packages
- workflow: **Gold Monthly F4 FX Rates Direct DDP Reaudit V1**
- authoritative run: **36580341003**
- head commit: **3d8ca815ede86fd8b7ad694d0a58be0278b13e22**
- job: **109446532518**
- conclusion: **SUCCESS**
- result artifact: **11038493043**
- artifact digest: `sha256:a24c1ed64097eeb4c25055695ff34b8785da1815de8c57093e95e2cd6427be20`

Earlier FRED-distribution audit attempts are **non-authority network diagnostics**:
- run 36578797117: download read-timeout before comparison; technical only
- runs 36579110948 / 36579569612: FRED download path was slow; direct Board DDP re-fetch supersedes them for this question.

## 2. Raw package hash re-check

All frozen raw source package hashes exactly match a fresh Board DDP download:

- H.10 index package SHA256 equal: **YES**
- H.10 rates package SHA256 equal: **YES**
- H.15 package SHA256 equal: **YES**

Gate: **PASS**

This is stronger than a sample-row comparison: the downloaded official raw package bytes are unchanged relative to the frozen authority inputs.

## 3. Full daily-series comparison

### Broad USD Index
- series role: FX / Broad USD
- frozen rows: **4167**
- fresh official rows in same window: **4167**
- common rows: **4167**
- frozen-only dates: **0**
- official-only dates: **0**
- value mismatches > 1e-10: **0**
- maximum absolute daily value difference: **0.0**

### Nominal 10Y Treasury yield
- frozen rows: **4186**
- fresh official rows in same window: **4186**
- common rows: **4186**
- frozen-only dates: **0**
- official-only dates: **0**
- value mismatches > 1e-10: **0**
- maximum absolute daily value difference: **0.0**

### Real 10Y Treasury yield
- frozen rows: **4186**
- fresh official rows in same window: **4186**
- common rows: **4186**
- frozen-only dates: **0**
- official-only dates: **0**
- value mismatches > 1e-10: **0**
- maximum absolute daily value difference: **0.0**

Full daily coverage/value gate: **PASS**

## 4. DEV transformation re-computation

For every DEV target origin from **2022-04 through 2024-12 (33 origins)**, the transforms were independently recomputed from the fresh official DDP series using the frozen release-lag contracts.

Maximum fresh-official vs External Authority V2 differences:

- Broad USD monthly mean log change (FX1 / MR1): **0.0**
- Broad USD daily RMS log-return volatility (FX2): **0.0**
- nominal 10Y monthly mean difference: **0.0**
- real 10Y monthly mean difference (Rates R1): **0.0**
- 10Y breakeven monthly difference (Rates R2): **0.0**

DEV transform gate: **PASS**

## 5. Release / chronology contracts retained

- H.10 FX release safety cutoff: **7 calendar days**
- H.15 Rates release safety cutoff: **2 calendar days**
- target-month data in transforms: **NO**
- 2025 used for DEV selection: **NO**
- 2026 used for DEV selection: **NO**

The existing B1/B2 chronology/scaling audits remain valid.

## 6. Scientific conclusion

The poor native-input Rates and FX results **cannot be attributed to a detectable raw-data corruption, date shift, missing-date problem, official-source mismatch, or transformation arithmetic error**.

Current evidence therefore supports:

1. Rates/FX source data are correct under the governed authority contract.
2. Release-safe monthly/daily-path transforms used in the tested variants are reproduced exactly from a fresh official source.
3. The deterioration after adding Rates/FX is a **model/representation/generalization issue in the native ChHHO-ANFIS integration path**, not a demonstrated data-quality failure.
4. This does not imply Rates or FX have no economic information; historical residual-layer results from different architectures remain separate evidence.
5. Native F4 Rates and FX family closures remain valid.
6. Next unopened external family remains **VIX**.

## 7. Gates

- raw package hash gate: **PASS**
- daily coverage gate: **PASS**
- daily values gate: **PASS**
- DEV transform parity gate: **PASS**
- overall hard data audit: **PASS**
