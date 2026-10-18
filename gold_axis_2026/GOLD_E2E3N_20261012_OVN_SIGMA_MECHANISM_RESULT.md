# E2/E3 OVN V0 — 16:45 TR → next calendar day 09:00 TR

Status **REJECT / NO PROMOTION** for both primary hypotheses, under precommitted frozen rules in `GOLD_E2E3N_20261012_OVN_SIGMA_MECHANISM_PREREG.md` (commit 5709d3f). 2025/26 outcomes are repeatedly opened; neither was used to pick windows or rescue the primary test.

## Dataset and safety
Real Neon-derived R73B Dukascopy-family **overnight-midpoint** outcomes, Monday–Thursday only, 60 prior completed nights in **same provider stream**, rolling drift/volatility. 2023–25 EV/Duka versus direct Duka 2026 are never combined for parameter windows. N: 2023 145, 2024 205, DEV350; opened2025 204, opened2026 73. No macro event or HAR M15 data were used, so this is an ultra-low-capacity **overnight-only smoke test**, NOT the fully proposed E2/E3 system. No bank quotes, profit or live-signal claims.

## E2 conditional overnight direction, lower Brier better
| Period | N | Dynamic sigma20 | Constant sigma60 | Rolling UP-rate60 |
|---|---:|---:|---:|---:|
| 2023 | 145 | 0.25190 | 0.25060 | 0.25352 |
| 2024 | 205 | 0.25079 | 0.24974 | 0.25115 |
| 2025 (opened) | 204 | 0.24782 | 0.24989 | 0.25073 |
| 2026 (opened) | 73 | 0.25760 | 0.25248 | 0.25632 |
| **DEV 2023–24** | **350** | **0.25125** | **0.25010** | **0.25214** |

**E2 REJECT.** Dynamic sigma20 is worse than constant sigma60 in both DEV years, mean paired Brier improvement = -0.001151 (negative). Month-resampled 95% CI [-0.00238, 0.00020]. This reaffirms the theory caveat: volatility alone does not provide a hard reversal sign if expected drift does not change sign.

## E3 overnight magnitude above the hypothetical 0.20% hurdle
Event `I(|overnight log-return|>0.002)`; **not** actual bank net trade profitability.

| Period | N | Dynamic sigma20 | Constant sigma60 | Prior-event frequency60 |
|---|---:|---:|---:|---:|
| 2023 | 145 | 0.22817 | 0.22670 | 0.23077 |
| 2024 | 205 | 0.22387 | 0.23109 | 0.22751 |
| 2025 (opened) | 204 | 0.17251 | 0.18101 | 0.18396 |
| 2026 (opened) | 73 | 0.12005 | 0.11803 | 0.12030 |
| **DEV 2023–24** | **350** | **0.22566** | **0.22927** | **0.22886** |

DEV point estimate of benefit relative to const = **0.003618 Brier**, but 2023 goes the wrong way. Month-bootstrap 95% CI for benefit [-0.00246, 0.01007], probability benefit≤0 in resamples 12%. **E3 primary fails preregistered year-consistency gate → REJECT / NO PROMOTION** even if pooled result or opened 2025 looks positive. 2026 transport reverses.

Secondary 0.10% / 0.30% values are in committed JSON and month-loss ledger. No tuning/threshold switch. No real bank quote history means no trade/non-trade decision is established.

## Interpretation and future
New independent quantitative tests were performed with actual previously archived data and strictly causal prior-night rolling features. **No robust value-add** is established by this low-capacity *overnight only* mechanism. It does not rule out a genuinely different, pre-announced macro/HAR realized-volatility model or higher-quality prospective future data; any such successor must justify non-duplication against R15–R27, test true issue-time publication provenance, and start with a fresh pre-registration. Do not amend original gold model/manifest.

## Reproduce
Execute `sql/gold_e2e3n_20261012_ovn_volatility_nullpilot.sql` **read-only** against Neon Gold Control; it returns month-grouped sums of squared losses. `..._MONTHLY_LEDGER.csv` retains exactly those aggregates, and `..._SUMMARY.json` lists cohorts and 20,000 fixed-seed month-block bootstrap diagnostics. Sigma20 vs sigma60 and source partition details are frozen in prereg. No Neon writes occurred.
