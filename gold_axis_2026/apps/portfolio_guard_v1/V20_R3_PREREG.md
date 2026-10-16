# V20 KAVİS–ATLAS R3 — PREREG / ÖN KAYIT (İLK VE TEK DOSYALI COMMIT)
2026-10-16. Parent branch: research-gold-v20-r2-shadow-prereg-20261016. No R3 algorithm or tests existed on this branch when this was committed.

## Frozen architecture
- riskMode: `alert` only in R3, real portfolio DD is an **alert**. `constrained` is **unsupported/rejected** until separate R4. `maxDrawdownPct` optional and alert-only. No hard drawdown cap or guaranteed stop.
- shadowGate independent: `off` default; `gated` only when explicitly selected. No maxDrawdownPct required to turn profit adviser on. The base V18 Double-Q is unchanged and trusted when gate is off.
- λ/R3 riskPenaltyLambda=0; dual ascent η=0 (INACTIVE). R4 must separately preregister positive η, DD reward and training, not sneak into R3.
- Block=16 **accepted bank checkpoints**; minimum 8 completed NONOVERLAPPING blocks (128 eligible observations); rolling evidence uses last 8 complete blocks. A fresh block score evaluated ONLY when 16 new observations mature. Raw history retained 8192 observations, not truncated to 32.
- Statistic: eight block sums of fee-net relative log-NAV, studentized t=mean(blockSums)/(sampleSD(blockSums)/sqrt(8)+1e-9). For all-equal-positive degenerate blocks, t capped at 12.0; for all-equal zero t=0. Block scores have no formal independence or distribution-free guarantee.
- Opening: after a block ends, two CONSECUTIVE eligible block scores `t>=T_OPEN` required. T_OPEN is NOT selected against outcome: it is determined once from exactly 500 separate drift-zero null worlds. Closing: immediately if current full block score `t<0` OR last two complete block sums are negative. Gate never opens mid-block. On quote expiry, no new false block labels, close gate pending revalidation.
- Calibration: 500 seeds = 100000 + i*37, i=0..499, 300 price checkpoints EACH, paired fee 0.008 and 0.025; one simulated zero-drift walk per seed, both fees. The maximum of the two fee paths' repeated two-confirmation block t-statistic is the per-seed test statistic. Select MINIMUM T_OPEN in grid [0,12] increments 0.1 with empirical fraction of these 500 per-path maxima at/above threshold <=0.05. If none -> R3 fails; do not extend grid. Freeze found value in calibration lock commit before evaluation data.
- Holdout zero-drift: **200 disjoint seeds** 200000 + i*53, i=0..199, each with both fees, 300 checkpoints. Per-seed false-open if EITHER fee opens at least once, unconditional. Threshold <=5% observed; Wilson 95% uncertainty interval reported. Capital delta mean across paired fee worlds >= -0.10 USD.
- Market families at least 32 NEW seeds EACH, two bank fee tiers each = 384 family-fee cases plus 200x2 null checks. Each has 300 checkpoints. Seeds fixed: for family j=0..5, i=0..31, seed=410000+10000*j+137*i; NO reusing V18/R2 scenario generator/seed set. Families: (0) drift-zero unbiased random walk (stress of transaction fees); (1) negatively autocorrelated mean-reversion returns; (2) persistent directional trend balanced 16 UP/16 DOWN paths; (3) alternating trend↔flat regimes; (4) fat-tail sudden jumps and recoveries; (5) switching low/high volatility. Family generation formula / noise parameters fixed in source before any eval runs, without tuning afterwards.
- Warmup=128 checkpoint observations to qualify; daily decision uses last COMPLETE block confidence status, never same-period price. When gate open, the target is the shadow risk portfolio's **post-rule-action intended position** at this checkpoint, NOT the old position. If base GOLD/CASH differs, align BUY/SELL on the same accepted bank quote; if quote is invalid, neither should change. Tests must assert post-fill positions match while gate open.
- Full shadow portfolios are independent and causal from R2; each pays verified simulated bank fee once per real virtual SWITCH. No future price leakage, and stale/bad quotes cannot earn blocks.
- Checkpoint restore: validate audit counters, pending action, portfolio consistency; reconstruct rolling evidence AND gate/hysteresis from a serializable completed-block event ledger, not trusting user-provided `lastEvidence`, `confirmedStreak`, `gateOpen`. If internal history is corrupted, fail closed or reject; never accept forged opened gate.

## PREDECLARED acceptance gates (ALL must pass; no after-failure threshold scan)
| Gate | Criteria |
|---|---|
| Null false gate opening in NEW 200 paths | <=5% of paired paths (either fee); report Wilson 95% interval |
| Null & mean-reversion mean portfolio delta | >= -0.10 USD EACH cohort |
| Mean delta of EVERY scenario family | >= -1.00 USD |
| Top 3 positive contributors share | <=40% of all positive delta gains; zero gains -> reject claim of alpha |
| Family comparisons | Separate paired outcomes and CIs; NEVER one pooled p-value |
| Default flags riskMode=alert, shadowGate=off | Exact V18 128/128 using unrounded capital and identical action & Q state |
| Gate state | No early opening; non-overlap; two complete positive blocks; closure within 2 completed negative evidence blocks; forged state cannot open |
| Alignment | Gate-active accepted checkpoint => actual CASH/GOLD position equals risk shadow target after same checkpoint |
| Flag isolation | shadowGate on/off changes only adviser authority, riskMode=alert never overrides; hard/constrained R3 unsupported |
| Risk policy | R3 only alert, no risk penalty, λ=η=0. Test %5/%15/%50 DD warning differences, ZERO action differences |
| Prior results | 128 previously exposed worlds diagnostic ONLY, not used for T_OPEN calibration or scientific acceptance |

## Anti-selection / release rule
**Başarısız olursa eşik taraması yapılmaz.** If any gate fails, tag R3 research FAILED, no retuning of T_OPEN, z, seeds, window, thresholds, λ, η, or hidden alternative datasets.
Separate calibration and evaluation seed sets, immutable reference branch and first prereg commit are the audit evidence.
Report all wins/losses, avg and worst capital, max DD, cash/passive gold, trade counts, bank fee and real-world limitation.
Real XAU and bank bid/ask as-of adapter is outside R3; this entire stage is synthetic and never authorizes actual bank orders.