# Gold DAY/OVN—2020, 2021, 2022 training-start preregistration (2026-10-08)

## User objective
Use previously audited 2020 and 2021 observations rather than silently dropping them, and evaluate 2026 as the central practical stress year when a **same-source, mature and independently verified** quote panel exists.

## Frozen independent historical training comparison
Source and labels: authoritative 2020-2025 EV Trading Labs Dukascopy-derived M15 BID private data/accepted DAY + OVN labels. Use the already source-overlap-validated official full 2020-2026 Cboe GVZ history, but restrict to data dated strictly before decision date. Previously named models retain their original fixed features and hyperparameters: BASE_LOGIT; SHAPE_LOGIT; SHAPE_GVZ_LOGIT; SHAPE_GVZ_HGB; VIX_GVZ_LOGIT; VIX_GVZ_HGB. The Cboe VIX downloaded source must use the same quote vintage and previous-day availability rule for every training start.

TRAIN_2020 starts from first eligible 2020 decision with properly matured features; TRAIN_2021 starts 2021; TRAIN_2022 starts 2022. In every case evaluate **exact same eligible 2023/2024 dates** with model re-fit at the start of each calendar month using fully matured prior labels, and the **exact same** retrospective 2025 dates using one frozen fit at 2025-01-01. Model parameter selection, window choice and confidence threshold NOT tuned against 2025/2026. 2020/2021 are historical training, never labeled unseen tests for these variants.

Report BA, accuracy, N, UP/DOWN recall, Brier, log loss by year/model/window/history; paired identical-date rescues/breaks and uncertainty versus 2022 history; outcomes on source-validation failure MUST produce blocked status, not invented BA. Friday 64-hour holds are excluded from weekday 16-hour comparisons. A longer history may help or hurt. 2025 was previously reviewed and is NOT truly prospective.

## 2026 crucial holdout / source policy
2026-01-01 .. **2026-10-08 (only bars matured at execution time)**: do not train/select model/feature/window/gate on 2026 outcomes. Preserve 2026 as independent calendar period. The source identity of 2020-2025 main BID/ASK feed cannot be silently mixed with 2026 Twelve Data or HistData: official source quotes are known to diverge between vendors. 2026 same-vendor M15 plus verified 09:00/17:00 exact anchors, 15m bar end, source freshness, Friday/holiday expiry and optional publication lag must pass first. Any incomplete 2026 label is excluded. 2026 futures/macro releases also restricted to PIT readiness. Only then score frozen 2024/2025 origin-safe fits and report months, N, UP/DOWN, BA and calibration; do not switch to ungoverned 2026 daily-close labels.

## Economic notes
The scientific win condition is stable incremental paired BA and DOWN recall plus probabilistic calibration and eventual bid/ask bank trading feasibility, **not** finding a high single-year percentage via retrospective search.
