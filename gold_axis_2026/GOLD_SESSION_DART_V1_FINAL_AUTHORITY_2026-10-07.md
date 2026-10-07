# SESSION DART V1 — FINAL AUTHORITY

**Date:** 2026-10-07  
**Status:** COMPLETE / NOT PROMOTED / 2025 CLOSED

## Identity

SESSION DART V1 is the disagreement-aware causal router between:

- `S14_A1_PLUS_1H_FULL` — canonical Structural-IRIS
- `PATH_GLOBAL_1H` — canonical hourly PATH expert

DART updates only when the two experts disagree directionally.

For each matured disagreement:
- X=1 if PATH_GLOBAL is correct;
- X=0 if STRUCTURAL_IRIS is correct.

Frozen BOCPD rule:
- Beta(1,1) new-regime prior
- hazard = 1/20 per matured disagreement
- max run length = 120
- minimum matured disagreements = 8
- enter PATH when Pr(theta>0.5) >= 0.90 and q_path >= 0.60
- return Structural when Pr(theta>0.5) <= 0.10 and q_path <= 0.40

Only same-window disagreement rows with `end_utc <= current start_utc` may update the detector.

No H3 DART/SENTRY/AURORA ledger is consumed as session model input.

## Development gate

| Session | N | DART BA | Structural BA | UP recall | DOWN recall | Matured disagreements | Switches | Verdict |
|---|---:|---:|---:|---:|---:|---:|---:|---|
| Sobti Asia Afternoon | 175 | 52.76% | 52.76% | 50.53% | 55.00% | 57 | 0 | FAIL — no switch |
| Sobti Asia Morning | 170 | 49.77% | 49.77% | 55.10% | 44.44% | 61 | 0 | FAIL — no switch |
| Sobti Europe | 189 | 48.71% | 48.71% | 71.84% | 25.58% | 62 | 0 | FAIL — recall floor / no switch |
| Sobti NY/London | 190 | 51.62% | 53.26% | 49.48% | 53.76% | 58 | 2 | FAIL — 2024 accuracy / development BA |
| Sobti Late-US | 89 | 50.05% | 50.05% | 70.83% | 29.27% | 21 | 0 | FAIL — recall floor / no switch |
| WGC Asia | 102 | 47.36% | 47.36% | 82.61% | 12.12% | 21 | 0 | FAIL — recall floor / no switch |
| WGC Europe | 189 | 52.12% | 52.12% | 70.09% | 34.15% | 67 | 0 | FAIL — no switch |
| WGC US | 162 | 47.97% | 47.97% | 30.12% | 65.82% | 49 | 0 | FAIL — no switch |

## Observed state transitions

Only Sobti NY/London switched during development:

1. 2023-11-17: STRUCTURAL_IRIS -> PATH_GLOBAL
   - q_path = 0.7665
   - Pr(PATH superior) = 0.9167
   - matured disagreements = 9

2. 2024-03-28: PATH_GLOBAL -> STRUCTURAL_IRIS
   - q_path = 0.2125
   - Pr(PATH superior) = 0.0930
   - matured disagreements = 24

This mechanism was active, but its routed performance failed the frozen confirmation gate.

## Frozen 2025 status

No DART head passed the pre-2025 gate.

Therefore:
- 2025 transport was not opened;
- no 2025 metrics were used to rescue or retune DART;
- no thresholds or BOCPD settings were modified.

## Binding decision

1. SESSION DART identity and chronology are valid.
2. DART is **not promoted** as a session router.
3. No DART session head is eligible for 2025 transport under the frozen gate.
4. The absence of state changes in most windows is a valid model result, not a data failure.
5. Sobti NY/London demonstrates that the BOCPD mechanism can switch, but the resulting development performance is insufficient.
6. DART state/posterior history may still be used as upstream evidence when reconstructing SESSION AURORA, because AURORA historically uses SENTRY for fast entry and DART for slow exit.
7. No 2026 outcome was opened.
8. Next dependency model: **SESSION AURORA**.
