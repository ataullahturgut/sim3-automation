# Gold Control — Macro Event Successor V1 Score Replay Change Control

Date: 2026-09-05
Engine: `MACRO_EVENT_SUCCESSOR_V1`
Scope: read-only historical research replay only

## Authorization

The user explicitly authorized proceeding with the historical score replay after the governed six-series research panel was successfully ingested to production Neon.

This change control authorizes **only** computation of the already-preregistered V1 score from the frozen source snapshot. It does not authorize a forecast, direction vote, selector/ensemble use, action mapping, runtime promotion, or Forecast/Decision Store writes.

## Frozen preregistration

Binding preregistration:
`GOLD_CONTROL_MACRO_EVENT_SUCCESSOR_V1_SCORE_PREREG_2026-09-05.md`

The following remain frozen and may not be changed after observing replay results:
- raw surprise = actual minus consensus;
- point-in-time sample standard deviation (`ddof=1`) from strictly prior complete-case events;
- minimum prior history = 24 events;
- no clipping/winsorization;
- gold signs: NFP negative, unemployment positive, AHE negative;
- equal component weights;
- state thresholds at +/-1.0 with breadth >=2;
- DEV/VAL/LOCK windows;
- complete-case only.

## Source snapshot

The replay must bind to the successful Neon ingestion snapshot:
- retrieval run: `6a18db17-6fb2-4bf8-a20b-f3b6d529ca8a`
- pipeline: `MACRO_EVENT_SUCCESSOR_V1_RESEARCH_DATA_PLANE_R1`
- complete-case months: 126
- six series, 756 observations
- excluded source months remain `2020-08` and `2025-10`.

No later row may be silently substituted into this V1 replay.

## Required replay controls

The implementation must:
1. read the six frozen series from Neon only;
2. verify 126 complete cases and 756 source observations;
3. bind to the exact retrieval run above;
4. standardize each event using only prior events;
5. prove prefix invariance/recompute equivalence;
6. emit a deterministic source fingerprint without publishing raw Investing.com values;
7. verify Forecast/Decision authority-store counts are unchanged before/after;
8. write no score rows to production Neon in this stage.

## Promotion boundary

A successful engineering replay does **not** itself approve the successor. The preregistration explicitly requires a separately frozen gold event-reaction source/window and validation contract before event-confirmed gold context or runtime promotion can be claimed.

Any modification of the V1 score after inspecting results requires a separately named successor revision/change-control. V1 must not be retuned in place.
