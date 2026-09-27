# GOLD MONTHLY — BOOSTING STAGE 1 CANONICAL BASELINES REPORT

Date: 2026-09-27
Status: **STAGE 1 COMPLETE — PASS**
Scope: DEV 2022-04..2024-12 only (n=33)
2025/2026: NOT OPENED / NOT EVALUATED

## Protocol
- Gold-only next-month log-return target.
- Forecast price = origin-known previous monthly Gold price × exp(predicted Gold log return).
- Frozen 8 VW-MIDAS predictors.
- Raw tree inputs; no scaling.
- Expanding-origin chronological training.
- No hyperparameter selection in Stage 1.
- No random split.
- Legacy LightGBM/CatBoost results not used for training or selection.
- Deterministic replay: PASS.
- DB: READ_ONLY.
- Authority invariants unchanged.

## Results

| Model | DEV SigmaAE | MAE | RMSE | Direction |
|---|---:|---:|---:|---:|
| **CatBoost Ordered** | **1460.4339** | **44.2556** | 57.8094 | 20/33 = 60.61% |
| Random Forest anchor | 1614.4908 | 48.9240 | 61.9796 | 20/33 = 60.61% |
| XGBoost canonical | 1778.0649 | 53.8808 | 66.4131 | **21/33 = 63.64%** |
| GBRT canonical | 1801.8648 | 54.6020 | 69.5902 | 19/33 = 57.58% |
| LightGBM canonical | 1832.5777 | 55.5327 | 69.9234 | 20/33 = 60.61% |

## Interpretation
- CatBoost is the clear Stage-1 price-error leader.
- XGBoost has the highest direction count but poor price error under its untuned canonical baseline.
- GBRT and LightGBM canonical defaults are too aggressive / poorly matched to this small monthly sample; they remain eligible for Stage 2–4 controlled ablations because the literature supports tuned low-capacity variants.
- Random Forest is only a comparator and is not promoted as a Boosting-family winner.
- Stage 1 does not justify using the legacy Sept-25 tuning results as official evidence.

## Comparison with project leaders
CatBoost Stage-1 SigmaAE 1460.43 improves substantially over the deferred DMA/DMS band (~1486–1490), but remains above the strongest existing nonlinear project families (~1413–1416). Therefore the Boosting family is promising enough to continue, but is not yet a project leader.

## Provenance
- Run ID: 36311943183
- Job ID: 108599472280
- Commit: 84fc59d6d58bf2aff6f2c37274eb074a43278985
- Artifact ID: 10929616178
- Artifact SHA256: ac22e4fb177c24fe33530ecd9cc25ff0cf8706f29faf28933cb51f0fd638e199
- Deterministic payload SHA256: 575df96457fa798ef9f005e08a1e14047e1b467485f053f9ae9a1d83c6f7d8a8

## Next
Stage 2 only: Target & Loss Ablation.
Do not proceed automatically beyond Stage 2.

## Kontrol ve Uyum Özeti
- Stage 1: PASS.
- Gold-only: PASS.
- Frozen 8 features: PASS.
- No hyperparameter tuning: PASS.
- Random split: NONE.
- 2025/2026 opened: NO.
- Determinism: PASS.
- DB writes: NONE.
- Legacy results used for selection: NO.
