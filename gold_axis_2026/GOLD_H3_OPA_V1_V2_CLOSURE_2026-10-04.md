# OPA-H3 V1/V2 — OPTIONS POSITIONING ASYMMETRY CLOSURE

**Date:** 2026-10-04  
**Branch:** `gold-h3-option-positioning-v1-20261004`  
**Binding champion:** `SAGE_H3_V2_EXCEPTION_ONLY`  
**Decision:** **CLOSE OPA AGGREGATE CALL/PUT POSITIONING FAMILY — NOT PROMOTED**

## 1. Independent channel tested

Official CME anonymous FTP daily-volume workbooks were used.

Product rows:
- `OG / GOLD CALL / O`
- `OG / GOLD PUT / O`

Fields:
- Total Volume
- preliminary Open Interest

Same-trade-date source values were forbidden. Only the latest valid trade date strictly before the H3 feature cutoff was permitted.

This is aggregate options positioning asymmetry. It is **not** signed order flow and **not** CME CVOL implied-variance skew.

## 2. Source coverage

- 2022: 251 / 251 = 100%
- 2023: 250 / 251 = 99.60%
- 2024: 252 / 252 = 100%
- 2025: 251 / 251 = 100%
- 2026: 53 / 188 = 28.19%, valid only through 2026-03-19 in this historical file family

The 2026 schema limitation is a source-coverage fact and was not used for model selection.

## 3. OPA V1 — generic low-capacity asymmetry model

DEV:
- 2023-2024 only
- eligible V5 momentum-continuation origins: 332
- true rescue targets: 93

Best observed precision in the frozen threshold grid:
- 33.77% at threshold 0.50

At the lower-action-rate 0.60 threshold:
- 83 candidates
- 27 rescue
- 56 broken
- precision 32.53%
- net -29

No threshold passed the preregistered DEV gate.

Status:
`OPA_DEV_FAIL`.

Therefore 2025 confirmation and 2026 holdout were not opened.

## 4. OPA V2 — momentum-opposed transition

V2 was designed only after the V1 DEV failure and used only the same 2023-2024 DEV universe.

Mechanism:
- OI call/put ratio transition against current momentum
- optional volume confirmation
- optional positioning-level confirmation

Across all frozen quantiles and four rule geometries, every rule had negative net rescue.

Best precision:
- 37.50%
- 16 actions
- 6 rescue / 10 broken
- net -4

Examples:
- OI extreme q=0.95: 5 / 15, net -10
- OI + volume confirmation q=0.95: 0 / 11, net -11
- dual confirmation q=0.85: 2 / 6, net -4

Status:
`OPA_V2_DEV_FAIL`.

Again:
- 2025 untouched confirmation not opened
- 2026 not opened

## 5. Scientific conclusion

Aggregate daily CALL/PUT volume and preliminary OI do **not** supply a sufficiently selective H3 reversal-rescue channel in this project.

The failure is stronger than a single-model failure because both were tested:

1. generic regularized multivariate asymmetry representation;
2. a mechanistic momentum-opposed transition representation.

Both failed on 2023-2024 DEV before later outcomes were used.

The result is consistent with an identification limitation:
aggregate call/put OI does not reveal whether positions are opening/closing long or short, and aggregate volume is not signed buyer/seller order flow.

## 6. What remains scientifically distinct

Do not keep retuning this same aggregate OI family.

A genuinely new directional options channel would require at least one of:

- CME Gold CVOL directional surface: UpVar / DownVar / Skew, if entitled historical access becomes available;
- signed options order flow / buyer-seller initiated imbalance;
- strike-level option chain with price, IV, delta/gamma and OI, allowing dealer-exposure / directional-demand reconstruction;
- higher-frequency contract-level futures/order-flow state rather than aggregate daily OI.

These are distinct information sets; they should not be approximated by re-labelling aggregate OG call/put OI.

## 7. Champion implication

No change to the direction champion.

Binding:
`SAGE_H3_V2_EXCEPTION_ONLY`.

The previously established probability-coherent mapping remains a valid calibration improvement:
- OCS FLIP => `p_sage = 1 - p_v5`;
- direction rule unchanged.

## 8. Evidence

- `GOLD_H3_OPA_V1_PREREG_2026-10-04.md`
- `GOLD_H3_OPA_V1_RESULT_2026-10-04.md`
- `GOLD_H3_OPA_V1_SUMMARY_2026-10-04.json`
- `GOLD_H3_OPA_V2_PREREG_2026-10-04.md`
- `GOLD_H3_OPA_V2_RESULT_2026-10-04.md`
- `GOLD_H3_OPA_V2_SUMMARY_2026-10-04.json`

No 2025/2026 outcome was used to rescue, tune or promote OPA V1/V2.
