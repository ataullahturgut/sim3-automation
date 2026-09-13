# GOLD CONTROL — V1.70 Public Positioning Context Result Checkpoint

Date: 2026-09-13

## Status

**Frozen result:** `NO_PRE2025_INCREMENTAL_PUBLIC_SIGNAL__FREE_CONTEXT_HYPOTHESIS_FAIL`

This is a retrospective method-development diagnostic. It is **not** fresh blind OOS evidence and has **no production authority**.

## Frozen question

Does freely accessible, point-in-time public positioning / volatility context add incremental 1D or 3D directional skill beyond the existing Gold Control information set?

The experiment was frozen before scoring. The candidate sets were fixed as:

- `BASE_CORE`: existing SESSION/RM + MACRO/CROSS features.
- `PUBLIC_ONLY`: strictly lagged public GVZ dynamics + PIT-safe CFTC Gold COT positioning.
- `BASE_PLUS_PUBLIC`: `BASE_CORE + PUBLIC_ONLY`.

Model family was fixed to training-only median imputation -> StandardScaler -> L2 logistic regression (`C=1`). No model search, post-score feature additions, selector/CRASE, detector, residual correction, abstention tuning or paid data were allowed.

## Public source lineage and PIT handling

- CFTC Disaggregated Futures Only dataset `72hh-3qpy`, COMEX Gold contract market code `088691`.
- Cboe GVZ historical daily source.
- COT default conservative availability: `report_date + 7 calendar days`; known 2025-2026 federal-shutdown catch-up reports use CFTC-published actual catch-up dates.
- COT join requires `available_date < origin_date`.
- GVZ join requires `gvz_date < origin_date`; same-day GVZ is forbidden.
- Training labels require `target_date < origin_date`.

Final public fetch used:

- CFTC rows: 1,057; coverage 2006-06-13 through 2026-09-08.
- GVZ rows: 4,269; coverage 2009-09-18 through 2026-09-11.
- CFTC filtered SHA256: `5ca3988c2caa18253f566a640f4b1075eb4d1aec2d985ef865afa193b0841b4b`.
- GVZ raw SHA256: `5ba0197cd0d43ef0518deb61378dbf4f99465ace59ce9c3bf988062f681fe067`.
- GVZ normalized SHA256: `55caf02be1793d0e3183d9a127cc53ac931a9b2c95c36fdc782de34175664ea1`.

## Implementation audit trail

Two pre-result implementation/schema failures occurred and produced no scientific score:

1. Cboe source schema is `DATE,GVZ`, not `DATE,CLOSE`; the workflow was changed only to normalize the public source schema to `DATE,CLOSE`.
2. The six-character CFTC code `088691` lost its leading zero under numeric CSV inference; R1 reads the official code as text and zero-pads to six characters.

Neither fix changed the frozen feature set, target, temporal design, model, benchmark, gate or decision rule.

Final successful workflow run: `34758650519`.
Final artifact ID: `10318107081`.
Artifact digest: `sha256:909236e12a3009acda8f5ef77e53972067e9b21b5f7aa30f620cc0aa951734bd`.

## Frozen pre-2025 decision

### 1D

Formation Brier improvements of `BASE_PLUS_PUBLIC` relative to `BASE_CORE`:

- 2023H2: **+0.02643** (better)
- 2024H1: **-0.08397** (worse)
- 2024Q3: **-0.02638** (worse)

Formation gate: **FAIL**.

2024Q4 bridge:

- `BASE_CORE`: Brier **0.25417**, AUC **0.6311**.
- `BASE_PLUS_PUBLIC`: Brier **0.29019**, AUC **0.5244**.
- Incremental Brier improvement: **-0.03602** (public augmentation made the forecast materially worse).

Bridge gate: **FAIL**.

### 3D

Formation Brier improvements of `BASE_PLUS_PUBLIC` relative to `BASE_CORE`:

- 2023H2: **+0.01941** (better)
- 2024H1: **-0.01999** (worse)
- 2024Q3: **-0.05342** (worse)

Formation gate: **FAIL**.

2024Q4 bridge:

- `BASE_CORE`: Brier **0.37130**, AUC **0.4000**.
- `BASE_PLUS_PUBLIC`: Brier **0.43184**, AUC **0.4667**.
- Incremental Brier improvement: **-0.06053**.

Bridge gate: **FAIL**.

Therefore neither horizon passes the frozen pre-2025 incremental-information test. 2025/2026 cannot rescue this failure.

## Researcher-visible diagnostics only

These values are reported only for diagnosis after the pre-2025 decision was fixed.

### 1D

- `BASE_PLUS_PUBLIC` 2025: Brier **0.26637**, frequency Brier **0.24667**, Brier skill **-7.99%**, AUC **0.5337**.
- `BASE_PLUS_PUBLIC` available-2026: Brier **0.28093**, frequency Brier **0.25398**, Brier skill **-10.61%**, AUC **0.4811**.
- `PUBLIC_ONLY` available-2026 is approximately benchmark-level on Brier (**0.25456 vs 0.25398**) but has AUC only **0.4768**; this is not useful persistent directional skill.

### 3D

- `PUBLIC_ONLY` 2025 shows a retrospective pocket: Brier **0.23213** vs frequency **0.23783** (Brier skill **+2.40%**), AUC **0.6192**.
- That pocket reverses in available-2026: Brier **0.28378** vs frequency **0.25111** (Brier skill **-13.01%**), AUC **0.4356**.
- `BASE_PLUS_PUBLIC` 2025: AUC **0.6003** but Brier skill **-6.83%**; available-2026 AUC **0.4224**, Brier skill **-19.87%**.

The visible periods therefore reinforce, rather than overturn, the frozen conclusion: public positioning/volatility context produces intermittent pockets but not transportable short-horizon skill.

## Interpretation

1. **Free public context is not enough under this hypothesis.** Weekly COT positioning plus strictly lagged GVZ dynamics do not supply stable incremental 1D/3D predictive content.
2. **The 3D 2025 PUBLIC_ONLY pocket is not a promotion signal.** It was unavailable for pre-2025 selection, fails the bridge, and reverses in 2026.
3. **GVZ is not fully novel information for Gold Control.** The source reconstruction is stricter and adds dynamics, but the parent information universe already contained GVZ context. The genuinely new public information in V1.70 is mainly weekly COT positioning, which is structurally slow for a 1D/3D target.
4. **This failure does not test full option-implied distribution or order-flow information.** A strike/maturity option surface or intraday futures microstructure is qualitatively richer and faster than weekly COT + one volatility index.

## Locked decision

Do **not**:

- tune COT lags or publication assumptions after seeing the scores;
- add more COT transformations to V1.70;
- tune GVZ transformations;
- combine the visible 2025 pocket ad hoc;
- restart CRASE, detector or residual-adaptation work on this result;
- treat 2025/2026 as model-selection periods.

Next justified research action:

- Do **not** purchase a large paid dataset solely because V1.70 failed.
- First seek a low-cost/sample/trial slice of genuinely forward-looking data: GC option surface / Greeks-IV and/or GC futures microstructure/order-flow.
- Freeze a small incremental-information experiment before examining outcomes.
- If no trial/sample is obtainable, the alternative is a separately justified target/horizon redesign rather than adding algorithms to the same public information set.
