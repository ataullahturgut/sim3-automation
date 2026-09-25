# GOLD MONTHLY 2026-08 FORECAST RE-AUDIT

**Audit date:** 2026-09-26
**Decision:** AUGUST MONTHLY FORECAST GENERATION = PASS

## Scope
This audit was triggered after invalidation of a separate exploratory DAILY H=1 experiment. The daily experiment and monthly forecast pipeline are separate code paths.

## August origin safety
- Target: 2026-08 monthly average XAU/USD.
- Origin: 2026-07 month-end.
- Origin Gold monthly level: 4073.00 USD/oz.
- Common governed daily-metal data available through: 2026-07-31.
- August target actual inside project DB at forecast run: unavailable / zero observations.
- Training rows used by each August component: 197, all pre-target.
- Forward X uses only July and June monthly metal levels plus July within-month weighted daily returns.
- GPR state is taken from the July origin vintage and lagged to June exactly as the governed monthly feature contract requires.
- August target Y is not read or substituted.

## Ensemble parity
Frozen Stage-4 FULL7 pool:
Vanilla, MPA, SCA, DE-ABC, Adaptive TLBO, TLBO-tuned PSO, MPA+SCA.
External weight rule: equal 1/7.

Frozen Stage-4 REDUCED4 pool:
Vanilla, MPA, SCA, DE-ABC.
External weight rule: equal 1/4.

Original August component artifacts:
- Vanilla 4067.577120
- MPA 4079.908717
- SCA 4092.288542
- DE-ABC 4067.744390
- Adaptive TLBO 4136.597224
- TLBO-tuned PSO 4135.334544
- MPA+SCA 4151.788052
- SMA-ELMFIS 4107.600401
- AOA-ELM 4108.385114

Recomputed ensemble arithmetic:
- FULL7 = 4104.462656 USD/oz.
- REDUCED4 = 4076.879693 USD/oz.

## Important wording correction
The scientifically precise description is not 'a completely fixed parameter vector from years earlier'. The model/feature/optimizer/ensemble protocol and Stage-4 component/weight choices are frozen by DEV authority; at each forecast origin, component fitting/refitting uses only information available before the target month, as in the canonical rolling-origin procedure.

## Decision
- August monthly FULL7 forecast 4104.46: VALID under the frozen monthly protocol.
- August monthly REDUCED4 forecast 4076.88: VALID under the frozen monthly protocol.
- SMA-ELMFIS 4107.60: VALID under its monthly protocol.
- AOA-ELM 4108.39: VALID under its monthly protocol.
- Separate daily H=1 invalidation does not alter these monthly outputs.
