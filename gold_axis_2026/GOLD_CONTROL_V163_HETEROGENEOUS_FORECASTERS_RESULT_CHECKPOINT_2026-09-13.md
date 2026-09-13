# Gold Control V1.63 — Heterogeneous Forecasters Result Checkpoint

Date: 2026-09-13  
Branch: `gold-v163-heterogeneous-forecasters-research`  
Draft PR: #54  
Parent: V1.62 negative context-aware meta-forecast research  
Pre-score freeze commit: `2d4465492557effeabfb195184715a02f2e80d1b`  
Successful implementation head: `7c2bfeed9f2b11f4a206e61dc944cce18cce2b8a`  
Workflow run: `34752232625` — SUCCESS  
Artifact: `10315927143`  
Artifact digest: `sha256:b4ed9be7774485e67fad27ddbf2aa7d786ff5ba16efd2797052bbc41b219d12b`

Evidence class: `RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_NOT_FRESH_OOS`.

## Frozen question

Can genuinely heterogeneous information-block forecasters create stable 1D/3D predictive skill and complementary errors at the exact NY17 XAU target clock before any new dynamic selector is attempted?

The contract, expert definitions, training scheme, skill thresholds and diversity thresholds were frozen before scoring. `AUTO_SELECTOR=OFF`, `AUTO_ENSEMBLE=OFF`, production authority is false and production writes are none.

## Implementation note

The first workflow attempt stopped before result reporting because V1.49 NY17 columns and V1.61 rich-panel columns shared five names (`nasdaq_ret`, `sp500_ret`, `xag_ret`, `xpt_ret`, `xpd_ret`), which caused pandas merge suffixes and a deterministic missing-column exception. The contract was not changed. The implementation was repaired only by explicitly replacing those colliding NY17 research columns with the frozen V1.61 rich-feature versions required by the contract. The successful rerun then completed all five experts and both horizons.

## Expert pool

- `GOLD_RIDGE`: gold-only lagged return, momentum and realized-volatility features.
- `SESSION_RM_RIDGE`: Europe/US-session returns plus realized moments.
- `PRICE_DISCOVERY_HGB`: strict-previous-date GC futures and GLD price-discovery features.
- `MACRO_CROSS_RIDGE`: cross-market, broad-USD and real-yield features.
- `FULL_HGB`: union of all above plus FAST/SLOW/monthly direction as role-preserving context features, never flat votes.

All experts use recursive rolling-origin fitting, `j+h<=t` target maturity, a 252-origin training cap and at least 180 matured targets. No random split or whole-sample preprocessing is used.

## 1D results

Common prediction rows: 404.

### Validation 2025 (N=203)

| Method | Brier | Log loss | Balanced accuracy | MCC |
|---|---:|---:|---:|---:|
| P50 | 0.2500 | 0.6931 | 0.5000 | 0.0000 |
| Expanding frequency | **0.2468** | **0.6868** | 0.5000 | 0.0000 |
| GOLD_RIDGE | 0.2537 | 0.7012 | 0.4831 | -0.0432 |
| SESSION_RM_RIDGE | 0.2583 | 0.7260 | 0.5243 | 0.0489 |
| PRICE_DISCOVERY_HGB | 0.2560 | 0.7099 | 0.5144 | 0.0315 |
| MACRO_CROSS_RIDGE | 0.2490 | 0.6924 | 0.5389 | 0.0855 |
| FULL_HGB | 0.2544 | 0.7064 | **0.5508** | **0.1073** |

### Available 2026 test (N=167)

| Method | Brier | Log loss | Balanced accuracy | MCC |
|---|---:|---:|---:|---:|
| P50 | **0.2500** | **0.6931** | 0.5000 | 0.0000 |
| Expanding frequency | 0.2539 | 0.7010 | 0.5000 | 0.0000 |
| GOLD_RIDGE | 0.2736 | 0.7438 | 0.4941 | -0.0121 |
| SESSION_RM_RIDGE | 0.2723 | 0.7703 | **0.5219** | 0.0443 |
| PRICE_DISCOVERY_HGB | 0.2706 | 0.7382 | 0.4782 | -0.0435 |
| MACRO_CROSS_RIDGE | 0.2712 | 0.7450 | 0.5126 | 0.0260 |
| FULL_HGB | 0.2738 | 0.7470 | 0.5004 | 0.0009 |

No 1D expert passes the frozen skill gate in both 2025 and 2026.

## 3D results

Common prediction rows: 400.

### Validation 2025 (N=201)

| Method | Brier | Log loss | Balanced accuracy | MCC |
|---|---:|---:|---:|---:|
| P50 | 0.2500 | 0.6931 | 0.5000 | 0.0000 |
| Expanding frequency | **0.2380** | **0.6690** | 0.5000 | 0.0000 |
| GOLD_RIDGE | 0.2400 | 0.6771 | 0.5284 | 0.0881 |
| SESSION_RM_RIDGE | 0.2545 | 0.7188 | 0.4797 | -0.0799 |
| PRICE_DISCOVERY_HGB | 0.2518 | 0.6987 | 0.5142 | 0.0314 |
| MACRO_CROSS_RIDGE | 0.2382 | 0.6727 | **0.5462** | **0.1083** |
| FULL_HGB | 0.2584 | 0.7206 | 0.5090 | 0.0205 |

### Available 2026 test (N=165)

| Method | Brier | Log loss | Balanced accuracy | MCC |
|---|---:|---:|---:|---:|
| P50 | **0.2500** | **0.6931** | **0.5000** | 0.0000 |
| Expanding frequency | 0.2511 | 0.6955 | 0.5000 | 0.0000 |
| GOLD_RIDGE | 0.3042 | 0.8197 | 0.4056 | -0.2214 |
| SESSION_RM_RIDGE | 0.2613 | 0.7203 | 0.4933 | -0.0168 |
| PRICE_DISCOVERY_HGB | 0.2803 | 0.7617 | 0.4556 | -0.0953 |
| MACRO_CROSS_RIDGE | 0.3035 | 0.8385 | 0.4656 | -0.0822 |
| FULL_HGB | 0.2921 | 0.8021 | 0.4811 | -0.0385 |

No 3D expert passes the frozen skill gate in both 2025 and 2026.

## Diversity diagnostic

The V1.63 information blocks did succeed at creating substantially more heterogeneous probability paths than V1.62's near-duplicate experts. This is a descriptive post-run diagnostic; because zero experts pass the skill gate, it does not make a selector eligible.

Across 2025 plus available 2026:

- 1D pairwise probability correlations range from approximately -0.03 to 0.44; squared-error correlations from about 0.05 to 0.49.
- 3D pairwise probability correlations range from approximately -0.04 to 0.42; squared-error correlations from about 0.33 to 0.60.
- Pairwise unique-win shares are generally close to 50/50, so the experts genuinely disagree and take turns being locally less wrong.

Therefore the V1.62 problem has been decomposed more precisely: **expert diversity is no longer the main bottleneck; stable predictive skill is.**

## Scientific decision

`V1.63 = FAIL / NEGATIVE SKILL-GATE RESULT`.

- Skill-passing experts at 1D: none.
- Skill-passing experts at 3D: none.
- Future selector eligibility: false at both horizons.
- Meta-selector scoring inside V1.63: forbidden and not performed.
- No production or trading claim is made.

The strongest near-signals are unstable across time. FULL_HGB reaches 1D balanced accuracy 0.5508 in 2025 but loses probabilistic quality and falls to approximately chance in 2026. MACRO_CROSS_RIDGE reaches 1D balanced accuracy 0.5389 in 2025 and 3D balanced accuracy 0.5462 in 2025, but its 2026 Brier/log-loss deteriorate sharply. This points to nonstationary / regime-dependent signal quality rather than a simple lack of information-block diversity.

## Next legitimate hypothesis

Do not revive CRASE or another selector yet. A new frozen version should target **temporal robustness inside the forecaster**. The defensible next experiment is a regime-adaptive/forgetting forecaster in which training emphasis can change using only matured prior origins, while the same heterogeneous blocks remain separate. Candidate mechanisms include predeclared exponential forgetting or a small state-dependent gating model inside the forecaster, not legacy engine voting. Any such experiment must retain P50 and expanding-frequency anchors, use proper probability scores and require 2025-to-2026 stability before a selector becomes eligible.

Academic basis remains consistent with dynamic model uncertainty (Raftery, Kárný & Ettler, 2010, DOI 10.1198/TECH.2009.08104), conditional predictive ability (Giacomini & White, 2006, DOI 10.1111/j.1468-0262.2006.00718.x), superior-set discipline (Hansen, Lunde & Nason, 2011, DOI 10.3982/ECTA5771) and proper probabilistic scoring (Gneiting & Raftery, 2007, DOI 10.1111/j.1467-9868.2007.00587.x).
