# GOLD D1 — CIG-D1 V1 EXTENDED THROUGH 2026-10-02

**Date:** 2026-10-05  
**Identity:** `CIG_D1_V1_EXTENDED_THROUGH_2026_10_02`  
**Status:** RETROSPECTIVE DIAGNOSTIC / MIXED-SOURCE EXTENSION — NOT PROSPECTIVE OOS

## Scope

This file combines:
1. the internally consistent refreshed Jan–Sep replay through issue date 2026-09-25; and
2. a five-day post-snapshot extension for issue dates 2026-09-28 through 2026-10-02.

The binding CIG decision remains unchanged:
- SAGE V2 + RuleFlow V3-TG
- HELIOS V5-DCE
- RIFT
- VEGA
- 4/4 agreement => directional action
- any disagreement => UNCERTAIN

## Added 28 Sep–2 Oct block

| Issue | Actual | SAGE+RF | V5 | RIFT | VEGA | CIG | Correct |
|---|---|---|---|---|---|---|---:|
| 2026-09-28 | DOWN | UP | UP | UP | UP | UP | 0 |
| 2026-09-29 | DOWN | UP | UP | DOWN | DOWN | UNCERTAIN | — |
| 2026-09-30 | UP | UP | UP | UP | UP | UP | 1 |
| 2026-10-01 | UP | DOWN | DOWN | DOWN | DOWN | DOWN | 0 |
| 2026-10-02 | DOWN | UP | UP | UP | UP | UP | 0 |

Added block:
- D1 days: **5**
- 4/4 consensus: **4**
- correct: **1**
- consensus accuracy: **25.00%**
- coverage: **80.00%**
- V5 full-chain historical reproduction max abs diff: **5.551e-17**

## Combined 2026 result through 2 October

| Metric | Result |
|---|---:|
| D1 days | **196** |
| 4/4 consensus actions | **161** |
| Correct consensus actions | **113** |
| Consensus accuracy | **70.19%** |
| Selective coverage | **82.14%** |
| UNCERTAIN days | **35** |
| SAGE+RuleFlow forced accuracy | **131/196 = 66.84%** |
| V5 forced accuracy | **130/196 = 66.33%** |
| RIFT forced accuracy | **129/196 = 65.82%** |
| VEGA forced accuracy | **129/196 = 65.82%** |

September after adding Sep 28–30:
- **18/22** consensus, **11** correct
- accuracy **61.11%**
- coverage **81.82%**

October 1–2 diagnostic bridge:
- **2/2** consensus
- **0/2 correct**
- accuracy **0.00%**

## Important interpretation

The late-September / early-October block is a sharp failure cluster for the continuation-heavy consensus: three of four high-confidence calls are wrong. The extension lowers the refreshed combined consensus result from **112/157 = 71.34%** through Sep 25 to **113/161 = 70.19%** through Oct 2.

This is not evidence that the consensus should be retuned on these five outcomes. It is evidence that the model stack can become coherently wrong: agreement alone does not guarantee regime validity. The 2026-09-29 issue is especially informative because V5 flips UP through DCE/OPAL while RIFT and VEGA remain DOWN, causing CIG to abstain; that abstention is correct operationally because the realized day is DOWN.

## Source and governance caveat

For issue dates Sep 28–29, prices remain inside the clean frozen price snapshot. For issue dates Sep 30, Oct 1 and Oct 2, the daily price extension is the previously approved **futures-return-spliced diagnostic bridge**, not the official prospective StakTrakr stream.

The frozen SAGE V2 IFBC/LLRS snapshots end on 2026-09-24. Under SAGE V2's frozen missing-source rule, missing source state means **no exception / KEEP V5**. RuleFlow V3-TG likewise has no same-origin archived frozen source state for these added origins, so no retrospective RuleFlow FLIP is invented.

Therefore:
- the five-day extension is **diagnostic**, not prospective OOS;
- the 196-day result is useful for stress analysis and model design;
- it must not be presented as 196 days of homogeneous prospective evidence;
- no threshold should be changed on the basis of these five outcomes without opening a new challenger identity.

Authority inputs:
- `GOLD_D1_CIG_V1_EXTENDED_JAN_SEP_REPLAY_2026-10-05.csv`
- `GOLD_D1_CIG_V1_SEP28_OCT2_EXTENSION_2026-10-05.csv`
