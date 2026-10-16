"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01 / S2 historical completed-M15 replay.
 * Research-only, private data. No S1 causal macro, no trades, no trained alpha.
 * SQL (READ-ONLY):
 * SELECT bar_start_utc,close_price,source_id,native_minute_bars
 * FROM gold_research_histdata_xau15m_candidate
 * WHERE bar_start_utc >= '2023-01-01' AND bar_start_utc < '2026-01-01'
 * ORDER BY bar_start_utc;
 *
 * node replay_phase_lifecycle_s2.js PRIVATE_ROWS.json [--integrated-core]
 * Outputs aggregate scores and input SHA only; NEVER prints market prices
 * or serialized checkpoints containing licensed original prices.
 */
const fs=require("node:fs"),crypto=require("node:crypto");
const phase=require("./adaptive_phase_lifecycle_s2");
const integrated=require("./adaptive_market_core_s1_s2");
const utc=x=>{
 if(typeof x!=="string"||!Number.isFinite(Date.parse(x))||
   !/(?:Z|[+-]\d\d:\d\d)$/i.test(x))throw Error("S2_REPLAY_INVALID_UTC");
 return Date.parse(x);
};
function replay(rows,{withS1=false}={}){
 if(!Array.isArray(rows)||!rows.length)throw Error("S2_ROWS_REQUIRED");
 const sourceId=rows[0].source_id;
 if(typeof sourceId!=="string"||!sourceId)throw Error("S2_SOURCE_MISSING");
 const sourceIds=[...new Set(rows.map(x=>x.source_id))];
 if(sourceIds.some(x=>typeof x!=="string"||!x)||sourceIds.length>4)
  throw Error("S2_MALFORMED_SOURCE_ALLOWLIST");
 const sourceRegistry=Object.fromEntries(sourceIds.map(id=>[id,
  {kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"}]));
 const state=withS1?integrated.create({sourceId,sourceIds}):phase.create({sourceRegistry});
 let previous=-Infinity,passed=0,rejected=0;
 for(const r of rows){
  const start=utc(r.bar_start_utc);
  if(start<=previous)throw Error("S2_RAW_DATA_NOT_CHRONOLOGICAL");
  previous=start;
  if(!sourceIds.includes(r.source_id))throw Error("S2_UNDECLARED_SOURCE");
  if(+r.native_minute_bars!==15){rejected++;continue;}
  const p=Number(r.close_price);
  if(!Number.isFinite(p)||p<=0)throw Error("S2_PRICE_NOT_FINITE");
  const end=new Date(start+15*60000).toISOString();
  const ob={asof:end,barStartedAt:r.bar_start_utc,barMinutes:15,
   price:p,priceSource:r.source_id,priceAvailableAt:end};
  if(withS1)integrated.observe(state,ob);
  else phase.observe(state,ob);
  passed++;
 }
 const phaseState=withS1?state.s2:state;
 phase.closeAtEndOfSample(phaseState);
 const result=withS1?integrated.summary(state):{lifecycle:phase.summary(state)};
 return {project:"GOLD-ADAPTIVE-MODEL-APP-01",stage:"S2",
  mode:"DISCOVERY_FULL_ARCHIVE",withExistingS1Core:withS1,
  scienceGate:"PENDING_NOT_ALPHA_PROVEN",sourceId,sourceIds,
  inputRows:rows.length,validCompletedM15Bars:passed,
  rejectedIncompleteM15Bars:rejected,
  firstBar:rows[0].bar_start_utc,lastBar:rows.at(-1).bar_start_utc,
  ...result};
}
if(require.main===module){
 if(process.argv.length<3||process.argv.length>4||
  (process.argv[3]&&process.argv[3]!=="--integrated-core"))
  throw Error("Use PRIVATE_ROWS.json [--integrated-core]");
 const raw=fs.readFileSync(process.argv[2],"utf8");
 const hash=crypto.createHash("sha256").update(raw).digest("hex");
 const report=replay(JSON.parse(raw),
  {withS1:process.argv[3]==="--integrated-core"});
 console.log(JSON.stringify({runId:"S2_RESEARCH_"+hash.slice(0,16),
  inputSha256:hash,...report},null,2));
}
module.exports={replay};
