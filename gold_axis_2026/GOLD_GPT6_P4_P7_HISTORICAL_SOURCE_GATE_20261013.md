# GPT-6 P4 and P7 — forecast-dispersion and Shanghai market data gates
2026-10-13; no model run due to source gaps. Joint *metadata audit only*, not a completed economic falsification experiment.

## P4 — macro forecast disagreement and revision
READ-ONLY Neon Gold Control `winter-art-94880101`, `observations`. Five `MACRO_*CONSENSUS_PIT` series (NFP, CPI, CORE_CPI, UNEMP, AHE), each **126 rows = 126 distinct release dates** over 2016–2026. Each one stored consensus value per release, **no multi-vintage pre-announcement forecast revisions nor individual analyst distribution**. Most historical `available_as_of` timestamps equal the economic release instant itself (e.g., CPI 2025-01-15 13:30Z and NFP 2025-01-10 13:30Z); this cannot prove access to a consensus snapshot at 08:45TR on release day or one day before. Do NOT put same-day actual/consensus into an earlier prediction, or compute fictitious analyst dispersion from single consensus. More data would require an approved separately licensed, timestamp-archived feed. **P4 data gate BLOCKED**; does NOT refute the macro uncertainty mechanism.

SQL:
```sql
SELECT series_id, COUNT(*) rows, COUNT(DISTINCT observation_ts) event_dates,
       COUNT(DISTINCT available_as_of) asof_count
FROM observations WHERE series_id LIKE 'MACRO_%CONSENSUS_PIT'
GROUP BY 1 ORDER BY 1;
```

## P7 — SHFE/SGE Shanghai gold spot/futures opening and premium
Neon `information_schema.tables` query for `%shfe%,%sge%,%shanghai%` returns **zero** public tables. Neon `observations` series IDs queried for those terms and `%LBMA_PREMIUM%` also return **none**. Without origin-certified Shanghai intraday price, timezone/calendar, unit and contract-vintage alignment, no usable source for 16:00–16:30TR early SHFE opening flow or Shanghai/London premium. **P7 BLOCKED**; research/data acquisition needed, user authorization before paid API/credit or new provider contract.

Neither gate is a poor performance result. Neither is to be treated as approval to acquire fee-based data. No source tables modified; all auditable SQL in this note, independently verified before considering model fitting.
