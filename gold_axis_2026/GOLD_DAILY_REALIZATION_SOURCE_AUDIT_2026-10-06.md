# GOLD DAILY REALIZATION SOURCE AUDIT

**Date:** 2026-10-06  
**Status:** BINDING SOURCE-SEMANTICS CORRECTION  
**Purpose:** determine exactly what the previously displayed `Gerçekleşen` values are and prevent clock semantics from being inferred from a date label.

## 1. Exact source of the numeric "Gerçekleşen" column

Recovered historical artifact:
`GOLD_DAILY_H1_V2_2026_GERCEKLESEN_TAHMIN_RECOVERED_2026-10-06.csv`

Columns include:
- `Tarih`
- `Önceki Gün Gerçek`
- `Gerçekleşen`
- model forecast columns.

The `Gerçekleşen` values were compared date-by-date with the pinned StakTrakr source:

- repository: `lbruton/StakTrakr`
- commit: `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`
- file: `data/spot-history-2026.json`
- metal: `Gold`.

Result:

**145 / 145 recovered daily `Gerçekleşen` values match the pinned StakTrakr Gold daily-history value exactly.**

Examples:
- 2026-01-02: `Gerçekleşen = 4386.85` -> StakTrakr Gold = `4386.85`
- 2026-01-05: `4436.70` -> `4436.70`
- 2026-01-28: `5277.80` -> `5277.80`
- 2026-07-31: `4102.17` -> `4102.17`.

Therefore the numeric `Gerçekleşen` column was **not invented and was not calculated from the forecast**. It is a copied historical daily Gold reference from the pinned StakTrakr history.

## 2. Critical timestamp correction

The StakTrakr year-history rows carry timestamps such as:

`2026-01-02 12:00:00`

However this must **not** be interpreted as "the Gold price observed at 12:00".

The StakTrakr pipeline itself documents that daily-history buckets are stamped at **synthetic noon UTC** and that this timestamp is a **calendar-day label, not an observation time**.

The seed updater also explicitly constructs history timestamps as:

`<date> 12:00:00`

when converting daily API/history values into year-history entries.

Therefore:
- 12:00 is not a legitimate execution timestamp;
- the source date may be used as a daily label;
- no intraday buy/sell clock may be inferred from that timestamp.

## 3. What "Gerçekleşen" actually means

Correct terminology:

**Gerçekleşen = pinned StakTrakr daily Gold reference value for that calendar date.**

It is **not proven to be**:
- New York close;
- London close;
- Istanbul close;
- 12:00 UTC spot print;
- UTC full-day arithmetic average.

The old label direction is simply:

`Gerçekleşen(today) > Önceki Gün Gerçek` -> UP  
otherwise -> DOWN.

This is the label used to reproduce the canonical CIG-D1 2026 Jan-Jul result.

## 4. Correction to the prior "UTC daily average" inference

The prior semantic audit found that StakTrakr levels/directions were close to a Twelve Data UTC-calendar-day hourly-mean reconstruction.

That is a useful **cross-provider similarity check**, but it does **not** prove that the StakTrakr value is itself a full-UTC-day average.

Source lineage now takes precedence over similarity inference.

Therefore the statement:

> "the governed Stak daily value is a full-UTC-day average"

is **superseded / unsupported**.

Correct statement:

> "the Stak value is a daily calendar-date reference whose exact intraday observation/fixing clock is not established by the stored synthetic noon timestamp."

## 5. Effect on the 74.40% CIG result

The exact 125-row CIG reconstruction remains numerically valid:

- consensus rows: 125
- correct daily labels: 93
- daily-label accuracy: 74.40%.

But its meaning is now strictly:

**74.40% accuracy against the pinned StakTrakr daily date-labelled Gold reference direction.**

It is not an accuracy claim for a known intraday interval.

## 6. H3 call-by-call "Gerçekleşen"

In `GOLD_H3_AURORA_V1_2026_CALL_BY_CALL.md`, the displayed `Gerçekleşen` field is a direction (UP/DOWN), not an independently observed intraday price.

It is derived from the sign of the stored H3 target return `target_r3`.

Thus:
- `Gerçekleşen = UP` if `target_r3 > 0`;
- `Gerçekleşen = DOWN` otherwise.

The corresponding `H3 getiri` is that stored target return shown as percent.

It must not be described as a return measured from the forecast issue timestamp unless the target clock is separately proven.

## 7. Binding rules from this audit

From now on:

1. Numeric daily `Gerçekleşen` = pinned Stak daily reference value.
2. Stak daily `12:00:00` = synthetic date label, not an executable market timestamp.
3. "full UTC daily average" is no longer a binding semantic description of Stak daily values.
4. CIG 74.40% remains a daily-reference-label score only.
5. Any tradable-time evaluation must use an independently timestamped intraday source and an explicitly frozen start/end clock.


## 8. Source-vintage mismatch found

A second, more important issue was found after tracing the `Gerçekleşen` values.

The recovered daily realization ledger is tied to the older pinned StakTrakr history:
- ref `ed2e549f82ba0d1cd3ca32842b82d3888d301e01`.

The clean H3/AURORA prospective architecture later froze its own daily price snapshot from:
- `FROZEN_STAK_REF = 54fdf1c8d39b7b6c7b874d0f30f784296e886044`.

Across the 145 recovered Jan-Jul daily rows:
- **34 / 145** Gold level values differ between the old realization ledger and the later H3 frozen Stak snapshot;
- **10 / 145** daily UP/DOWN labels differ.

On the exact 125 canonical CIG consensus rows:
- old recovered label: **93/125 = 74.40%**
- later H3 frozen-source daily direction: **88/125 = 70.40%**
- **9 / 125** daily labels differ.

Therefore the published 74.40% CIG figure was produced by evaluating the H3-derived consensus against a **different Stak data vintage/source snapshot** than the later clean H3 frozen daily price snapshot.

This does not make the old score arithmetically false, but it creates a material **source-vintage mismatch**. The 74.40% figure must no longer be treated as a source-consistent clean H3/CIG performance statistic.

Until a single frozen daily source/vintage is selected and the expert signals and labels are replayed consistently from that same source contract, the canonical CIG score is:

**historical mixed-vintage diagnostic, not a clean source-consistent validation result.**
