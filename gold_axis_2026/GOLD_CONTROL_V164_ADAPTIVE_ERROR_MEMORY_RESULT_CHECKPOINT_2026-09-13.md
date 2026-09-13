# Gold Control V1.64 — Adaptive Error-Memory Forecaster Result Checkpoint

Date: 2026-09-13  
Branch: `gold-v164-adaptive-error-memory-forecaster-research`  
Draft PR: #55  
Parent: V1.63 heterogeneous forecasters research  
Pre-score freeze commit: `c171a2a0c8809e8924df1c875a0df6db236e942b`  
Workflow run: `34752686111` — SUCCESS  
Artifact: `10316352769`  
Artifact digest: `sha256:23901808b5b8db4b2065797865f7ac4269bf544953fe1ce38b37964e19ab78da`

Evidence class: `RETROSPECTIVE_METHOD_DEVELOPMENT_DIAGNOSTIC_NOT_FRESH_OOS`.

## Frozen question

Can the short-horizon forecaster improve temporal robustness by causally learning from only matured prior errors, using exponential forgetting plus residual-error correction, with an additional state-local error-memory correction?

All constants, state variables, horizons, parent forecasters and success gates were frozen before scoring. Only `j+h<=t` outcomes can enter training or error memory. No selector, ensemble scoring, abstention tuning, random split, production write or trading action is allowed in V1.64.

## Mechanisms tested

For each V1.63 parent (`GOLD_RIDGE`, `SESSION_RM_RIDGE`, `PRICE_DISCOVERY_HGB`, `MACRO_CROSS_RIDGE`, `FULL_HGB`) and for 1D/3D targets:

- `STATIC`: V1.63-style rolling parent.
- `FORGET`: same parent with exponential sample forgetting (frozen half-life 60 origins).
- `ERRMEM`: `FORGET` plus shrunken causal correction from matured prior residuals `y-p`.
- `LOCAL_ERRMEM`: `FORGET` plus matured residual correction weighted by recency and similarity of the current state (`gold_mom5`, `gold_mom20`, `gold_rv20`, FAST/SLOW/monthly role context, broad-USD 5D change, real-10Y 5D change).

## Primary decision

`V1.64 = FAIL / NEGATIVE PRIMARY SUCCESS-GATE RESULT`.

No adaptive variant passes the frozen gate in both 2025 validation and available-2026 test for either 1D or 3D. In particular, no path simultaneously beats the expanding-frequency Brier anchor, improves its own static parent in both periods, retains acceptable two-direction BA/MCC, and delivers the required 2026 Brier improvement.

This does **not** mean error-based adaptation is useless. V1.64 reveals a narrower and more useful result: adaptation helps some parents specifically during the 2026 deterioration, but an always-on fixed forgetting/correction rule damages other periods or other parents.

## Most informative 2026 changes

### 3D Macro/Cross forecaster

Static parent in available 2026:

- Brier: `0.30349`
- BA: `0.46556`
- MCC: `-0.08224`

`ERRMEM`:

- Brier: `0.27530` (improvement of about `0.02819` versus static)
- BA: `0.49667`
- MCC: `-0.00788`

This is a large proper-score repair relative to the failed static parent, but it still does not beat the expanding-frequency Brier anchor (`0.25107`) and does not establish positive directional skill. In 2025 the same adaptation worsens the already-strong macro/cross path, so the effect is not temporally stable.

### 3D Gold-only forecaster

Available-2026 static Brier `0.30425`, BA `0.40556`, MCC `-0.22138`.

`LOCAL_ERRMEM` improves this to:

- Brier: `0.29430`
- BA: `0.46333`
- MCC: `-0.08257`

Again, error memory repairs part of the failure but not enough to create predictive skill.

### 3D Session / realized-moment forecaster

This is the strongest directional self-correction signal in V1.64.

Available 2026:

| Variant | Brier | BA | MCC | UP / DOWN |
|---|---:|---:|---:|---:|
| STATIC | 0.26130 | 0.49333 | -0.01679 | 133 / 32 |
| FORGET | 0.25989 | 0.52222 | 0.05164 | 125 / 40 |
| ERRMEM | 0.25971 | 0.56444 | 0.13965 | 115 / 50 |
| LOCAL_ERRMEM | 0.26000 | **0.57000** | **0.15256** | 116 / 49 |

Relative to the forgetting forecaster, `LOCAL_ERRMEM` changes 15 2026 classifications; 11 of those flips correct an error and 4 worsen a previously correct call. Relative to the static parent, it changes 29 classifications; 20 improve and 9 worsen.

However, 2025 for this same parent remains weak (LOCAL_ERRMEM BA about `0.48463`, MCC negative, Brier `0.25924` versus frequency `0.23795`). Therefore the 2026 directional recovery is a real retrospective signal but not a stable model success.

## Why the current self-correction still fails

The error-correction machinery is active too often rather than only when the parent is actually drifting:

- median matured error-memory history is about 202 origins at 1D and 198 at 3D;
- median local effective N is about 127 at 1D and 129 at 3D;
- local error correction is non-zero on roughly 92% of origins.

Therefore V1.64 behaves more like a permanently modified forecaster than a model that selectively notices deterioration and changes behavior only when needed. This explains the core pattern: it can repair a broken 2026 parent (especially 3D macro/cross and 3D session/RM) while simultaneously degrading a parent/regime that was already working better in 2025.

## Scientific interpretation

The main bottleneck has narrowed again:

1. V1.62 showed that a selector cannot rescue weak, near-duplicate forecasters.
2. V1.63 created genuinely heterogeneous experts, but their skill was temporally unstable.
3. V1.64 shows that **causal error memory can repair some regime-specific failures**, but a fixed always-on forgetting/correction rule is too blunt.

The next defensible hypothesis is therefore **error-triggered adaptation**, not stronger permanent forgetting and not another selector.

The forecaster should remain close to its stable parent while recent matured proper-score errors are normal; when its recent error process deteriorates materially relative to its own historical baseline, it should enter an adaptation state (shorter memory / stronger error correction / state-local update). After performance normalizes, the extra adaptation should decay back toward the parent. This is a drift-detection/control problem over the model's own forecast losses.

Any next version must freeze the drift trigger and adaptation response before scoring. V1.64 thresholds, half-lives, rho, state vector and horizons must not be retuned after this result.

No prospective or production claim is made.
