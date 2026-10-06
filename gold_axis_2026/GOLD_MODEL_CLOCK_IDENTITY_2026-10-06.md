# GOLD SHORT-HORIZON — MODEL CLOCK IDENTITY

**Date:** 2026-10-06  
**Status:** BINDING CLOCK AUTHORITY / GOVERNANCE CORRECTION  
**Purpose:** define exactly which timezone controls each layer of the current H3/CIG-D1 stack and prevent Turkey / New York / UTC clock semantics from being mixed.

## 1. Executive answer

The current short-horizon model is **not a Turkey-clock model**.

It is also not a single-clock New York model.

The current stack is a **mixed-clock architecture**:

| Layer | Binding clock | Current semantic |
|---|---|---|
| Governed daily Gold reference / H3 target | **UTC calendar day** | full-UTC-day daily-reference semantic |
| Hourly intraday feature layer (IRIS/SAGE lineage) | **America/New_York** | features anchored at 16:00 New York on feature-cutoff date |
| Forecast issue/deadline | **America/New_York** | next-weekday 08:00 New York |
| CIG-D1 historical same-day label | derived from governed daily reference | therefore inherits the daily-reference/UTC-day semantic rather than an Istanbul trading day |
| User-facing clock conversion | **Europe/Istanbul** | reporting/execution localization only; not a model input clock |

**Therefore the model itself does not currently calculate a Turkey trading session.**

## 2. Daily target clock

The semantic audit established that the governed Gold daily series is best represented as a **full UTC calendar-day average/reference**, cross-audited against the arithmetic mean of Twelve Data hourly closes over each UTC calendar day.

Thus:
- daily date D means approximately 00:00 UTC -> 24:00 UTC;
- in Türkiye this corresponds to approximately **03:00 Istanbul -> 03:00 Istanbul next day**;
- it is not a Borsa İstanbul session;
- it is not a London session;
- it is not a New York 09:30-16:00 session;
- it is not a New York close-to-close return.

H3 `target_r3` is constructed from these governed daily references.

## 3. Hourly feature clock

The IRIS/SAGE intraday layer explicitly sets:

`TZ = "America/New_York"`

and freezes hourly features at:

**16:00 America/New_York on the feature_cutoff_date**

No hourly bar from the forecast issue date or later is allowed in that feature block.

Therefore intraday feature engineering is **New York-clock based**.

Approximate Istanbul conversion:
- 16:00 NY = 23:00 Istanbul during US daylight time;
- 16:00 NY = 00:00 Istanbul next day during US standard time.

Conversion must always be date-aware.

## 4. Forecast issuance clock

The prospective H3 authority explicitly creates the next weekday issue deadline at:

**08:00 America/New_York**

The code localizes 08:00 in `America/New_York` and then converts it to UTC for storage/governance.

Approximate Istanbul conversion:
- 08:00 NY = 15:00 Istanbul during US daylight time;
- 08:00 NY = 16:00 Istanbul during US standard time.

Thus operational issuance governance is **New York-clock based**.

## 5. CIG-D1 label clock

The original CIG-D1 document described its historical realization as previous available daily "close" -> current daily "close".

Subsequent semantic audit showed that the governed daily Gold series should **not** be called a conventional close-price series. It has a full-UTC-day daily-reference semantic.

Therefore the historical CIG-D1 target is not correctly described as:
- Turkey-session direction;
- New York-session direction;
- 08:00 NY -> close direction.

It is a direction label derived from the governed **UTC-day daily-reference series**.

This correction is binding.

## 6. Why this matters

The architecture combines:
- a **UTC-day target/reference**;
- **New York-clock hourly features**;
- a **New York-clock issue deadline**.

That is acceptable for H3 forecasting if the target definition remains frozen and clearly labelled.

But for D1 trading/execution it creates a clock mismatch:

> the historical daily label can contain price movement that occurred before the 08:00 New York decision time.

Therefore historical D1 label accuracy is not automatically executable post-signal accuracy.

## 7. Turkey clock status

`Europe/Istanbul` is currently used only for:
- human-readable conversion;
- execution planning for the user;
- audit displays.

It is **not** currently:
- a model target boundary;
- a feature cutoff boundary;
- an issuance boundary;
- a training-label boundary.

No result may be called a "Turkey-session forecast" unless a new target is explicitly defined and frozen in Europe/Istanbul time.

## 8. Binding terminology

From this date forward:

- **UTC-day label** = governed daily-reference target/realization.
- **NY feature clock** = 16:00 America/New_York anchor.
- **NY issue clock** = 08:00 America/New_York deadline.
- **Istanbul display clock** = date-aware conversion for user execution.
- **Post-issue execution label** = a newly constructed intraday outcome beginning strictly after the governed issue time.

Do not use "daily close" unless a source explicitly supplies and governs a close.

## 9. Consequence for the canonical CIG reconciliation

Before the exact 125-row CIG population is re-scored, the comparison must be framed as:

**Original:** UTC-day-derived historical label accuracy.  
**New:** post-08:00-New-York executable-clock accuracy.

The new label must not silently replace the original target. It is a separate execution evaluation of the unchanged signals.

## 10. Next authorized step

Recover/reproduce the exact canonical 145-row 2026 Jan-Jul D1 universe and the exact 125 4/4 consensus rows, then join those **same rows** to 15-minute XAU/USD and calculate outcomes beginning strictly after 08:00 New York.

No Turkey-session relabelling and no model retuning are authorized during that reconciliation.


## 11. Canonical CIG population recovery update

The exact 2026 Jan-Jul daily realization artifact has now been recovered:
`GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv`.

This confirms:
- the CIG historical realization layer is a **date-labelled daily reference series**;
- it is not a Turkey-session price series;
- it is not a New York 08:00-to-close price series;
- it must not be assigned an executable intraday timestamp.

The old snapshot contains 145 rows because 2026-02-27 and 2026-03-02 through 2026-03-06 are absent from that frozen snapshot. This is a data-coverage gap, not a timezone/session filter.

The exact 125 canonical consensus rows reproduce 93/125 = 74.40% daily-label accuracy. Re-scoring those identical rows after 08:00 New York gives 47.20% for 08:15->16:00 and 08:15->20:00, and 50.40% for 17:00->20:00.

Hence the mixed-clock warning in this authority is no longer provisional; it is empirically demonstrated on the exact canonical population.
