# Gold Control V1.60 — Final Regime Selector Result Checkpoint

**Status:** `RETROSPECTIVE_FINAL_ARCHITECTURE_DIAGNOSTIC_COMPLETE`  
**Support gate:** `FAIL`  
**Evidence class:** `RETROSPECTIVE_FINAL_ARCHITECTURE_DIAGNOSTIC`  
**Production authority:** `FALSE`  
**Production writes:** `NONE`  
**Stopping rule:** `FINAL_NORMAL_DAY_RETROSPECTIVE_ARCHITECTURE_EXPERIMENT_V151_V160_SEQUENCE`

## Frozen experiment outcome

The frozen V1.60 selector did **not** promote any normal-day H20 direction signal. It returned `NO_SIGNAL` for every scored origin in formation 2024, validation 2025, and the available 2026 test window.

| Period | Selector coverage | Selector signals | Support |
|---|---:|---:|---|
| Formation 2024 | 0.0% | 0 | NO_SIGNAL |
| Validation 2025 | 0.0% | 0 | FAIL |
| Test 2026 available | 0.0% | 0 | FAIL |

This is not an implementation failure. The workflow, frozen chronology tests, regime tests, stopping-rule tests, retrospective audit, and artifact upload all completed successfully. The selector abstained because neither frozen expert satisfied the causal same-regime eligibility requirements at any scored origin.

Primary ineligibility reasons were:

- `INSUFFICIENT_SIGNAL_HISTORY`
- `DEGENERATE_PREDICTED_CLASS_SUPPORT`
- `BALANCED_RELIABILITY_BELOW_FLOOR`
- early-window `REGIME_UNKNOWN`
- a small number of `INSUFFICIENT_REALIZED_CLASS_SUPPORT` cases for the driver-corrected expert.

## Expert diagnostics retained unchanged

### LEGACY_RTQ_R126

- Validation 2025: coverage `58.92%`, accuracy `77.46%`, balanced accuracy `50.00%`, MCC `0.000`, UP/DOWN signals `142/0`.
- Test 2026 available: coverage `72.97%`, accuracy `70.37%`, balanced accuracy `69.23%`, MCC `0.4947`, UP/DOWN signals `88/20`.

### DRIVER_RTQ_R126

- Validation 2025: coverage `51.45%`, accuracy `71.77%`, balanced accuracy `49.44%`, MCC `-0.0554`, UP/DOWN signals `123/1`.
- Test 2026 available: coverage `77.03%`, accuracy `69.30%`, balanced accuracy `67.59%`, MCC `0.4714`, UP/DOWN signals `95/19`.

The corrected broad-USD / real-yield parent therefore did not solve the 2025 one-class problem and did not improve on the legacy RTQ in the frozen 2026 balanced-accuracy comparison.

## Interpretation lock

1. The V1.60 selector **fails the frozen support gate** and is not promoted.
2. The zero-coverage result must not be repaired by changing thresholds, regime definitions, support minima, experts, horizon, features, or same-period rules after scoring.
3. The 2026 legacy H20 RTQ result remains an important retrospective conditional signal, but 2025 demonstrates that it is not stable two-direction evidence across regimes.
4. The normal-day retrospective model-search sequence V1.51–V1.60 is closed under the frozen stopping rule.
5. Future work for normal-day H20 may proceed only as a separately preregistered / prospective research line; it must not reinterpret 2025/2026 as fresh blind evidence.
6. Stronger role-specific lanes remain separate: monthly level forecasting, macro-event direction, regime/risk/context. They must not be collapsed into an equal-vote universal direction engine.

## CI evidence

Workflow run: `34718421969`  
Artifact: `10305892266`  
Artifact digest: `sha256:e6f53108755abdfae58c3131ec47ee5f41a23a91812e6acbbb517ff903ac4d45`

No canonical merge or production authority is authorized by this checkpoint.
