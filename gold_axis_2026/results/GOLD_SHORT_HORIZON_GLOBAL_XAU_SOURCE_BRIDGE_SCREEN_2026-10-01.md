# GOLD SHORT-HORIZON GLOBAL XAU — Source Bridge Screen Result

**Authority:** 2026-10-01 frozen pre-run specification

- Historical anchor: `XAU_STAKTRAKR_RESEARCH_DAILY_R1`
- Preferred existing candidate (frozen ranking rule): `XAU_EOD_TWELVE_NY17`
- Prospective live extension status: **UNRESOLVED_NO_CANDIDATE_PASSES_REFERENCE_GATE**
- Target authority freeze allowed: **False**

| Candidate | N return | Pearson | Spearman | Sign % | Mean abs diff % | Diff SD % | Median ratio | Ratio CV % | Gate |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| XAU_EOD_TWELVE_NY17 | 441 | 0.937478 | 0.544281 | 65.08 | 0.829 | 1.049 | 0.999909 | 0.760 | FAIL |
| XAU_DAILY_XAUS | 98 | 0.710705 | 0.624301 | 70.41 | 0.949 | 1.251 | 0.999519 | 0.889 | FAIL |

## Reference gate

- Common return pairs >= 60
- Pearson >= 0.9
- Sign agreement >= 80.0%
- Return-difference SD <= 0.75%

No lag search was performed. 2025 remained closed for model/horizon/threshold selection.
