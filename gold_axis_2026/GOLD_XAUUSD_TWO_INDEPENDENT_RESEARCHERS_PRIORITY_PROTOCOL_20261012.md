# XAU/USD SHORT-HORIZON — PAIRED INDEPENDENT RESEARCH PROGRAM
## Non-authoritative coordination protocol, 2026-10-12

**Objective:** materially improve decision-time-valid future XAU/USD **return, direction and future price**, not TRY/gram, bank utility or execution. This plan DOES NOT replace established manifests, data authority, training contracts or champions. It only governs the independent Claude-versus-GPT research queue.

**Two independent investigators:** CLAUDE and GPT-6. Use **the exact same source rows, frozen candidate definition, dates, clocks, simple baselines and evaluation scripts/metrics** where possible; develop/implement independently, store separate PRs. Each must preregister hypotheses before opening postdecision targets. Neither sees the other's *experimental outcome* until its own artifact/report is frozen; seeing common prereg/legacy results is allowed.

**Known current status:** old 74% daily and native D0→D3 H3 direction do NOT establish decision-time-forward predictability. PRs #85/86/89/90/91/92 and R7/R8, R15–R30, R38, R66–R73, BSC-8, QBoost, OPAL/HELIOS are background and cannot be relabeled novel. 2025/26 previously examined repeatedly; NOT virgin OOS. Original spot, vendor and source publication times are not fully proven prospective.

### P0 — Neon's frequent permissions, precondition
- The repository's `CLAUDE.md` already authorizes *research* `SELECT`, but text instructions DO NOT modify Claude Code platform/tool approval. Do not bypass auth.
- Connect Claude Neon MCP **project-scoped read-only** if appropriate: `https://mcp.neon.tech/mcp?readonly=true&projectId=winter-art-94880101`; select/read-only OAuth grant, never share secrets.
- In Claude Code `/permissions`, permit the **actual registered MCP tool name** for schema and `run_sql` **only after verifying Neon-side readonly is active**; don't blanket-allow server, Bash, write, migrations, OAuth scope expansion or all-tools approvals. If repeated prompt is OAuth instead of tool-use, capture sanitized prompt and troubleshoot separately. Developer must make these local settings changes and approve once; GitHub cannot change a private local Claude configuration.
- If read-only project scope cannot be verified, **STOP** and ask user instead of weakening approvals. For other external sources, honor credential/minimum-scope and budget limitations. GPT reads through connected Neon; these are independent clients and OAuth grants.
- For reproducibility prefer `run_sql SELECT` and commit source-bound SQL, aggregate month/day feature panels and per-target comparisons; avoid copying giant market data or private secrets.

### Common strict clock and fairness contract
- Türkiye timezone `Europe/Istanbul`, local UTC+3; US economic releases `America/New_York` and date-aware DST; one decision cutoff = **08:45** for DAY 09:00→16:45, **16:30** for OVN16:45→next09:00 Mon–Thu, and H3 at fixed origin 09:00 or 16:45 to third source trading day same clock. No mixing native D0-avg→D3-avg with exact-clock direction.
- Input M15 bar beginning at timestamp t is only known after t+15min plus any live receipt latency. Use latest strictly completed bar by issue-time; if no provable first receipt timestamp mark historical approximation (not live certified).
- Choose one primary outcome per experiment: **future log return** with RMSE/MSE and RW zero return; direction with accuracy + balanced accuracy + both class recalls vs always-UP/empirical prior; if forecasting RV, QLIKE/CRPS/quantiles separately. Return-price `P_future=P_origin*exp(rhat)` and level MAE on exact source cohort. Score row-matched; no unpaired literature metrics.
- 2020–2022 historical warmup where source coverage available, 2023–24 DEV, 2025/26 opened transport. Reporting per year and vendor with n and CI mandatory. Dependence for overlapping D3 via purging/nonoverlap and HAC/block bootstrap. Multiplicity across experiments and variants logged; frozen original models untouched. No optimizing on 2025/26.

### PRIORITY ORDER — BOTH RESEARCHERS FOLLOW IDENTICALLY

| Stage | Topic; causal economic hypothesis | Data / novelty vs prior work | Primary prerequisite, falsifier and success gate |
|---|---|---|---|
| **P1** | **Correct conditional session/DST baseline**: separate London/COMEX/Asia and US release-aware pre-issue state, quantify where UP/down base rates already explain labels. | Existing M15 XAU spot and exchange schedule; complements old clock audits but NO new fitted H3. | Original archived clock/source checks; freeze segment definitions BEFORE scores. If unconditional segmentation adds no stable OOS log-loss or future return skill vs intercept / RW per 2023,24 and opened 2025, classify **BASELINE_ONLY**. |
| **P2** | **FOMC announcement response → next TR DAY returns**. Distinguish *pre-FOMC price drift reversal* vs *post-FOMC first 45min reaction reversal*. Do not claim FX evidence establishes gold effect. | Existing M15 spot + official scheduled Fed announcement 14:00 ET per-date, planned vs emergency flags. Never use outcome at 08:45. | 2020–24 scheduled events (~40), correct baseline matched non-FOMC Wed→Thu; sample too small for modest effect. One frozen primary test, separate secondary Holm; sign wins + paired errors + CI. No day/window threshold fishing. 2025/26 previously opened. |
| **P3** | **Macro calendar-aware XAU future-window log return distribution and RV**. Event schedule may forecast shock probability, but direction is separate. | Existing PR #91 session HAR and RV controls, scheduled BLS/Fed preissue calendar, previous-session RV, prior GVZ if PIT. **Original macro event vintages/exception dates need verification.** | Compare HAR sliding/expanding to **Persist5** (the strong 2025 comparator), CLIM60 and frozen H3A; event coefficient only if known before issue. Test both signed conditional return/quantile score and RV/QLIKE. Report if only RV improves; no signed-direction promotion. |
| **P4** | **Consensus revisions and forecast dispersion before release**: unpriced macro uncertainty vs price-only baseline. | Neon CPI/NFP consensus *levels* exist; dispersed analyst-by-analyst vintage and revisions may be absent; prospective provider/data license cost needs check. | First run coverage/vintage/provenance audit without data purchase; if only current consensus/after-event surprise, mark **BLOCKED** not synthetic. Else preissued information, chronological test on event windows and alternatives. |
| **P5** | **COMEX→spot information share/lead-lag persistence** at exact decision hours and 15m/1h/4h/7h/16h. Test source-lag, not contemporaneous discovery statistics. | CME hourly OHLCV and XAU spot M15 currently available, but authentic signed order flow and depth not; DataBento trades/tbbo/mbp may cost money. | Start with zero-cost price/quote timestamps; **stop** if lead-lag effect vanishes before intended horizon. Order-flow paid data only after explicit user permission, with cost quote. |
| **P6** | **Probabilistic price forecast / GPR or local-level state-space** as methodological control, NOT new-information mechanism. | Jin & Xu 2025 level reports cannot substitute for own future-return OOS; do not confuse geometric drift with skill. | Compare exact-clock price-level MAE/RMSE against spot last-price RW and return-based intercept, 2023–24→opened 2025/26; reject if no stable incremental returns or direction calibration. |
| **P7** | **SHFE/SGE Shanghai premium and opening information** (optional after P1–P6). | Foreign venue data/vintage/licensing unclear; do not proxy lookahead with retro revisions. | Only source/cost/firstprint survey until auditable as-of data exists; no paid data without user approval. |

### Every stage result — standard format
1. **What was predicted**: price/return/direction/RV; strict issue time, exact source and future target hour, denominator n.
2. **Why this model**: literature mechanism and exact comparison vs previous experiments (not just naming ML architectures).
3. **Data gate**: source time, lookahead, missingness, licensability, as-of revision.
4. **Baselines and scientific gate**: row-matched RW, class prior, past HAR Persist5 and previous champion when same target available.
5. **Four year/year blocks** where eligible + matched rows, 2025/26 OPENED; confidence intervals, corrected multiple comparisons, sign flips and failure analysis.
6. **Final independent result:** REJECT / TENTATIVE / BLOCKED; no retroactive tuning rescue; negative result saved with exact code/output hashes. Compare independent artifacts **only after both frozen**.
7. Two distinct GitHub branches per stage, e.g. `research-claude-p1-...` and `research-gpt6-p1-...`. Only separate OPEN PRs to `gold-execution-channel-audit-20261006`; no direct canonical writes or merge, no shared branch overwrites.

### Source bibliography starting points
- Hauptfleisch, Putniņš & Lucey (2016), *Who Sets the Price of Gold? London or New York* (PRICE DISCOVERY, not predictive accuracy).
- Elder, Miao & Ramchander (2012), macro news, gold futures reaction.
- Bonato et al. (2018), quantile-boosting realized moments, not calibrated exact-clock h=1 direction.
- Corsi (2009), HAR-RV; Jin & Xu (2025), Gaussian-process level forecast; Smales & Yang forecast disagreement.
- Lee & Wang (2025), post-FOMC FX reversal; **not directly evidence gold post-FOMC reversal**.
- Cont et al. (2014/2023), order-flow short-lived price information; theoretical transport risk.
