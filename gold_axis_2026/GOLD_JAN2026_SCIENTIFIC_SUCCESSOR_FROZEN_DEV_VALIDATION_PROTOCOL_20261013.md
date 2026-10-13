# JAN-26 SCIENTIFIC SUCCESSOR — FROZEN DEVELOPMENT DESIGN
2026-10-13. Manifest records January model failure. This protocol is appended **after January results known**: 2026 Jan remains **prior-exposed stress check, not untouched final test**. Never market this as prospective success.

## Goal
Evaluate whether adding a **session-ending intraday risk-state overlay** to the PR#123 existing price-only AL/TUT/SAT baseline improves out-of-era 2023–25 cost-adjusted performance *before any parameter adaptation to Jan2026*. Binary long XAU or flat cash only. No leverage and no automatic intraday order here.

## Cohorts / information
2023 & 2024 = development EV bid/ask mid M15; each year starts full CASH with warmup from 2022 or 2023. 2025 = **validation EV M15**, not used for parameter choice. Jan2026 = **previously studied stressed period**, HistData M15 NY17 with warmup Sep-Dec2025, used after all rules frozen. Quote sources differ: cannot promote production without more independent source checks. Historical prices backfilled, provider publication time never proven (no true prospective PIT). NY17 session = last completed 15min midpoint bar; label exact end17 belongs ending date; >=70 bars; abnormal early sessions marked, note holiday limitations. All actionable state uses current/prior session data, never next one.

## Original benchmark B0
When CASH and r5>=1.2%, r20>0, close>=SMA10 => AL. When GOLD and r3<=-1.5% OR drawdown10<=-2% OR (close<SMA10 AND r5<=-0.5%) => SAT. Otherwise TUT. End-of-session decision, next eligible session first M15 quote fill, 0.8% on every action. Portfolio priced daily spot last bid/ask MID without actual bank spread. Same rules all cohorts, January should reproduce old PR#123 to numerical rounding.

## Locked exploratory overlay candidates
At session end, `session_ordered_dd = min_j (low_j / max_{k<=j} high_k - 1)*100`, computed using bars observed *no later than* end of same session; no leaking future bars into decision.
- B1_2: if GOLD and session_ordered_dd<=-2.0%, SAT, else B0.
- B2_3: threshold -3.0%.
- B3_4: threshold -4.0%.
- B4_5: threshold -5.0%.
All candidates use identical B0 AL rules. Signal ALWAYS next eligible quote, not intraday low/high. Conditional on SELL due intraday shock, **3 eligible-session cooldown** before allowing AL to avoid immediate churning; B0 has no cooldown. No extra daily sell if not already GOLD; end-of-session bar must exist. **Cooldown choice is provisional fixed design**, sensitivity may be studied only on DEV without retroactive 2025/Jan tuning.

## Selection gate (NO selection on 2025/Jan)
Evaluate full-year 2023 and 2024 independently. Promote an overlay **only if** (i) both 2023 and 2024 ending NAV after hypothetical last-day liquidation-fee haircut >= the corresponding B0 by at least +0.5 percentage points, (ii) both years max peak-to-trough end-session NAV drawdown does NOT worsen by >1 percentage point, (iii) total paid-action count per year <= 16, and (iv) no intraday lookahead, fabricated bank fill, or incomplete source. Choose eligible overlay with largest WORST annual absolute terminal-NAV improvement (2023/2024), tie -> fewest trades then higher trigger threshold. If no overlay qualifies, retain B0 as **NO_PROMOTION**. After selection freeze, report 2025 evaluation and Jan2026 stress results, including ALL candidates for transparency not selection.
- Primary metric: terminal net cash-equivalent NAV (open gold position valued after a **hypothetical** 0.8% sell-cost haircut at final eligible close, not executable at that close). Secondary actual NAV without last sale, max daily closed-mark DD, fee-paying action counts, exposure, false exits, time-in-market and risk-alert precision.
- Benchmarks: identical first eligible January session entry at *next* quote for always-gold with same fee valuation; cash=1.0.
- If any data, governance or sampling problem prevents head-to-head, report as blocker and no new performance claim.

## News and regime layer
Dated contemporaneous news (Jan3 Venezuela, Jan11 Powell, Jan17 Greenland and Jan29/30 technical/liquidity) and retrospective silver/PT/Pd, rates, risk indices may be inspected diagnostically, not optimization/real-time predictors absent trustworthy original availability timestamps. Do not add ex-post 2026 catalyst columns into training. Even a successful Jan overlay would merely detect an already occurring intraday shock, not forecast it before onset.

## Deliverables
Versioned 2023/2024 DEV and 2025 validation + Jan2026 stress metrics and explicit selection verdict; per-year decisions / realized next-session fills; no alteration of #123 ledger. All on new GitHub PR; official canonical manifest note already recorded.
