# GOLD V34/V22/BASE14 — staged live integration, 30 October 2026

**Status:** STARTED; NEVER claim production forecast or live V22 signal until strict prospective controls pass. Monthly calibration remains suspended and portfolio history unchanged.

## Phase outcomes

| Stage | Tested evidence | Result |
|---|---|---|
| 1 — Source recovery | Neon canonical XAU 2026-10-29 21:00Z, GVZ/VIX 2026-10-29, DGS10/EFFR 2026-10-28 | PASS five headline series |
| 2 — Original implementations located | V34 `gold_v34_ann_replay.py`, weekly `gold_weekly_h1_ann_4metal_v1.py`, V22 `risk_v22_slope_decision.py`, V33 risk replays in `research/gold-v34-ann-weekly-monthly-alert-position-20261027` | Located, not current executors |
| 3 — Data-origin dependency verifier | `gold_weekly_live_dependency_gate_v2.py` with nine offline failure/safety invariants, read-only Neon audit | PASS execution; **BLOCKED_NOT_LIVE** status is expected |
| 4 — Reproducible V34 H1 *forward* runner | Original 16D AU/AG/PT/PD, expanding fit, training-only scaling, no target-week dependence; original model parity test | NOT YET PROVEN |
| 5 — V22/BASE14 prospective scorer | Full as-of BASE14/CFTC21 panel, original V22 7 rules + previous-day state; independent replay comparison | NOT YET PROVEN |
| 6 — Immutable firstprint issue | Target dates, checkpoint SHA256, input snapshot SHA256, source availability timestamps, no late sources; Neon writes only once all gates pass | NOT ENABLED |
| 7 — UI and automated issuance | Read current firstprint records, fail-closed health banner, scheduler running and end-to-end tests | NOT ENABLED |

## Actual Neon source situation at this checkpoint

- Approved main five-series market freshness: READY, but this is **not** enough to run original V34.
- `gold_monthly_h1.staktrakr_2026_git_snapshot_daily_v1` has AU, AG, PT, PD at 2026-10-16, classified `RESEARCH_GIT_SNAPSHOT_NOT_PIT`; raw historical research extension to 2026-10-23 is in the research branch only, without firstprint authority.
- On Friday 30 October 07:41 UTC, next not-yet-started target is week Monday 2026-11-02; its origin week (2026-10-26 through 2026-10-30) is not complete before Friday NY17, and no aligned four-metal records are present for that origin.
- `gold_weekly_live.weekly_forecast_records` count=0, `gold_weekly_live.downside_signal_records` count=0.
- `public.decision_runs` and `public.decision_signal_snapshots` are both empty; historic engine executions are from September, not current model issuers.
- The V34 2026 replay includes a 2026-02-27 externally substituted reference marked NOT PIT. Source-specific experiments must not be treated as a validated production price stream.

## Invariants

1. No substitution of indicative `XAU_SPOT_XAUS` or `XAU_EOD_TWELVE_NY17` for original four-metal 16D weekly ANN input.
2. No firstprint classification for research Git snapshots or undated revisions.
3. Current-week forecast must not be backdated after target week began; originating Friday NY17 close must have occurred.
4. Original V22 and BASE14 must preserve source provenance, frozen thresholds and chronological prior state. Retrospective 2024–2026 scoring is not current trading advice.
5. No table changes, model training, prediction publication, money movement, or application promotion in Stage 3.

## CI evidence

GitHub Actions: https://github.com/ataullahturgut/sim3-automation/actions/runs/41021628533 — nine offline tests PASS and read-only production Neon audit PASS; audit output explicitly `BLOCKED_NOT_LIVE`.

**Next implementation:** independently reproduce the frozen V34 weekly model at a historical origin without target-week actuals, then verify byte-level numerical parity; only after this proceed to a forward-run adapter with original source/feature checks. V22 as-of scorer follows the same process.