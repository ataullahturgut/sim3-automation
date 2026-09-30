# GOLD MONTHLY — Unified Alarm Matrix V1 Authority

**Date:** 2026-09-30
**Status:** PRE-REGISTERED / BINDING CONSOLIDATION
**Scope:** consolidate existing alarm signals only. No new thresholds, no forecast correction, no routing/model switching.

## 1. Evaluation rows

Use the binding APE-severity evaluation:
- targets 2021-11..2026-08
- 58 rows
- NORMAL: APE < 2.5%
- MEDIUM: 2.5% <= APE < 3.0%
- HIGH: APE >= 3.0%.

## 2. Columns

For every target month report:

- target
- origin
- forecast
- actual
- APE
- severity
- A
- B
- C
- D
- E
- G
- H
- I1
- I2
- T1_WGC
- T1 publication date
- T1 timely flag

Definitions are inherited unchanged from their binding authorities.

### T0 model/market alarms
- A = Cross-metal fragility
- B = Supported momentum underreaction (warning-only)
- C = Delayed rates catch-up (currently medium-error/low-event warning)
- D = Macro-Gold conflict
- E = Extreme-level/model disagreement (discovery-period/unvalidated)
- G = Post-liquidation / high-movement regime warning
- H = CFTC positioning shift (warning candidate)
- I1 = ETF flow deterioration (candidate transition warning)
- I2 = ETF redemption persistence (historically supported, regime-dependent warning)

### T1 report alarm
- T1_WGC = R2_WGC, two consecutive official WGC global ETF outflow reports.

## 3. Derived reporting columns

For readability only; these do not create new alarm rules:

- T0_STANDARD = A OR B OR C OR D OR H
- T0_ALL_VISIBLE = A OR B OR C OR D OR E OR G OR H OR I1 OR I2
- T0_PLUS_T1_STANDARD = T0_STANDARD OR T1_WGC
- ANY_VISIBLE = T0_ALL_VISIBLE OR T1_WGC

Also report the names of active signals in a text field.

These union columns are descriptive summaries only. They do not promote E/G/I to hard alarms.

## 4. Required summaries

Report:
- complete 58-row matrix;
- all HIGH rows with active alarms;
- all MEDIUM rows with active alarms;
- HIGH rows with no T0_STANDARD signal;
- HIGH rows with no T0_ALL_VISIBLE signal;
- HIGH rows with no ANY_VISIBLE signal;
- signal-by-signal event/hit/false-alarm counts under APE HIGH;
- pairwise overlap counts among A..I2 and T1_WGC;
- per-year signal counts.

## 5. Source artifacts

Use only frozen outputs:
- APE severity V3 artifact 11090497943
- ETF dynamic regime V2 artifact 11090919621
- WGC T1 V4 artifact 11093192454

No model rerun is required.

## 6. Governance

- No threshold retuning.
- No new Boolean alarm rule.
- No forecast correction.
- No routing/model switching.
- Signal statuses remain distinct; matrix presence does not imply validation equivalence.
