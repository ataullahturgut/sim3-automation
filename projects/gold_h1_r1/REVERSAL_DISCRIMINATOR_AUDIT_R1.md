# GOLD H1 R1 — Pre-2023 Reversal Discriminator Audit R1

Date: 2026-08-29

## Question
Can an origin-safe signal learned before 2023 distinguish a **true reversal conflict** from a **temporary counter-trend Tactical CONFLICT**, so that 2023 turning-point errors can be corrected without damaging correct 3M calls?

## Non-negotiable contract
- No 2023–2026 outcome may select or tune a discriminator.
- Candidate evidence must exist before 2023 or be frozen independently of 2023 outcomes.
- Target-month information is prohibited.
- Tactical R1 definition remains frozen: completed weekly close vs SMA4, same state for 2 completed weeks.
- Old Tactical V2 remains BLOCKED_MISSING_EXACT_RULE.

## Candidate 1 — Flip every Tactical CONFLICT
Pre-2023 rationale was real:
- DEV 2010–2020 CONFIRM N=53, 3M hit=83.02%.
- DEV CONFLICT N=36, 3M hit=25.00%.
- DEV NEUTRAL N=40, 3M hit=37.50%.
- Flip-on-CONFLICT challenger improved DEV accuracy 52.70% -> 66.67% and balanced accuracy 52.40% -> 66.41%.

One-shot 2023 result:
- Base 3M = 7/12 (58.33%; flat Oct scored as miss).
- Frozen flip = 7/12 (58.33%).
- Corrected May, Jun, Nov.
- Damaged Mar, Jul, Aug.
- Net gain = 0.

Decision: **REJECT as automatic reversal discriminator.**

## Candidate 2 — Tactical CONFLICT + BOCPD alarm
This candidate is independently meaningful because BOCPD supplies structural-break context and was frozen separately.

However the archived incremental audit already tested whether BOCPD improves Tactical directional-confidence calibration:
- DEV probabilities: 2010–2020 only.
- Validation: 2021–2023.
- Tactical-only validation Brier = 0.2104886.
- Tactical+BOCPD validation Brier = 0.2187891 (worse).
- Tactical-only validation log loss = 0.6139698.
- Tactical+BOCPD validation log loss = 0.6322436 (worse).
- Locked diagnostic also worsened: Brier 0.1961 -> 0.2096; log loss 0.5709 -> 0.5983.

Conflict event evidence also fails to separate reliably:
- 2020-09 BOCPD + CONFLICT: Tactical reversal was correct next month.
- 2022-05 BOCPD + CONFLICT: 3M remained correct; flip would be wrong.
- 2022-07 BOCPD + CONFLICT: Tactical reversal was correct.
Thus even this stronger joint state has mixed outcomes and small N.

Decision: **REJECT as 1M automatic reversal discriminator; KEEP BOCPD as risk/severity context only.**

## Candidate 3 — Continuous weekly hard gate
Already rejected by the frozen Tactical audit because it sacrifices too much bull upside. Locked replay net return fell from 1.288 for the 3M baseline to 0.696 for weekly MOM1 hard gate (MDD improved but opportunity cost was excessive). A MOM1&MOM4 hard gate also remained inferior at 0.857.

Decision: **REJECT.**

## Candidate 4 — Monthly static trend alternatives / adaptive selector
The direction audit had already tested simple monthly alternatives. No additional monthly trend/MA rule was stable enough to replace or hard-gate the direction layer; the adaptive 1M/3M selector did not provide a robust reversal advantage. Logistic trend challenger degraded out of development and was rejected.

Decision: **NOT_PROVEN / REJECT as production reversal discriminator.**

## 2023 error interpretation after causal audit
The data support the following classification:
- Feb-2023: collective surprise; 3M, Tactical, VW, Patch and IDMA were broadly bullish before the month. Existing technical reversal layer could not know it ex ante.
- May-2023: weak downside reversal; Tactical/Patch warning existed but move was only about -0.4%.
- Jun-2023: clear trend-lag reversal; 1M/Tactical/VW had turned down while 3M remained up.
- Nov-2023: clear upside reversal; Tactical/VW/IDMA were up while 3M remained down.
- Oct-2023: exact-flat monthly-average target; mostly a direction scoring artifact.

## Final R1 decision
`PRE2023_REVERSAL_DISCRIMINATOR = NOT_PROVEN`

No currently archived pre-2023 signal can reliably distinguish true reversal conflicts from temporary counter-trend conflicts without unacceptable false flips. Therefore:

1. Do **not** introduce an automatic direction flip.
2. Keep Tactical R1 as `CONFIRM / CONFLICT / NEUTRAL` confidence information.
3. Keep BOCPD as risk/severity context, not a direction vote.
4. Treat 2023 Jun/Nov as identifiable high-risk conflicts, but not as proof of a production rule.
5. Feb-2023 remains `UNEXPLAINED_BY_EXISTING_ORIGIN_SIGNALS`.
6. Any future discriminator must be developed from a clean pre-2023 event-level dataset and frozen before testing 2023.

## Auto-control
- Target leakage: PASS.
- 2023 used for rule tuning: NO.
- 2024–2026 used for rule tuning: NO.
- Metric-role separation: PASS.
- Hindsight/oracle used as model input: NO.
- Exact old Tactical V2 invented: NO.
- Production claim beyond evidence: NO.
