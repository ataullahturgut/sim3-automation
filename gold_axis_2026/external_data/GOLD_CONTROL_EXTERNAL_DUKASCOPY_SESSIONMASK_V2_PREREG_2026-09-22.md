# GOLD CONTROL — EXTERNAL DUKASCOPY SESSION-MASK CORRECTION V2 PREREGISTRATION

**Date:** 2026-09-22  
**Identity:** `EXTERNAL_DUKASCOPY_SESSIONMASK_V2_RESEARCH`  
**Trigger:** independent method audit after V1 external extension.  
**Runtime authority:** NONE.

## 1. Audit finding

The governed internal source uses exactly 276 recurring 5-minute local-time bins on normal weekdays.

The missing bins are:

`17:00, 17:05, ..., 17:55 America/New_York`

The staged V1 external spine retained 288 five-minute bins/day, including this 17:00–17:55 maintenance hour.

Although V1 source harmonization was already extremely high, this is a real construction mismatch and must be corrected before relying on the pre-2022 result.

## 2. Corrected external session

Rebuild the external Dukascopy-derived 5-minute daily spine for 2018–2021 using:

- exact bid/ask timestamp inner join;
- mid close = (bid + ask)/2;
- last close per UTC 5-minute bin;
- convert each bin to America/New_York;
- exclude all bins whose local time is 17:00 through 17:55;
- group by America/New_York calendar date;
- retain weekdays with at least 240 bars;
- drop zero-variance days.

Expected normal retained day: 276 bars.

No 2025 data are used.

## 3. Required rechecks

Before any corrected pre-2022 model test:

1. consolidated row uniqueness/sorting/finite-value audit;
2. exact overlap against governed 2020–2021 source;
3. close-return sign/correlation;
4. RV/DR correlation and scale;
5. high-risk state agreement;
6. frozen SQRT implementation reproduction on governed 2022–2024;
7. frozen direct-expert reproduction already established must remain unchanged in method identity.

## 4. Corrected pre-2022 rerun

Only after the corrected harmonization gate passes:

- rerun 2020/2021 SQRT parent using the exact frozen equations;
- rerun frozen direct experts and Router-V2-style yearly formation;
- rerun the single fixed hard-veto LTT safety test.

The V1 external result is superseded for methodological interpretation if V2 materially changes the 2020/2021 outcomes.

## 5. Governance

- correction is based on governed session structure, not on outcome optimization;
- no threshold tuning;
- no policy tuning;
- no production writes;
- no runtime promotion.
