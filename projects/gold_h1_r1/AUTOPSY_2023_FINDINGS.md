# 2023 Direction Error Autopsy — Findings

## Evidence used
- Exact audited monthly 3M Momentum replay.
- Archived 2023 VW/Patch forecast outputs (`results_2023.csv`).
- IDMA/TVP/DMA rolling-origin H=1 outputs.
- Tactical Slow state rebuilt from pinned `simom1/XAUUSD-history` commit `f09a4dea9de06fc1b9f58ff95f7cffaa193b70c0`, using only completed weekly bars available by each month-end origin.
- Tactical rule frozen before this autopsy: sign(last completed weekly close - SMA4) with two consecutive completed-week persistence; otherwise NEUTRAL.
- Macro/autopsy features are origin-lagged diagnostics only.

## Auto-control result
PASS for the autopsy construction: no target-month observation was used to construct the origin Tactical state or model directions. Realized target values are used only to label post-hoc correctness/error type.

## 2023 headline
The reported 3M direction accuracy was 7/12 = 58.33%, but one of the five misses is October where the monthly average was exactly unchanged (1916 -> 1916). Economically meaningful wrong-direction months are therefore February, May, June and November.

## Error decomposition
### February 2023 — collective surprise reversal
Actual monthly average: 1898 -> 1855 (-2.27%).
At the Jan-31 origin: 3M UP, 1M UP, Tactical Slow persistent UP, VW UP, Patch UP, IDMA UP. There was no pre-month disagreement in this audited signal set. This is not a simple 3M-lag error. A technical reversal override learned from these same signals would not have caught it ex ante.

### May 2023 — weak reversal, warning existed
Actual: 2000 -> 1992 (-0.40%).
3M remained UP, but Tactical Slow was persistent DOWN and Patch implied DOWN before May. VW/IDMA/1M remained UP. The move was very small, so this is better treated as low-confidence conflict than proof that Tactical should automatically flip the monthly direction.

### June 2023 — clearest correctable lag error
Actual: 1992 -> 1943 (-2.46%).
3M remained UP, but 1M had turned DOWN, Tactical Slow was persistent DOWN, and VW implied DOWN. This is the strongest evidence of a real turning-point lag in the monthly trend signal. Patch and IDMA still pointed UP, so the correction should be confidence/consensus-aware rather than a single-signal flip.

### October 2023 — scoring artifact / flat month
Actual: 1916 -> 1916 (0.00%).
3M predicted DOWN and is counted as a direction miss because actual direction is 0. This should not be treated as an economically meaningful reversal failure. Future direction scorecards should report a flat/dead-band diagnostic separately from binary UP/DOWN accuracy.

### November 2023 — clear upside reversal with disagreement
Actual: 1916 -> 1984 (+3.55%).
3M stayed DOWN. At the Oct-31 origin Tactical Slow was persistent UP, VW implied UP and IDMA implied UP; Patch remained DOWN and 1M was flat. This is a genuine reversal-disagreement case. Origin GPR diagnostic also jumped sharply (197.89 versus 98.63 in the preceding row), but this must not be turned into a threshold using 2023 hindsight.

## Important counterexamples
A naive rule `flip 3M whenever Tactical conflicts` is not justified. In March, July and August 2023 the 3M direction was correct despite Tactical conflict. Therefore Tactical conflict is useful as a confidence/reversal-warning state, not an unconditional flip rule.

## Conclusion
`ERROR_MECHANISM_2023 = MIXED`.
- February: collective surprise / no technical warning in audited origin signals.
- May: weak reversal with partial warning.
- June: clear trend-lag/reversal error and strongest candidate for causal correction.
- October: flat-month scoring artifact.
- November: clear upside reversal/disagreement and second strong candidate for causal correction.

The next minimal correction must be trained/frozen on pre-2023 development data and should focus on **multi-signal reversal disagreement**, not Tactical-alone or 1M-alone flipping. 2023 is diagnostic evidence, not the threshold-training set.
