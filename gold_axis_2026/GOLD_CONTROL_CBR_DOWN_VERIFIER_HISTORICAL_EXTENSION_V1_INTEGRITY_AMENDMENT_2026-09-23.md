# GOLD CONTROL — CBR DOWN VERIFIER HISTORICAL EXTENSION V1 INTEGRITY AMENDMENT

**Date:** 2026-09-23  
**Parent identity:** `CBR_DOWN_VERIFIER_HISTORICAL_EXTENSION_V1_RESEARCH`  
**Trigger:** first CI integrity run failed before any model scoring.

## Finding

The cross-source path harmonization step initially attempted to compare every calendar-date overlap between the reconstructed external source and the governed internal source.

The frozen CBR path representation itself requires at least **239 intraday returns** per day. Some governed overlap dates have fewer than 239 returns (first observed failure: 203), so those dates are not representable under the frozen CBR method.

## Amendment

For the path-harmonization gate only:

- define `CBR-representable overlap` as exact-date source overlap where **both** external and governed daily return arrays satisfy the frozen CBR requirement `len(returns) >= 239` and have positive realized variance;
- compute all preregistered correlation / DTW harmonization metrics only on that representable overlap;
- keep the preregistered minimum overlap requirement `n >= 300` unchanged;
- do not impute, pad or resample a short governed day;
- do not change CBR NPTS, BAND, K, EPS or p=0.50;
- do not alter any outcome labels or model scoring rule.

This is an integrity/eligibility clarification forced by the original frozen CBR contract, not a performance-based change.

No model outcome had been scored when the failure occurred.
