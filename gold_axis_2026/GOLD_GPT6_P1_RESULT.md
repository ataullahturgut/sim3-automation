# GPT-6 independent P1 result — US-DST feature added to fixed Türkiye session prior
**Decision: BASELINE_ONLY / NO PROMOTION.** Precommitted at `0e410cd1`. No original model or authority edited.

Data: actual archived EV-Dukascopy XAU spot BID/ASK M15 mid, **2740 strictly complete DAY/OVN windows** 2020–25. Real-time vendor first-receipt unproven. Issue 08:45 DAY09→16:45 / 16:30 OVN16:45→next09 Mon–Thu TRT; entry price is strictly future-open (outcome only), exit is last bar close. 1366 scored windows in 2023/24 sequential development + 2025 already-open transport. Winter/summer NY DST known on issue date.

Primary Brier (smaller better):
| Window | Year (N) | expanding/frozen same-session prior | conditional DST prior | Delta (Base−DST) |
|---|---|---:|---:|---:|
| DAY | 2023 (256) | .251660 | .251827 | −.000166 |
| DAY | 2024 (259) | .246809 | .245957 | +.000852 |
| DAY | 2025 (258) | .245396 | .246344 | −.000948 |
| OVN | 2023 (198) | .249198 | .249981 | −.000784 |
| OVN | 2024 (197) | .247948 | .248953 | −.001004 |
| OVN | 2025 (198) | .248828 | .248782 | +.000046 |

DAY DEV 2023–24 Brier improvement +.000346, three-month moving bootstrap 95% CI [−.000190,+.000932]; OVN - .000894 CI [−.001897,−.000126]. Both fail required robust cross-year gain; OVN worse. Most candidate predictions degenerate to majority UP; DEV DAY/OVN candidate BA approximately .4994/.4834. Signed log-return and reconstructed XAU price errors also saved in result JSON; never relabel class-prior accuracy as causal price discovery. **No new signed return forecast value established.**

Reproducibility: source `sql/gold_gpt6_p1_m15_session_forward_price.sql`, archived six annual source CSVs, every outcome/prediction in `GOLD_GPT6_P1_SCORE_ROWS.csv`, summary `GOLD_GPT6_P1_RESULT.json`, Python strict replay in `tools/gold_gpt6_p1_replay.py`; CI verifies original rates/outputs. All on separate PR.
