# 2023→ ileri ay ay KAVİS öğrenme — ilk commit sözleşmesi (2026-10-16)

## Hedef ve deney tasarımı
2023-01-01 günü CASH 100 USD ile başlangıç; ilk uygun banka işlem kontrol noktası 2023-01-03, Türkiye 09:00/12:00/15:00 (UTC 06:00,09:00,12:00). Tarih boyunca yalnızca önceki tamamlanmış gözlemler ile AL/SAT/TUT. AL %0,8, SAT %0,8. Bir ay sonu durumundan sonraki aya model Q, gradient/adaptif moment, mevduat, altın birimi, high water mark, fee ve en son varlık pozisyonu **aynen taşınır**; her ay yeniden başlatma yasaktır.

## Veri
- Gold: `apps/portfolio_guard_v1/data/RECOVERY_HIST_3H_2023_2025_V1.csv` research price proxy p/c, NOT user's executable bank BID/ASK; source original historical source as-of quotes unconfirmed. Signal strictly from previous-row complete features; trade price current checkpoint source c, not prior fwd information.
- Nasdaq, US Treasury (ZN), silver / oil: `data/CROSSMARKET_ASOF_2023_2024_3H_V1.csv` joined with strict availability timestamp no later than previous gold observation; missing = missing, no imputation. Pre-existing V18 supported directly nq6; other crossmarket values shadow-only / diagnostic unless separately preregistered as model input.
- Macros: `GOLD_MACRO_EVENT_LEDGER_RAW_V1_2023_2025.csv` proof `surprise_ready_at_utc` after official event, require pair_complete and lineage before potential model integration; macro signals DISABLED until publication QC (no fabricated first prints).
- ETF/equities: inventory present but full source-vintage not established, no ETF/equity training feature falsely claimed. CME `GC.c.0` and `SI.c.0` sparse 2023; no raw continuous contract roll spanning trade as causal return.
- COT: `GOLD_COT_GOLD_PIT_STATE_RAW_REBUILT_2026-10-06.csv` with `cot_available_at_utc`, offline availability audit; optional later post-publication indicators only; no hindsight weekly report on its Tuesday report_date.

## Algorithms and frozen comparisons
- Engine A: existing mathematically trainable `v18_kavis_dayaniqlilik.js` Double Q price-only; feature vector (r4,r1,r3,rv,dd) from **previous completed** row.
- Engine B: same Double Q plus availability-safe NQ component, same parameters. 2023–2024 asof panel only; if unavailable in a given period, use NQ missing indicator instead of replacing it with a noncausal value. No hidden overnight NQ future leak. Both agents start with zero Q weights and each update only after matured price. No post-month restarts or off-policy fabricated best outcome.
- No R2/R3 until mathematical baseline and B audit: R3 failed prior acceptance, may not be silently promoted.
- Save month-end checkpoints and evaluate each month's actual CASH/GOLD positions, buy/sell count, fees and liquidation NAV. Compare to 100% CASH and single buy+hold. **No looking at next month before current month state frozen.**
- Beginning 2023-01 may be warmup with poor choices; still include the month and report unfavourable rows. Do not optimize 2023 backtest after reviewing outcomes. Shadow variants are parallel self-financing portfolios, their final NAV difference is not model's ability to pick the winning variant in advance.
- Source data include hindsight acquisition; chronology is simulated strictly with prior timestamps, not a literal historical bank execution proof. Research result not OOS, not guaranteed.
- Model math evolves online at every matured 3h interval. **Monthly scientific improvements** after loss analysis must be proposed separately and preregistered to apply beginning in FOLLOWING month only, NEVER rewrite the tested month. Across-month meta-controller adaptation is a proposed next stage, not invented in this initial comparison. No threshold sweep if failed.

## Acceptance
- No later-row price/quote/feature may influence signal.
- Every month end state is next month's identical start state, including Q and portfolio; no hidden reset.
- Fees once on BUY and once on SELL, terminal marked net liquidation.
- Rows/provenance completeness and missing indicators reported, not hallucinated.
- Original Jan2026 studies and older R3 branch left intact; new research branch only.
