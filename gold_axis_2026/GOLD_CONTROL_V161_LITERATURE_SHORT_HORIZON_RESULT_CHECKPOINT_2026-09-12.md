# Gold Control V1.61 — Literature Short-Horizon Result Checkpoint

**Status:** `RETROSPECTIVE_SHORT_HORIZON_LITERATURE_DIAGNOSTIC_COMPLETE`  
**Support gate:** `FAIL`  
**Evidence class:** `RETROSPECTIVE_SHORT_HORIZON_LITERATURE_DIAGNOSTIC`  
**Production authority:** `FALSE`  
**Production writes:** `NONE`

## Trial tested

The frozen V1.61 experiment adapted gold-specific quantile-boosting literature to the existing XAU/USD 13:29 research panel. `QB_REALIZED` was the primary candidate. It used q25/q50/q75 gradient boosting with technical, session, cross-market, broad-USD, real-yield and realized-moment inputs. H5 was primary and H3 secondary. A signal was emitted only when q25>0 (`UP`) or q75<0 (`DOWN`); otherwise `NO_SIGNAL`.

This was an inspired XAU spot adaptation, not an exact replication of the published algorithms and not a COMEX futures experiment. Official GC futures history was not present in the governed research store for this freeze.

## Primary H5 result — QB_REALIZED

| Period | Coverage | Accuracy | Balanced accuracy | MCC | UP / DOWN |
|---|---:|---:|---:|---:|---:|
| Formation 2024 | 9.88% | 68.00% | 50.00% | 0.000 | 25 / 0 |
| Validation 2025 | 12.76% | 83.87% | 50.00% | 0.000 | 31 / 0 |
| Test 2026 available | 22.81% | 42.31% | 50.00% | 0.000 | 26 / 0 |

The apparently high 2025 raw accuracy is not directional skill: every H5 signal was `UP`. The model therefore failed the two-direction, balanced-accuracy, MCC and validation-coverage requirements. In 2026 the same all-UP behavior produced only 42.31% accuracy.

H5 mean pinball loss for `QB_REALIZED` was 0.006931 in formation 2024, 0.009259 in validation 2025, and 0.016945 in the available 2026 test. The realized-moment version was only marginally different from the `QB_BASE` ablation and did not create a stable direction edge.

## Secondary H3 result — QB_REALIZED

| Period | Coverage | Accuracy | Balanced accuracy | MCC | UP / DOWN |
|---|---:|---:|---:|---:|---:|
| Formation 2024 | 2.75% | 57.14% | 50.00% | 0.000 | 7 / 0 |
| Validation 2025 | 1.63% | 100.00% | 100.00% | 1.000 | 3 / 1 |
| Test 2026 available | 14.66% | 29.41% | 50.00% | 0.000 | 17 / 0 |

The four 2025 H3 signals are far too few to support a claim. The 2026 H3 result collapses back to one-class `UP` and performs poorly.

## Interpretation

1. V1.61 fails its pre-frozen support gate and is not promoted.
2. Gold-specific quantile boosting plus realized moments did not solve near-term H3/H5 direction on the current XAU spot/cross-market panel.
3. The failure pattern is again class/regime instability: 2025 upward dominance makes raw accuracy look strong, while 2026 exposes the lack of two-sided skill.
4. Realized moments can still carry distribution/quantile information, but they did not deliver robust direction in this implementation.
5. No post-score threshold, quantile, feature, horizon or hyperparameter repair is permitted inside V1.61.
6. The next scientifically justified near-term step requires genuinely new information rather than another classifier on the same panel. Highest-priority additions are properly licensed COMEX GC futures/settlement or intraday price-discovery data, option-implied gold volatility if available, and point-in-time gold-news text/sentiment. These must be introduced in a separately frozen research line.

## CI evidence

Workflow run: `34720626270`  
Artifact: `10305044437`  
Artifact digest: `sha256:f026927fd901b6e17b94b633e4a6535b65b5db3bc8f19b27d778584bf7561c68`

No canonical merge or production authority is authorized by this checkpoint.
