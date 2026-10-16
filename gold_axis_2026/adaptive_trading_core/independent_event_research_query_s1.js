"use strict";
/**
 * S1 archive discovery, retrospective macro ledger (NOT true PIT).
 * Emit derived-return SQL for user's READ-ONLY Neon. Never publish licensed
 * prices, or claim January-2023 STRICT_WALK_FORWARD success.
 * node independent_event_research_query_s1.js private_macro_ledger.csv
 */
const fs=require("node:fs");
const csv=require("./economic_evidence_s1").csv;
const TZ=/^\d{4}-\d\d-\d\d[T ]\d\d:\d\d:\d\d(?:\.\d{1,3})?(?:Z|[+-]\d\d(?::?\d\d)?)$/;
function buildSql(ledger){
 const gr=new Map();
 for(const r of csv(ledger)){
  if(!["NFP","AHE","UNEMP","CPI"].includes(r.event_type)||
     r.pit_use!=="POST_RELEASE_ONLY"||r.pair_complete!=="True"||
     !r.actual_lineage_id||!r.consensus_lineage_id||!Number.isFinite(Number(r.surprise)))
    continue;
  if(!TZ.test(r.event_ts_utc))throw Error("MACRO_TIME_FORMAT");
  const t=new Date(r.event_ts_utc).toISOString();
  if(t<"2023-01-01T00:00:00.000Z"||t>="2026-01-01T00:00:00.000Z")continue;
  if(!gr.has(t))gr.set(t,{});
  if(r.event_type in gr.get(t))throw Error("DUPLICATE_COMPONENT_OF_ONE_RELEASE");
  gr.get(t)[r.event_type]=Number(r.surprise);
 }
 if(gr.size<20)throw Error("ARCHIVE_HAS_TOO_FEW_INDEPENDENT_RELEASES");
 const values=[...gr.entries()].sort(([a],[b])=>a.localeCompare(b)).map(([t,v])=>{
  const kind=("NFP" in v)?"EMP":"CPI";
  const nums=["NFP","AHE","UNEMP","CPI"].map(k=>k in v?String(v[k]):"NULL");
  return "('"+t+"'::timestamptz,'"+kind+"',"+nums.join(",")+")";
 }).join(",\n");
 return [
 "-- PRIVATE SQL: prices are transient to mature CORE labels; DO NOT LOG/COMMIT RAW PRICE ROWS.",
 "-- Archive source is post-event reconstructed NOT contemporaneous PIT.",
 "-- Same UTC clock negative controls selected on PRE-OUTCOME 1h gold move only.",
 "WITH ev(release_utc,release_family,nfp,ahe,unemp,cpi) AS (VALUES "+values+"),",
 "b AS MATERIALIZED (",
 " SELECT bar_start_utc,bar_start_utc+interval '15min' end_utc,close_price,native_minute_bars,",
 " lag(close_price,4) OVER (ORDER BY bar_start_utc) pre_close,",
 " lag(close_price,8) OVER (ORDER BY bar_start_utc) pre2_close,",
 " lag(bar_start_utc,8) OVER (ORDER BY bar_start_utc) pre2_start,",
 " lag(bar_start_utc,4) OVER (ORDER BY bar_start_utc) pre_start,",
 " lead(close_price,16) OVER (ORDER BY bar_start_utc) next_close,",
 " lead(bar_start_utc,16) OVER (ORDER BY bar_start_utc) next_start,",
 " min(native_minute_bars) OVER (ORDER BY bar_start_utc",
 " ROWS BETWEEN 4 PRECEDING AND CURRENT ROW) min_pre_complete,",
 " min(native_minute_bars) OVER (ORDER BY bar_start_utc",
 " ROWS BETWEEN CURRENT ROW AND 16 FOLLOWING) min_complete",
 " FROM gold_research_histdata_xau15m_candidate",
 " WHERE bar_start_utc>='2023-01-01' AND bar_start_utc<'2026-01-02'",
 "), a AS MATERIALIZED (",
 " SELECT end_utc,100*ln(close_price/pre_close) pre1h,",
 " 100*ln(pre_close/pre2_close) pre2h,",
 " 100*ln(next_close/close_price) next4h,",
 " close_price anchor_price,next_close due_price",
 " FROM b WHERE native_minute_bars=15 AND min_complete=15 AND min_pre_complete=15",
 " AND pre_start=bar_start_utc-interval '1h'",
 " AND pre2_start=bar_start_utc-interval '2h'",
 " AND next_start=bar_start_utc+interval '4h'",
 " AND close_price>0 AND pre_close>0 AND pre2_close>0 AND next_close>0",
 "), ea AS MATERIALIZED (",
 " SELECT ev.*,p.end_utc anchor_end,p.pre1h,p.pre2h,p.next4h,",
 " p.anchor_price,p.due_price",
 " FROM ev LEFT JOIN LATERAL (",
 " SELECT end_utc,pre1h,pre2h,next4h,anchor_price,due_price FROM a",
 " WHERE end_utc>=ev.release_utc+interval '60min'",
 " AND end_utc<=ev.release_utc+interval '75min'",
 " ORDER BY end_utc LIMIT 1) p ON TRUE",
 "), cc AS (",
 " SELECT e.release_utc,c.end_utc control_anchor,c.pre1h control_pre1h,",
 " c.pre2h control_pre2h,c.next4h control_next4h,",
 " c.anchor_price control_anchor_price,c.due_price control_due_price",
 " FROM ea e JOIN LATERAL (",
 " SELECT x.* FROM a x WHERE e.anchor_end IS NOT NULL",
 " AND EXTRACT(HOUR FROM x.end_utc)=EXTRACT(HOUR FROM e.anchor_end)",
 " AND EXTRACT(MINUTE FROM x.end_utc)=EXTRACT(MINUTE FROM e.anchor_end)",
 " AND x.end_utc BETWEEN '2023-01-01'::timestamptz AND '2025-12-31'::timestamptz",
 " AND NOT EXISTS(SELECT 1 FROM ev z",
 " WHERE x.end_utc BETWEEN z.release_utc-interval '24h'",
 " AND z.release_utc+interval '24h')",
 " ORDER BY abs(x.pre1h-e.pre1h),x.end_utc LIMIT 4) c ON TRUE",
 ")",
 "SELECT 'EVENT' kind,release_utc,release_family,nfp,ahe,unemp,cpi,",
 " anchor_end anchor_utc,pre1h,pre2h,next4h,anchor_price,due_price FROM ea",
 "UNION ALL",
 "SELECT 'CONTROL',release_utc,NULL,NULL,NULL,NULL,NULL,",
 " control_anchor,control_pre1h,control_pre2h,control_next4h,",
 " control_anchor_price,control_due_price FROM cc",
 "ORDER BY release_utc,kind DESC,anchor_utc"
 ].join("\n");
}
if(require.main===module){
 if(process.argv.length!==3)throw Error("Pass one private macro-ledger CSV filepath");
 process.stdout.write(buildSql(fs.readFileSync(process.argv[2],"utf8"))+"\n");
}
module.exports={buildSql};
