# GOLD H1 R1 — Reversal Evidence Diagnostic, 2026 Jan–Jul

Status: DIAGNOSTIC_ONLY / NOT_A_TUNED_PRODUCTION_MODEL

Method discipline:
- 2026 outcomes were not used to tune thresholds.
- Each row uses only information available by the preceding month-end origin.
- ETF flow was NOT included because a point-in-time real-time flow series was not yet source-locked; monthly post-hoc WGC commentary is prohibited as an origin feature.
- BOCPD alarm is usable only from the month after the alarm month closes.

Evidence hierarchy tested diagnostically:
1. Monthly prior: canonical 3M direction.
2. Reversal evidence: MOM1 disagreement, Tactical Slow disagreement, VW implied direction disagreement.
3. Structural confirmation: previously frozen BOCPD-return alarm known by origin.
4. No automatic flip from Tactical alone.

| Target | Actual | 3M | MOM1 | Tactical Slow | VW implied | BOCPD known at origin | Diagnostic action | Result |
|---|---|---|---|---|---|---|---|---|
| 2026-01 | UP | UP | UP | UP | DOWN | no | KEEP UP | correct |
| 2026-02 | UP | UP | UP | UP | UP | no | KEEP UP | correct |
| 2026-03 | DOWN | UP | UP | UP | UP | no | KEEP UP / no ex-ante reversal evidence | wrong |
| 2026-04 | DOWN | UP | DOWN | DOWN | DOWN | Mar-2026 alarm known | REVERSAL CONFIRMED -> DOWN | correct |
| 2026-05 | DOWN | DOWN | DOWN | NEUTRAL | DOWN | Mar+Apr alarms known | KEEP DOWN | correct |
| 2026-06 | DOWN | DOWN | DOWN | DOWN | UP | Apr alarm known | KEEP DOWN; VW dissent insufficient | correct |
| 2026-07 | DOWN | DOWN | DOWN | DOWN | UP | Jun alarm known | KEEP DOWN; VW dissent insufficient | correct |

Headline:
- Canonical 3M baseline: 5/7 = 71.43%.
- Evidence hierarchy diagnostic: 6/7 = 85.71%.
- It corrects the April lag/reversal failure without damaging Jan, Feb, May, Jun or Jul.
- March remains a collective-surprise reversal: at the Feb-28 origin 3M, MOM1, Tactical Slow and VW all remained UP, and no prior BOCPD-return alarm was available. A price-history-only reversal layer cannot honestly claim to have forecast this turn.

Decision:
- MULTI-SIGNAL REVERSAL EVIDENCE: PROMISING_DIAGNOSTIC.
- PRODUCTION APPROVAL: NOT_PROVEN.
- The main remaining target is collective-surprise months like March 2026. These require genuinely independent origin-safe information (macro surprise / real yields / USD / flow) rather than more momentum transformations.
