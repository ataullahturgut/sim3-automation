# GOLD MONTHLY — CHHHO BRENT EXPANDED RESIDUAL SCREEN V1

**Date:** 2026-09-29  
**Status:** COMPLETE / NO ROBUST EXTERNAL PROMOTION  
**Purpose:** Re-test Brent residual information with additional stationary movement/stress variables after the bias-only attribution correction.

## Frozen design

Base:
- frozen ChHHO-ANFIS authority artifact **10989389723**
- BASE DEV ΣAE **1413.0298545342782**
- BASE Direction **23/33**

Mandatory attribution benchmark:
- BIAS_ONLY DEV ΣAE **1338.8935117711515**
- Direction **23/33**
- same residual chronology/cap logic, no external variables.

Residual learner:
- Ridge(alpha=10)
- StandardScaler on prior eligible residual rows only
- minimum prior residuals 12
- correction cap ±1.5 × median(abs(prior residual))
- prequential DEV only
- no 2025/2026 selection
- Neon read-only

## Brent variables

- `BRENT_MR1`: log ratio of origin-month mean Brent to previous-month mean Brent
- `BRENT_VW`: GPR-weighted daily Brent log-return summary, exact CURRENT8 weighting
- `BRENT_RVOL`: sqrt(sum(daily log return²)) within eligible origin month
- `BRENT_DOWNSIDE_VOL`: sqrt(sum(min(daily log return,0)²))
- `BRENT_MAX_DD`: maximum within-month peak-to-trough fractional drawdown

No raw Brent price level was used.

## Predeclared blocks and results

| Block | Variables | DEV ΣAE | Direction | Incremental vs BIAS_ONLY | Robust incremental excl. best month | 2024 incremental | Decision |
|---|---|---:|---:|---:|---:|---:|---|
| B1_MR1 | MR1 | 1346.502415 | 23/33 | -7.608904 | -10.032326 | -2.238102 | FAIL |
| B2_MR1_RVOL | MR1 + RVOL | 1332.365899 | 23/33 | +6.527612 | -1.219005 | +22.077338 | FAIL |
| **B3_MR1_DOWNSIDE** | **MR1 + DOWNSIDE_VOL** | **1330.832804** | **23/33** | **+8.060708** | **-1.265988** | **+27.898247** | **FAIL** |
| B4_MR1_MAXDD | MR1 + MAX_DD | 1359.785146 | 23/33 | -20.891634 | -30.173095 | -4.983855 | FAIL |
| B5_MR1_RVOL_DOWNSIDE_MAXDD | MR1 + RVOL + DOWNSIDE + MAX_DD | 1347.836087 | 23/33 | -8.942575 | -19.549669 | +12.518025 | FAIL |
| B6_ALL5 | MR1 + VW + RVOL + DOWNSIDE + MAX_DD | 1354.323041 | 23/33 | -15.429529 | -26.697682 | +4.381602 | FAIL |

Every block passes the old BASE-relative gate. **None passes the binding incremental-vs-BIAS_ONLY robustness gate.**

## Interpretation

The expanded Brent representation does contain a small amount of apparent incremental signal in B2/B3 on aggregate DEV:
- B2 beats BIAS_ONLY by **6.53 USD**
- B3 beats BIAS_ONLY by **8.06 USD**

However, for both blocks the advantage disappears after removing the single most favorable month:
- B2: **-1.22 USD**
- B3: **-1.27 USD**

Therefore the apparent gain is not distributed robustly across DEV origins. It is too dependent on one month to promote.

## Decision

- **No Brent residual block promoted**
- Best numerical block: **B3_MR1_DOWNSIDE**
- Scientific decision: **FAIL incremental robustness**
- Do not transport B3 to 2025/2026 as a selected challenger.
- Brent residual family remains closed unless a substantively new representation is proposed; simple feature expansion has been exhausted under this protocol.

## Execution

- workflow: **Gold Monthly ChHHO Brent Expanded Residual Screen V1**
- run: **36593458061**
- head: **b00e410dadcf24fb5c8a1ba2f4d05240be5ad8b8**
- job: **109492222857**
- artifact: **11045435477**
- digest: `sha256:c3af6e6e550f849bcc2c6e63db4e7d943ae829999c80176d26347891e5fcbfff`
