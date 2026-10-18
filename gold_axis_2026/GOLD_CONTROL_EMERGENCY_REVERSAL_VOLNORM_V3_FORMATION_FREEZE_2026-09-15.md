# GOLD CONTROL — EMERGENCY REVERSAL VOLNORM V3 FORMATION FREEZE

**Freeze date:** 2026-09-15  
**Identity:** `EMERGENCY_REVERSAL_VOLNORM_SUCCESSOR_V3`  
**Status:** `FORMATION_PASS_FROZEN_BEFORE_VALID_2025_REPLAY`  
**Formation workflow run:** `35023205527`  
**2025 observations consumed during V3 formation:** `0`

## 1. Frozen executable/configuration identity

- configuration SHA-256: `fdb2c6238fc194afd9c5a253ae232790bdde5b6faa49cbcd96811972d5a83a84`
- implementation SHA-256: `4adcec3043b141babd38a7bef9ed854f3fdb868bd84a88a32e835fa1e6921cbd`
- formation timeline SHA-256: `1600b810e4ea724f6f863ca11505d30e49c3288271476dd8be0f0b7ac14aff69`

Frozen parameters/source:

- source: `XAU_TWELVE_1H_SELECT_14_00_NY_WEEKDAY_RESEARCH_V3`;
- provider: Twelve Data `XAU/USD`, interval `1h`, timezone `America/New_York`;
- selected bar open time: exact `14:00:00`;
- selected calendar dates: Monday-Friday only;
- Saturday/Sunday provider bars: rejected from the governed path;
- annual source coverage gate: >=95%;
- invariant: selected dates <= Monday-Friday calendar dates;
- volatility window: 20 prior observed returns;
- leg threshold: 2.0 accumulated path-vol units;
- reversal threshold: 2.0 accumulated path-vol units;
- EXTREME annotation threshold: 3.0 accumulated path-vol units;
- monthly forecast dependency: NONE;
- fixed raw-percentage threshold: NONE;
- interpolation / forward-fill / alternate-hour fallback / provider substitution: NONE.

## 2. Formation evidence

Formation interval: calendar 2022–2024 only.

Source coverage:

- 2022: 257/260 = 98.85%;
- 2023: 256/260 = 98.46%;
- 2024: 258/262 = 98.47%;
- weekend rows consumed: 0.

Detector accounting:

- selected closes: 771;
- eligible post-warmup rows: 750;
- reversal alerts: 11;
- UP alerts: 5;
- DOWN alerts: 6;
- EXTREME alerts: 1;
- alert rate: 1.4667%.

All targeted tests passed (10/10), including strictly prior-only volatility, transition-only alerting, prefix invariance, exact determinism, no monthly-forecast dependency, explicit weekday source guard and selected-count calendar invariant.

## 3. Invalid predecessor boundary

The V2 2025 run is not evidence. It was invalidated because non-weekday provider bars entered its state path. No V2 2025 alert count, match count, timeline hash or overlay result may be reused for V3 performance claims.

V3 is a source-governance corrective successor only. No detector threshold, path-volatility formula, source hour or state-transition rule was changed in response to the invalid V2 performance output.

## 4. Valid corrected 2025 challenge lock

From this freeze onward a corrected 2025 replay is permitted only if runtime recomputation of the V3 configuration and implementation hashes exactly matches the frozen hashes above.

The corrected challenge must remain two-stage:

1. **Engine stage:** use the complete historical path required for state initialization, generate every eligible 2025 Monday-Friday V3 output without loading the 19-event volatility inventory, assert annual coverage >=95%, assert no weekend date and assert selected count <=261, then save/hash the complete 2025 engine timeline.
2. **Overlay stage:** read the already frozen engine payload and only then overlay the independent frozen 19-event volatility inventory.

Primary comparison is same governed date. ±1 and ±3 observed-day proximity may be reported descriptively only.

No V3 source, threshold, volatility window, state transition or alert rule may change after the corrected 2025 engine output is observed under this identity.

The corrected result remains `HISTORICAL_REPLAY / RETROSPECTIVE_DIAGNOSTIC`, not human-blind prospective evidence, because an invalid predecessor run had already exposed 2025 market outcomes to the research process.