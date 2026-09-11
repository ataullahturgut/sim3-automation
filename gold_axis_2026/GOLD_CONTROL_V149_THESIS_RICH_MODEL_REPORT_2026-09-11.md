# Gold Control V1.49 — Thesis Rich Model Research Report

Date: 2026-09-11  
Authority: `GOLD_CONTROL_PROJECT_MANIFEST.md` v1.49, Section 19  
Evidence class: `RETROSPECTIVE_HISTORICAL_RECONSTRUCTION_NOT_PROSPECTIVE`

## Executive conclusion

The richer short-horizon hypothesis was implemented and replayed without random splits, future targets, whole-sample scaling or production writes. It did **not** establish a promotable 1D or 3D model. The 1D challenger was worse than P50. The 3D challenger was better than P50 but not better than the expanding-frequency benchmark, and its calibration was weak. The development block-selection sample was too small for a scientific incremental-content claim.

Monthly evidence is unchanged: VW is the strongest point-estimate model in the 19-month retrospective outer sample, but superiority over RW is not established at 5%. DMA/DMS/IDMA complementarity remains blocked by missing legitimate same-origin PIT forecasts.

## Canonical and recovered evidence

The work started from canonical `c4a477bb628e1be1c45628297da7f2a1acd67f87` on `gold-r4-direction-engine`, manifest v1.49. Market Shock V3 was recovered from historical research branches and imported only as non-promoted evidence. It is an event-confirmation challenger, not a daily direction engine.

The recovered Macro Event–Market Shock joint audit reports 5 shocks in 21 event windows versus 1 in 84 matched controls (Fisher one-sided p=0.00109584), 5/5 initial sign concordance and only 2/5 continuation. Therefore a 1D/3D continuation claim remains `NOT_PROVEN`.

## Monthly programme

| Finding | Result |
|---|---:|
| Common PIT-safe models | VW, Patch, Momentum, RW |
| Common target months | 43 (2023-01..2026-07) |
| Seven-view VW/DMA/DMS/IDMA/Patch/Momentum/RW common PIT sample | 0 |
| Outer sample | 19 months (2025-01..2026-07) |
| VW MAE / RMSE | 132.561 / 176.076 |
| RW MAE / RMSE | 176.053 / 216.326 |
| VW vs RW HAC squared-loss p-value | 0.0917 |
| Final status | `NOT_PROVEN` |

VW has the best point error, but no universal winner, proven ensemble, selector or regime weighting may be claimed. DMA/DMS/IDMA remain `BLOCKED_PIT` for same-origin complementarity.

## Rich short-horizon panel

The target clock is exact unique Twelve Data XAU/USD 1-minute 16:59 America/New_York, stored with NY17 semantics. Cross-market closes are joined only from an earlier governed origin. Employment and inflation events are admitted only when `available_as_of <= origin`; no event is represented by an explicit zero-event state.

| Block | Complete origins | Disposition |
|---|---:|---|
| B0 gold history/moments | 565 | mandatory baseline |
| B1 XAG/XPT/XPD | 585 | incremental value not proven |
| B2 rates/FX | 223 | development complete cases unavailable |
| B3 equity/risk | 97 | development complete cases unavailable |
| B4 Gold Control states | limited to later history | not reselected after outer visibility |
| B6 Macro Event employment/inflation | 585 | apparent development gain; inference blocked by n=12/6 |

The estimator universe was frozen before scoring: logistic ridge C=0.1, logistic ridge C=1 and depth-2 histogram gradient boosting. At every origin the candidate and Platt calibration used only matured prior predictions.

## Short-horizon results

| Horizon | N | Model Brier | P50 Brier | Frequency Brier | Model log loss | Frequency log loss | Balanced accuracy | Calibration intercept | Calibration slope | Status |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1D | 371 | 0.252625 | 0.250000 | 0.250165 | 0.698424 | 0.693485 | 0.4899 | 0.0790 | 0.0490 | `NOT_PROVEN` |
| 3D | 369 | 0.244200 | 0.250000 | 0.244289 | 0.682114 | 0.681774 | 0.5000 | 0.2490 | 0.1946 | `NOT_PROVEN` |

The 3D Brier improvement against P50 is real in this retrospective sample, but it is only 0.000089 better than expanding frequency while log loss is slightly worse. This is not a defensible predictive promotion. The 3D labels overlap, so an IID superiority statement is prohibited; no superiority claim is made.

Compared with the retained HS-SDL-DMA baseline, the new 1D Brier (0.252625) is lower than 0.254468 and the 3D Brier (0.244200) is lower than 0.255404. This is descriptive improvement only, not proof, because origin universes and contracts are not identical.

## Answers to the thesis questions

- **VW plus DMA/DMS/IDMA?** `BLOCKED_PIT`; complementarity cannot be inferred from research-only forecasts.
- **Patch and Momentum incremental?** Not proven on the small common monthly panel.
- **Simple versus complex monthly combination?** Complex integration was not eligible; simple/RW remain mandatory anchors.
- **RW anchoring?** Still required by governance and weak statistical separation.
- **State-predictable relative performance?** `NOT_PROVEN`.
- **Strongest monthly architecture?** VW by point error; promotion remains `NOT_PROVEN`.
- **Short-horizon gain?** B6 showed a development signal, but n=12/6 makes it `BLOCKED_INSUFFICIENT_SAMPLE`. B1 did not pass both horizons; B2/B3 lacked development complete cases.
- **FAST/SLOW incremental over richer features?** `NOT_PROVEN`; later-history state coverage prevents legitimate reselection after outer visibility.
- **Did 1D/3D beat baseline?** 1D no. 3D beat P50 but not expanding frequency; therefore no.
- **Calibration acceptable?** No; slopes 0.049 and 0.195 are too weak for user-facing probability.
- **Statistical superiority?** Not established.
- **Prospective shadow?** A research observation-only shadow can be frozen, but not with `PROSPECTIVE_SHADOW_READY` promotion status. It must collect genuinely unseen outcomes before evaluation.
- **Production ready?** No.

## Validity and governance

Chronology, 3D maturity, prefix-invariance and deterministic replay tests passed in GitHub Actions. No accepted leakage or PIT violation was found in admitted features. Insufficient PIT coverage was kept as a blocker; it was not repaired with interpolation, alternate providers or final-vintage backdating.

`AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`. No production forecast, decision or trading authority was written. Production Neon writes: NONE.

## Legitimate next experiment

Outer outcomes are visible, so the same 2025-2026 window cannot be used to invent and validate another architecture. The defensible next step is to freeze an observation-only prospective shadow with B0 as the mandatory baseline and B6 as a separately reported sparse event specialist. B1/B2/B3/B4 enter only after exact prospective collection clocks are operational. Promotion requires predeclared Brier/log-loss/calibration thresholds over genuinely unseen matured origins.

## Academic basis

The design follows rolling-origin evaluation (Tashman, DOI 10.1016/S0169-2070(00)00065-0), leakage discipline (Hewamalage et al., DOI 10.1007/s10618-022-00894-5), proper probabilistic scoring and calibration (Gneiting et al., DOI 10.1111/j.1467-9868.2007.00587.x), predictive accuracy comparison (Diebold–Mariano, DOI 10.1080/07350015.1995.10524599), conditional predictive ability (Giacomini–White, DOI 10.1111/j.1468-0262.2006.00718.x), and superior-set discipline (Hansen–Lunde–Nason, DOI 10.3982/ECTA5771). These authorities justify the test design, not a positive result.
