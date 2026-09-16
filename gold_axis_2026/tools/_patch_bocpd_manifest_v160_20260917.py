from pathlib import Path

p = Path('gold_axis_2026/GOLD_CONTROL_PROJECT_MANIFEST.md')
s = p.read_text(encoding='utf-8')

s = s.replace('**Manifest version:** 1.59  ', '**Manifest version:** 1.60  ', 1)

old_31 = '''### 3.1 BOCPD research authority — exactly two retained identities

The active BOCPD research authority contains exactly **two** identities:

1. `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH` — **primary BOCPD research model**.
2. `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` — **frozen comparison baseline only**.

No other BOCPD identity is active authority. Raw hourly Candidate B, earlier optimized B2 identities, daily Candidate A, monthly `BOCPD_RETURN_SUCCESSOR_V1`, duration/residual V2, robust-clipped V3, duration+robust V4 and other superseded BOCPD experiments are historical only. Their active code/result surfaces are removed from the current research branch; Git history may retain them solely for audit traceability.

Neither retained BOCPD identity is a governed runtime or production engine at this stage. V5 is the active research reference; R2 is a benchmark. Neither emits an equal-weight direction vote.
'''
new_31 = '''### 3.1 BOCPD research authority — exactly two retained identities

The active BOCPD research authority contains exactly **two** identities:

1. `BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH` — **primary BOCPD research model**.
2. `BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` — **frozen comparison baseline only**.

No other BOCPD identity is active authority. Raw hourly Candidate B, earlier optimized B2 identities, daily Candidate A, monthly `BOCPD_RETURN_SUCCESSOR_V1`, duration/residual V2, robust-clipped V3, duration+robust V4 and other superseded BOCPD experiments are historical only. Their active model-code/result/workflow surfaces are removed from the current research branch; Git history may retain them solely for audit traceability.

The **only authoritative BOCPD model surfaces** on the active research branch are:

- code: `gold_axis_2026/tools/bocpd_hourly_b2_adaptive_hazard_pre2025.py`;
- code: `gold_axis_2026/tools/bocpd_hourly_b2_baseline_r2_pre2025.py`;
- result: `gold_axis_2026/GOLD_CONTROL_BOCPD_B2_ADAPTIVE_HAZARD_V5_PRE2025_RESULT_2026-09-16.md`;
- result: `gold_axis_2026/GOLD_CONTROL_BOCPD_B2_BASELINE_R2_PRE2025_RESULT_2026-09-17.md`;
- reproducibility workflow: `.github/workflows/gold-bocpd-b2-adaptive-hazard-pre2025-20260916.yml`;
- reproducibility workflow: `.github/workflows/gold-bocpd-b2-baseline-r2-pre2025.yml`.

Any other BOCPD-named model code, model result or model workflow present on the active research branch is non-authoritative and must be removed or separately re-authorized by manifest change control. Historical lineage belongs in Git history, not in a competing active surface.

The retained hourly input series is `XAU_USD_TWELVE_1H_RESEARCH_V1`. It is a **research-only** historical series and does not replace canonical `XAU_EOD_TWELVE_NY17` runtime semantics.

Neither retained BOCPD identity is a governed runtime or production engine at this stage. V5 is the active research reference; R2 is a benchmark. Neither emits an equal-weight direction vote.
'''
assert old_31 in s, 'section 3.1 anchor not found'
s = s.replace(old_31, new_31, 1)

old_108 = '''### 10.8 BOCPD — retained research authority and pre-2025 evidence

Evidence class: `PRE2025_RETROSPECTIVE_TIME_ORDERED_COMPARISON_NOT_PRISTINE`.

Binding chronology for both retained BOCPD identities:

- 2022: research formation / hour-of-day normalization / prior formation;
- 2023: development and parameter selection;
- 2024: pre-2025 chronological retrospective comparison; not described as a pristine untouched holdout;
- 2025: prohibited for BOCPD tuning/model selection in this retained line and not accessed by the V5/R2 pre-2025 evaluation scripts.

`BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` — frozen benchmark, 2024 comparison:

- 57 episodes;
- 12 matched episodes;
- 45 unmatched episodes;
- 11 / 17 abnormal-volatility events captured;
- precision `0.210526`;
- recall `0.647059`;
- F0.5 `0.243363`.

`BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH` — primary BOCPD research model, same 2024 comparison:

- 65 episodes;
- 15 matched episodes;
- 50 unmatched episodes;
- 14 / 17 abnormal-volatility events captured;
- precision `0.230769`;
- recall `0.823529`;
- F0.5 `0.269576`.

V5 improves event coverage, precision, recall and F0.5 relative to R2 under the same pre-2025 comparison. False-warning burden remains material, therefore the result does **not** authorize runtime or production promotion.

No BOCPD identity other than V5 and R2 may be used as current research authority.
'''
new_108 = '''### 10.8 BOCPD — retained research authority and pre-2025 evidence

Evidence class: `PRE2025_RETROSPECTIVE_TIME_ORDERED_COMPARISON_NOT_PRISTINE`.

Hourly model input: `XAU_USD_TWELVE_1H_RESEARCH_V1` (research-only; not canonical NY17 runtime authority).

Binding chronology for both retained BOCPD identities:

- 2022: research formation / hour-of-day normalization / prior formation;
- 2023: development and parameter selection;
- 2024: pre-2025 chronological retrospective comparison; not described as a pristine untouched holdout because BOCPD programme-level 2024 evidence had already been seen;
- 2025: prohibited for BOCPD tuning/model selection in this retained line and **not queried or accessed** by the V5/R2 pre-2025 model scripts.

The 2022 hourly history is accepted as **sufficient high-coverage research formation data for this phase**. This manifest does not claim that every theoretically expected 2022 market-hour slot has been independently completeness-certified.

`BOCPD_HOURLY_B2_PRE2025_BASELINE_R2_RESEARCH` — frozen benchmark, 2024 auxiliary abnormal-volatility comparison:

- 57 episodes;
- 12 matched episodes;
- 45 unmatched episodes;
- 11 / 17 abnormal-volatility events captured;
- precision `0.210526`;
- recall `0.647059`;
- F0.5 `0.243363`.

`BOCPD_HOURLY_B2_ADAPTIVE_HAZARD_V5_RESEARCH` — primary BOCPD research model, same 2024 auxiliary abnormal-volatility comparison:

- 65 episodes;
- 15 matched episodes;
- 50 unmatched episodes;
- 14 / 17 abnormal-volatility events captured;
- precision `0.230769`;
- recall `0.823529`;
- F0.5 `0.269576`.

These BOCPD metrics are **auxiliary abnormal-daily-volatility comparison metrics**. They do **not** establish performance against the primary engine-independent structural GC-BREAK label universe in Section 9 and must not be reported as structural-break recall/precision.

V5 improves event coverage, precision, recall and F0.5 relative to R2 under the same pre-2025 auxiliary comparison. False-warning burden remains material, therefore the result does **not** authorize runtime or production promotion.

No BOCPD identity other than V5 and R2 may be used as current research authority. Any future BOCPD successor requires a separately named preregistration/change-control step; this manifest does not pre-authorize one.
'''
assert old_108 in s, 'section 10.8 anchor not found'
s = s.replace(old_108, new_108, 1)

old_final = 'Current BOCPD research authority is restricted to Adaptive Hazard V5 plus the frozen R2 benchmark; all other BOCPD models are superseded and removed from the active research surface.'
new_final = 'Current BOCPD research authority is restricted to Adaptive Hazard V5 plus the frozen R2 benchmark and the explicit code/result/workflow allowlist in Section 3.1; all other BOCPD model surfaces are superseded and removed from the active research surface.'
assert old_final in s, 'final BOCPD summary anchor not found'
s = s.replace(old_final, new_final, 1)

p.write_text(s, encoding='utf-8')
print('BOCPD_MANIFEST_V160_PATCHED=TRUE')
