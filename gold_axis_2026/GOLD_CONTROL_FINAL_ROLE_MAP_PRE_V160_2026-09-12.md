# Gold Control Final Role Map — Pre-V1.60 Freeze

**Date:** 2026-09-12  
**Status:** FROZEN BEFORE V1.60 SCORING  
**Production authority:** NONE

| Component | Target/clock | Evidence interpretation | Frozen role |
|---|---|---|---|
| VW/MIDAS monthly level expert | Monthly H=1 price level | Useful monthly specialist; separate from direction | CORE MONTHLY LEVEL EXPERT |
| CAUSAL_PATCH | Monthly H=1 price level | Monthly benchmark/challenger | MONTHLY LEVEL EXPERT |
| MOMENTUM_3M | Monthly H=1 price level | Monthly benchmark/challenger | MONTHLY LEVEL EXPERT |
| RANDOM_WALK | Monthly H=1 price level | Mandatory benchmark | MONTHLY BENCHMARK |
| Employment + Inflation Event Specialist | Event-time, primary R15 | Strongest directional research lane; future prospective shadow required | CORE EVENT SPECIALIST |
| FOMC event lane | Event-time | Separate diagnostic; weaker/smaller support | EVENT DIAGNOSTIC |
| H20 LEGACY RTQ R126 | Normal-day H20 direction | Conditional signal; 2025 one-class failure, 2026 strong | H20 SELECTIVE EXPERT |
| H20 DRIVER RTQ R126 | Normal-day H20 direction | Corrected-driver challenger; not unconditional winner | H20 SELECTIVE EXPERT |
| FAST | Short trend context | Context only | TREND CONTEXT |
| SLOW | Slow trend context | Context only | TREND CONTEXT |
| MONTHLY_DIRECTION_3M | Strategic direction | Prior/context only | STRATEGIC PRIOR |
| BOCPD | Structural break state | Regime detector only | REGIME CONTEXT |
| GVZ | Volatility/risk | Confidence/risk only | RISK CONTEXT |
| Emergency Level/Reversal | Extreme displacement/reversal state | Context/veto geometry; not independent daily direction authority | REVERSAL/RISK CONTEXT |
| Market Shock V3 | Post-release shock confirmation | Initial event confirmation only; not continuation forecast | EVENT CONFIRMATION |
| General normal-day H1 direction | H1 | Repeatedly not proven | NO_SIGNAL_UNTIL_SEPARATELY_PROVEN |

## V1.60 eligibility rule

Only the two already-frozen H20 RTQ experts may compete for normal-day H20 selection. Context engines may define regime state but may not cast equal directional votes. Event and monthly engines remain outside the H20 selector because their targets and clocks are different.

If no H20 expert has enough matured, two-class, two-direction evidence in the current causal regime, V1.60 must return `NO_SIGNAL`.
