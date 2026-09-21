# GOLD CONTROL — ALTUNTAŞ ALEXNET CANDLE V1 PREREGISTRATION

**Date:** 2026-09-21  
**Identity:** `DIRECTION_ALTUNTAS_ALEXNET_CANDLE_V1_RESEARCH`  
**Primary authority:** Altuntaş, Okumuş & Kocamaz (2022), *Prediction of Gold Price Direction using Convolutional Neural Networks and a Transfer Learning Approach*, DOI 10.53070/bbd.1205299  
**Evidence class:** `SOURCE_CONSTRAINED_TRANSFER_LEARNING_RECONSTRUCTION / LOCKED_RETROSPECTIVE_RESEARCH`  
**Runtime authority:** NONE  
**Production writes:** NONE

## 1. Why the original 15-year span is not copied mechanically

The source study used 2007-2021 daily gold OHLC and split it 3:1:1 as 9 years training, 3 years validation and 3 years test. The paper does not establish 15 years as a required model parameter or as an optimized history length. Its AlexNet setup is transfer learning / fine-tuning, which the paper itself motivates as enabling training with less task-specific data.

Gold Control therefore freezes a shorter recent-history adaptation before scoring:

- training targets: 2018-01-01 through 2022-12-31;
- development / early-stopping validation targets: 2023-01-01 through 2023-12-31;
- fixed pre-2025 validation targets: 2024-01-01 through 2024-12-31;
- locked retrospective challenge targets: 2025-01-01 through 2025-12-31.

Warm-up OHLC may begin before 2018 only to compute the 50-day moving average and image history. No pre-2018 target enters training.

This is not claimed as an exact reproduction of the source split.

## 2. Data source and authority boundary

Provider: Twelve Data.  
Instrument: `XAU/USD`.  
Endpoint: `/time_series`.  
Interval: `1day`.

Only true provider daily OHLC fields are eligible:
- open;
- high;
- low;
- close.

No OHLC may be synthesized from close-only data.

Daily-provider semantics are retained as returned by the provider. The source paper used Investing.com daily OHLC and did not expose enough daily-boundary metadata to prove exact clock equivalence; therefore this is a source-constrained method reconstruction, not an exact data replication.

Validation rules:
- finite positive O/H/L/C;
- low <= open <= high;
- low <= close <= high;
- Monday-Friday only for the governed research panel;
- duplicate dates with conflicting values are fatal;
- equal-close next-day labels are omitted exactly as an unlabelled direction case;
- no forward fill or interpolation.

Raw vendor market values are not written to production databases and are not committed as a public project data table by this audit workflow. Reproducibility retains row counts, period coverage and a normalized-data SHA-256 digest.

## 3. Source method elements retained

The source establishes:
- next-trading-day UP/DOWN label from close(t+1) versus close(t);
- 11-day candlestick chart image ending at the forecast origin;
- SMA(7);
- SMA(50);
- Bollinger Bands based on SMA(20) plus/minus 2 standard deviations;
- RGB input resized to 227x227;
- pretrained AlexNet fine-tuning;
- replacement of the final fully connected classifier by a two-output classifier;
- maximum 100 epochs;
- mini-batch size 32;
- learning rate 1e-4;
- validation once per epoch;
- early stopping after 10 validations without improvement.

These are frozen before 2024/2025 scoring.

## 4. Image reconstruction boundary

The source paper does not fully specify every plotting primitive, pixel colour, line width, axis setting or MATLAB renderer default. Gold Control therefore freezes one deterministic reconstruction before scoring:

- 11 retained trading-day candles ending at t;
- overlays: SMA7, SMA50, Bollinger upper/middle/lower;
- no future value appears in the image;
- axes, tick labels and text removed;
- fixed canvas and deterministic rendering;
- per-image plot limits may depend only on values available through t;
- resize to 227x227 RGB after deterministic rendering.

The exact plotting implementation must be committed before any 2024 or 2025 score is read.

## 5. Chronology and target maturity

At image origin t:
- every plotted candle and indicator uses data completed no later than t;
- label uses the next retained trading-day close solely as the supervised target;
- the 2023 development set may control early stopping only;
- 2024 is a fixed pre-2025 validation period and may not alter rendering, history span, learning rate, batch size, model family, class mapping or threshold;
- 2025 is locked retrospective challenge evidence only and cannot rescue a failed 2024 decision.

No random split is permitted.

## 6. Minimum sample-support gate

Before model implementation proceeds, the daily OHLC source audit must establish at least:
- 1000 eligible labelled training images in 2018-2022 after warm-up;
- 200 eligible labelled 2023 development images;
- 200 eligible labelled 2024 fixed-validation images;
- 200 eligible labelled 2025 challenge images.

If any floor fails, status is `BLOCKED_INSUFFICIENT_IMAGE_SUPPORT` and no CNN score is produced under this identity.

## 7. Frozen evaluation metrics

Mandatory for 2024 and 2025:
- n;
- accuracy;
- balanced accuracy;
- UP sensitivity;
- DOWN sensitivity / specificity;
- precision and F1 by class;
- TP/TN/FP/FN;
- forecast UP/DOWN counts;
- Brier score from the UP softmax probability;
- log loss;
- always-UP and always-DOWN raw-accuracy baselines.

The source paper's reported 53.8% accuracy and 37.54% DOWN specificity are literature-reference values only; they are not a project promotion threshold.

## 8. Pre-2025 research-interest gate

A 2024 result is considered worth retaining for further scientific analysis only if:
- balanced accuracy >= 0.55;
- UP sensitivity >= 0.40;
- DOWN sensitivity >= 0.40;
- raw accuracy strictly exceeds both always-UP and always-DOWN baselines.

A failed 2024 gate may still be replayed unchanged on 2025 for audit completeness, but 2025 cannot reverse the failed pre-2025 decision.

## 9. Interpretation lock

Possible statuses:
- `SOURCE_AUDIT_READY`;
- `BLOCKED_INSUFFICIENT_IMAGE_SUPPORT`;
- `EVALUATED / PRE2025_GATE_PASSED`;
- `EVALUATED / NO_PROMOTION / PRE2025_GATE_FAILED`.

No runtime, trading or production authority is created by this experiment.

## 10. Executable reconstruction choices frozen before scoring

The primary paper does not state the optimizer name or every plotting/rendering primitive. The executable V1 therefore freezes the following as **Gold Control reconstruction choices**, not source-paper claims:

- framework: PyTorch / torchvision pretrained `alexnet`, `AlexNet_Weights.IMAGENET1K_V1`;
- all AlexNet layers remain trainable (full fine-tuning);
- optimizer: SGD, learning rate `1e-4`, momentum `0.9`, weight decay `0`;
- loss: ordinary unweighted cross entropy;
- seed: `20260921`;
- no data augmentation;
- ImageNet RGB normalization after deterministic resize to 227x227;
- early stopping monitor: 2023 development-set accuracy; checkpoint only on strict accuracy improvement; ties retain the earlier epoch;
- patience: 10 completed development evaluations without strict accuracy improvement;
- maximum epochs: 100; batch size: 32;
- class threshold: UP iff softmax P(UP)>=0.5.

Deterministic chart reconstruction:
- white background, no axes/ticks/text;
- 11 candles ending at the origin;
- UP candle: white body with black outline; DOWN candle: black body; grey wick;
- SMA7: cyan; SMA50: red;
- Bollinger upper: green; middle SMA20: yellow; lower: magenta;
- price limits are computed only from the plotted origin-safe candle/indicator values with fixed 5% vertical padding;
- fixed raster geometry followed by deterministic resize to 227x227 RGB.

These choices are frozen before any 2024 fixed-validation or 2025 challenge score is produced. A negative result may not be rescued by changing optimizer, momentum, renderer, colours, checkpoint rule, augmentation, threshold or history span under this identity.
