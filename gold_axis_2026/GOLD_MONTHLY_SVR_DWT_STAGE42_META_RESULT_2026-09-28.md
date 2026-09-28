# GOLD MONTHLY FORECAST — SVR / DWT-SVR STAGE 4.2 METAHEURISTIC RESULT

Date: 2026-09-28  
Status: **COMPLETE / BATCH 4.2 SCIENTIFIC GATE PASS / FIVE-METHOD SUPERSEDING RUN**

Supersession:
- An earlier four-method Stage 4.2 run/report is historical only.
- The user subsequently froze five-method batching.
- This report is the authoritative Stage 4.2 result for **ABC, SSA, GWO, WOA, HHO**.

Frozen parent reference:
- **EPSILON_RBF_DAILY12**
- DEV SigmaAE **1449.187363**
- Direction **19/33**

## DEV ranking

| Rank | Method | SigmaAE | MAE | RMSE | MAPE | Rel.MAE/RW | Direction | Worst month | Worst AE |
|---:|---|---:|---:|---:|---:|---:|---:|---|---:|
| 1 | HHO | **1549.539823** | 46.955752 | 65.314101 | 2.3055% | 0.881422 | 18/33 | 2024-11 | 183.389768 |
| 2 | ABC | 1563.258913 | 47.371482 | **62.367316** | 2.3251% | 0.889226 | 16/33 | 2024-11 | 176.842819 |
| 3 | GWO | 1590.104631 | 48.184989 | 63.997706 | 2.3805% | 0.904496 | 18/33 | 2024-11 | 163.761706 |
| 4 | WOA | 1635.345256 | 49.555917 | 63.415749 | 2.4628% | 0.930231 | 17/33 | 2024-11 | **152.635717** |
| 5 | SSA | 1659.670617 | 50.293049 | 67.134298 | 2.5014% | 0.944067 | **19/33** | 2024-11 | 180.502630 |

## Comparison with frozen parent

| Candidate | SigmaAE | Direction |
|---|---:|---:|
| EPSILON_RBF_DAILY12 parent | **1449.187363** | **19/33** |
| Best Batch 4.2 — HHO | 1549.539823 | 18/33 |

HHO minus parent:
- SigmaAE: **+100.352460**
- direction: **-1**

No Batch-4.2 method beats the frozen parent on the primary DEV criterion.

## Decision
- Batch 4.2 recorded only.
- No Stage-4 parent selected yet.
- Mandatory broad-screen progress: **9/32**.
- Remaining methods: **23**.
- Next five-method batch:
  - ACO
  - BAT
  - FA
  - MFO
  - FPA

## Provenance
Authoritative five-method run:
- Workflow run: **36399323779**
- Job: **108853166239**
- Artifact: **10959784334**
- Artifact SHA256: `7c7297b7dcd39baca51d61073167b36c447c4a80b88c4455da1e8719e658f54f`
- Scientific gate: **SVR_DWT_STAGE42_GATE=PASS**
- Model execution: SUCCESS
- Aggregate: SUCCESS
- Scientific gate: SUCCESS
- Artifact upload: SUCCESS
- Workflow overall conclusion: FAILURE only because final report git push was rejected as non-fast-forward after branch advancement.

Historical four-method run:
- run 36398195330
- retained only as superseded evidence; not the authoritative Batch 4.2 result.

## Kontrol ve Uyum Özeti
- Five-method batch directive respected: PASS.
- Common bounds: PASS.
- Population=24: PASS.
- Generations=45: PASS.
- Repeats=3: PASS.
- Prior-only chronology: PASS.
- No outer-target tuning: PASS.
- Scientific gate: PASS.
- 2025 opened: NO.
- 2026 used: NO.
- Random split: NONE.
- DB mutation: NONE / READ_ONLY.
- Batch 4.2: **COMPLETE / 9 OF 32 TOTAL METHODS COMPLETE**.
