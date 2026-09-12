# Gold Control V1.61 — Short-Horizon Price-Discovery Result Checkpoint

**Status:** `RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC_COMPLETE`  
**Primary support gate:** `FAIL`  
**Evidence class:** `RETROSPECTIVE_SUCCESSOR_DIAGNOSTIC`  
**Production authority:** `FALSE`  
**Production writes:** `NONE`

## Frozen primary result

The pre-score frozen H5 price-discovery + realized-moments quantile-boosting challenger (`H5_PD_RM_QB`) did not pass the support gate.

| Period | Coverage | Accuracy | Balanced accuracy | MCC | UP / DOWN | Mean pinball |
|---|---:|---:|---:|---:|---:|---:|
| Formation 2024 | 15.42% | 51.28% | 46.12% | -0.1267 | 35 / 4 | 0.007130 |
| Validation 2025 | 21.61% | 72.55% | 52.22% | 0.1021 | 49 / 2 | 0.008992 |
| Test 2026 available | 14.29% | 43.48% | 50.00% | 0.0000 | 23 / 0 | 0.012781 |

The challenger improved mean pinball loss versus the H5 base in both 2025 and 2026, and passed validation coverage/MCC/both-direction checks. It failed the frozen balanced-accuracy floor in validation and failed coverage, balanced accuracy, MCC and both-direction checks in 2026. The 2026 directional surface again collapsed to one predicted class.

## Frozen ablations

- `H5_BASE_QB`: validation BA 52.38%, MCC 0.1627, coverage 17.97%; 2026 BA 50.00%, MCC 0, coverage 19.02%, 31 UP / 0 DOWN.
- `H5_RM_QB`: validation BA 48.39%, MCC -0.1059, coverage 19.92%; 2026 BA 50.00%, MCC 0, coverage 21.74%, 35 UP / 0 DOWN.
- `H3_PD_RM_QB` secondary diagnostic: validation BA 46.67%, MCC -0.1754, coverage 11.39%; 2026 BA 50.00%, MCC 0, coverage 11.04%, 18 UP / 0 DOWN.

## Interpretation lock

1. V1.61 is **not promoted**.
2. The high 2025 raw accuracy of the primary challenger must not be presented as robust direction skill because balanced accuracy is only 52.22% and signals are 49 UP / 2 DOWN.
3. Adding strictly lagged GC=F/GLD price-discovery proxies and realized moments improved distributional pinball loss but did not solve two-direction H5 robustness.
4. Same-day Yahoo daily bars remain forbidden at the 13:29 XAU forecast origin; GC=F remains a research proxy, not official CME settlement.
5. No V1.61 threshold, feature, horizon or model parameter may be repaired after this score.
6. Any successor must be a separately frozen hypothesis with a distinct scientific rationale; 2025/2026 remain researcher-visible retrospective diagnostics.
7. Future prospective shadow remains required for any thesis-strength promotion claim.

## CI evidence

Workflow run: `34721230225`  
Artifact: `10307135023`  
Artifact digest: `sha256:581370678a1fc5f161e3c60844faa94ac6b1e4980bcc80098cf460006fd3ae6d`

No canonical merge or production authority is authorized by this checkpoint.
