# GOLD MONTHLY — ChHHO Origin-Signal Frozen Transport 2025/2026

**Date:** 2026-09-29  
**Status:** FROZEN ALARM-DETECTION TRANSPORT COMPLETE / GENERAL ALARM DETECTOR NOT YET VALIDATED  
**Purpose:** Test one question only: whether the DEV-derived origin-visible warning mechanisms can identify future ChHHO high-error months before the target month begins.

> **This report does NOT test model switching, fallback selection, routing, blending, or alternative-model choice.**
> Those are separate later questions and are intentionally excluded here.

## 1. Frozen rule set

No 2025/2026 outcome was used to alter these rules.

### A — CROSS_METAL_FRAGILITY
At the forecast origin:
- ChHHO forecast direction = current Gold monthly direction;
- |Gold monthly log return| < 2%;
- at least 2 of Silver / Platinum / Palladium move in the opposite direction to Gold.

### B — SUPPORTED_MOMENTUM_UNDERREACTION
At the forecast origin:
- Gold monthly log return > +3%;
- at least 2 of Silver / Platinum / Palladium are positive;
- Broad USD monthly mean log change < 0;
- nominal 10Y monthly-mean change < 0;
- real 10Y monthly-mean change < 0;
- ChHHO predicted Gold move <= +1% (near-flat or opposite-direction forecast).

### C — DELAYED_RATES_CATCHUP
At the forecast origin:
- Gold monthly log return < 0;
- nominal 10Y monthly-mean change < 0;
- real 10Y monthly-mean change < 0;
- |ChHHO predicted Gold move| < 1%.

### D — MACRO_GOLD_CONFLICT
At the forecast origin:
- Gold monthly log return > +3%;
- Broad USD monthly mean log change > 0;
- nominal 10Y monthly-mean change > 0;
- real 10Y monthly-mean change > 0;
- ChHHO predicts UP.

The alarm system is simply A OR B OR C OR D.

## 2. Frozen transport data

- ChHHO 2025 forecasts: frozen ANFIS authority artifact 10989389723.
- ChHHO 2026 Jan-Aug forecasts/actuals: frozen transport authority artifact 11042740289.
- Four-metal origin data: governed DEV snapshot through 2024-12 plus public StakTrakr extension from 2025-01-02 through 2026-09-28.
- Broad USD / nominal 10Y / real 10Y: External Authority V2 artifact 11028494060.
- Release cutoffs retained: H.10 Broad USD = 7 calendar days; H.15 rates = 2 calendar days.
- 2025/2026 are reporting-only.
- No threshold or rule was altered after observing transport outcomes.

## 3. What counts as a high-error month?

The frozen DEV ChHHO absolute-error third quartile is:

- **Q3 = 63.06 USD**

For this transport audit:

- **HIGH ERROR = ChHHO absolute error > 63.06 USD**
- **ALARM HIT = alarm fires and the target month is HIGH ERROR**
- **FALSE ALARM = alarm fires but error is <= 63.06 USD**
- **MISS = HIGH ERROR occurs but no alarm fires**

This definition is frozen from DEV and is not retuned on 2025/2026.

## 4. Alarm months only

| Target | Alarm mechanism | ChHHO AE | High error? | Detection result |
|---|---|---:|---|---|
| **2025-03** | B — Momentum underreaction | **119.06** | YES | **HIT** |
| **2025-09** | A — Cross-metal fragility | **288.42** | YES | **HIT** |
| **2025-12** | A — Cross-metal fragility | **93.32** | YES | **HIT** |
| **2026-05** | A — Cross-metal fragility | **55.10** | NO | **FALSE ALARM** |

No C or D alarm fires in 2025 or 2026 Jan-Aug.

## 5. 2025 alarm-detection result

2025 contains 12 target months.

- alarms fired: **3**
- high-error months: **8**
- alarm hits: **3**
- false alarms: **0**
- high-error misses: **5**

Metrics:
- **precision = 3 / 3 = 100%**
- **recall = 3 / 8 = 37.5%**
- false-alarm rate among alarms = **0%**

Interpretation:

The frozen alarm system is **highly selective but incomplete** in 2025.  
When it raises an alarm, the alarm is correct in all three cases.  
However it detects only 3 of 8 high-error months.

Therefore 2025 supports the statement:

> “Some ChHHO danger states are visible ex ante.”

It does **not** support:

> “Most ChHHO high-error months can already be detected.”

## 6. 2026 Jan-Aug alarm-detection result

2026 Jan-Aug contains 8 target months.

- alarms fired: **1**
- high-error months: **5**
- alarm hits: **0**
- false alarms: **1**
- high-error misses: **5**

Metrics:
- **precision = 0 / 1 = 0%**
- **recall = 0 / 5 = 0%**

Large unflagged ChHHO errors:

- **2026-01: 458.50 USD — MISS**
- **2026-03: 145.62 USD — MISS**
- **2026-06: 362.17 USD — MISS**
- **2026-07: 82.68 USD — MISS**
- **2026-08: 347.99 USD — MISS**

The only alarm:
- **2026-05: 55.10 USD — FALSE ALARM**

Interpretation:

The DEV-derived alarm mechanisms **do not identify the dominant 2026 high-error regime**.

## 7. Combined frozen transport result

Across 2025 + 2026 Jan-Aug:

- months: **20**
- alarms: **4**
- high-error months: **13**
- hits: **3**
- false alarms: **1**
- misses: **10**

Metrics:
- **precision = 75.0%**
- **recall = 23.1%**
- false alarms among alarms = **25.0%**

This is not sufficient for a general-purpose high-error warning system.

The important distinction is:

- **Precision is reasonably high overall because the system rarely raises an alarm.**
- **Recall is too low because most high-error months are not detected.**

So the present mechanism set is better described as:

> **specific warning signatures for a subset of failure modes**

rather than:

> **a general ChHHO error alarm.**

## 8. Mechanism-level transport reading

### A — Cross-metal fragility
Transport alarms:
- 2025-09 — HIT
- 2025-12 — HIT
- 2026-05 — FALSE ALARM

Result:
- 2 true high-error detections
- 1 false alarm

**Status: PARTIAL TRANSPORT.**

### B — Supported momentum underreaction
Transport alarm:
- 2025-03 — HIT

**Status: PROMISING, BUT ONLY ONE OUT-OF-DEV EVENT.**

### C — Delayed rates catch-up
No transport event.

**Status: NOT TESTED BY EVENT COUNT.**

### D — Macro-Gold conflict
No transport event.

**Status: NOT TESTED BY EVENT COUNT.**

## 9. Scientific conclusion

The alarm hypothesis is **partially supported, but not validated as a complete detector**.

What is supported:
- the DEV mechanisms were not pure retrospective storytelling;
- three frozen alarms in 2025 correctly identify three genuinely high-error ChHHO months;
- cross-metal fragility and momentum-underreaction can carry real ex-ante warning information.

What is not supported:
- the current four mechanisms do not detect most high-error months;
- they completely fail on the dominant 2026 failure regime;
- therefore the alarm layer is not yet complete enough for operational use.

## 10. Correct next question

The next stage remains **alarm discovery**, not routing.

Do NOT ask:
- which alternative model should replace ChHHO;
- whether FULL7/REDUCED4 should be used;
- what switching rule should be applied.

Ask only:

> **What origin-visible state was present before the unflagged 2026 high-error months, especially 2026-01, 2026-06 and 2026-08, that is absent from the current four mechanisms?**

Candidate information families for that separate mechanism-discovery stage:
- COMEX positioning;
- gold ETF flows;
- GVZ / gold implied volatility;
- central-bank / gold-specific flow proxies;
- event-risk state.

The frozen A/B/C/D rules must not be retuned using 2025/2026 outcomes.
