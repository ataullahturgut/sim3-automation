# GOLD MONTHLY — CHHHO VIX R1 FROZEN TRANSPORT 2025/2026

**Date:** 2026-09-29  
**Status:** COMPLETE / FROZEN TRANSPORT PASS  
**Selection authority:** DEV 2022-04..2024-12 only  
**2025/2026 role:** retrospective transport/reporting only

## Frozen challenger

Selected on DEV:
- **VIX_R1_CHANGE**
- feature: origin-month mean eligible VIX minus previous-month mean eligible VIX
- residual target: actual price − frozen ChHHO BASE forecast price
- Ridge alpha: **10**
- correction cap: **±1.5 × median(abs(DEV residual))**
- scaler and Ridge fit on full DEV only
- no 2025 or 2026 residual updating
- no random split
- Neon reads in transport run: **0**

Frozen fit:
- n = **33**
- cap = **53.266887317887495**
- standardized VIX_CHANGE coefficient = **2.3347459307325407**
- intercept = **13.690850943418237**

## 2025 transport

BASE:
- ΣAE **1252.0541594740248**
- MAE **104.3378466228354**
- Direction **9/12**

VIX_R1 corrected:
- ΣAE **1082.0273188083147**
- MAE **90.16894323402623**
- Direction **9/12**

Improvement:
- ΣAE **+170.0268406657101 USD**
- relative ΣAE improvement **13.5798%**
- direction change **0**

The correction reduced absolute error in all 12 months of 2025.

## 2026 Jan-Aug transport

BASE:
- ΣAE **1526.1332118229584**
- MAE **190.7666514778698**
- Direction **5/8**

VIX_R1 corrected:
- ΣAE **1526.0485229389474**
- MAE **190.75606536736842**
- Direction **6/8**

Improvement:
- ΣAE **+0.08468888401102959 USD**
- direction **+1 month**

The correction materially helped some months and hurt others. Aggregate price-error improvement is effectively zero.

August 2026:
- actual **4411.00**
- BASE **4063.0063**
- correction **+13.2547**
- corrected **4076.2610**
- BASE direction: **wrong**
- corrected direction: **correct**
- BASE AE **347.9937**
- corrected AE **334.7390**

September 2026:
- **BLOCKED**
- canonical ChHHO BASE requires August Gold/Silver/Platinum/Palladium origin inputs and the governed canonical four-metal history is incomplete for August.

## Interpretation

The VIX residual signal has strong DEV evidence and strong 2025 transport, but it does **not** materially reduce aggregate 2026 Jan-Aug price error.

Therefore:
- VIX_R1 remains a valid residual challenger.
- 2025 transport supports genuine out-of-sample value.
- 2026 shows regime instability / limited magnitude adaptation.
- Do not claim universal improvement.
- Do not retune on 2025/2026.

## Execution authority

- workflow: **Gold Monthly ChHHO VIX R1 Frozen Transport 2025 2026 V1**
- run: **36587033148**
- head commit: **acfee6fdc0c7b41e874e7a166d5376cba74bf9bb**
- job: **109469978233**
- artifact: **11042740289**
- artifact digest: `sha256:5d6966e470412675af649c1fc869b32fadb9b0252be27f6b5fec4307716aa285`
