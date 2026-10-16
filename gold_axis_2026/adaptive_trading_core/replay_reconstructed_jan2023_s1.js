"use strict";
/**
 * READ-ONLY S1 economic *market-context* prototype experiment.
 * Data from JAN2023_RECONSTRUCTED_ASOF_S1_INPUT.sql. Never upload licensed rows.
 * Source-timing is reconstructed from completed bars, NOT independently
 * certified first-available-in-2023. NOT a trading strategy.
 */
const fs=require("node:fs");
const core=require("./adaptive_rule_discovery_s1");
const XAU="HISTDATA_XAUUSD_M1_FIXED_EST_M15_2022_2024_QC_CANDIDATE_V1";
const CME="DATABENTO_GLBX_MDP3_OHLCV_1H_CALENDAR_CONTINUOUS_C_SOURCE_V1";
const SCHEMA=["gold_1h","nq_1h","zn_1h","cl_1h"];
const finite=x=>typeof x==="number"&&Number.isFinite(x);
function utc(s){
  if(typeof s!=="string"||!/(Z|[+-]\d\d:\d\d)$/i.test(s)||
     !Number.isFinite(Date.parse(s)))throw Error("TIMESTAMP_WITH_UTC_OFFSET_REQUIRED");
  return Date.parse(s);
}
function feature(t,at,value,source,metrics){
  if(value===null||value===undefined)return null;
  const n=Number(value);
  if(!Number.isFinite(n))throw Error("INVALID_FEATURE_VALUE");
  const observed=utc(at);
  if(observed>t||t-observed>75*60000)throw Error("STALE_OR_FUTURE_H1_FEATURE");
  // Fixed engineering scale set BEFORE seeing the realized outcome.
  // 1.5 percentage point move = 1 normalized unit, clipped at [-5,5].
  const unbounded=n/1.5,normalized=Math.max(-5,Math.min(5,unbounded));
  if(normalized!==unbounded)metrics.clipped++;
  return {kind:"MARKET",value:normalized,observedAt:at,availableAt:at,source};
}
function make(options={}){
  return core.create({featureNames:SCHEMA.slice(),
    horizons:[240,1440,4320,10080,20160],anchorMinutes:240,
    noveltyDistance:options.noveltyDistance??.3,maxRules:options.maxRules??16,
    maxLateMinutes:15,
    sourceRegistry:{[XAU]:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"},
      [CME]:{kind:"MARKET",evidenceStatus:"RECONSTRUCTED_MARKET_ASOF"}}});
}
function run(rows,options={}){
  if(!Array.isArray(rows))throw Error("ROWS_ARRAY_REQUIRED");
  const s=make(options);
  const quality={rows:rows.length,source:"NEON_RECONSTRUCTED_COMPLETED_BAR_RESEARCH",
    truePointInTimeVintage:false,firstPrintEconomicNewsValidated:false,
    cmeContinuousRollPointInTimeValidated:false,clipped:0,
    featureCoverage:{gold_1h:0,nq_1h:0,zn_1h:0,cl_1h:0},
    rulesNotTradeSignals:true};
  let prior=-Infinity,anchored=0;
  for(const row of rows){
    const t=utc(row.end_utc),bar=utc(row.bar_start_utc);
    if(t<=prior||t-bar!==15*60000)throw Error("BAR_ORDER_OR_DURATION");
    prior=t;
    if(t<Date.parse("2023-01-01T00:00:00Z")||
       t>=Date.parse("2023-02-01T00:00:00Z"))
       throw Error("JAN2023_ONLY");
    if(row.source_id!==XAU)throw Error("SOURCE_ID_NOT_WHITELISTED");
    const v={};
    v.gold_1h=feature(t,row.end_utc,row.gold_1h_pct,XAU,quality);
    v.nq_1h=feature(t,row.nq_end,row.nq_1h_pct,CME,quality);
    v.zn_1h=feature(t,row.zn_end,row.zn_1h_pct,CME,quality);
    v.cl_1h=feature(t,row.cl_end,row.cl_1h_pct,CME,quality);
    for(const [k,z] of Object.entries(v))if(z)quality.featureCoverage[k]++;
    const obs={asof:row.end_utc,price:Number(row.close_price),
      priceAvailableAt:row.end_utc,priceSource:XAU,
      barStartedAt:row.bar_start_utc,barMinutes:15,
      features:Object.fromEntries(Object.entries(v).filter(([,z])=>z!==null))};
    if(core.observe(s,obs).anchored)anchored++;
  }
  const learned=core.rules(s);
  return {
    audit:{...quality,firstAsOf:rows[0]?.end_utc??null,
      lastAsOf:rows.at(-1)?.end_utc??null,
      observations:s.audit.observations,anchors:anchored,
      rules:learned.length,created:s.audit.ruleCreated,merged:s.audit.ruleMerged,
      rejectedAsNovel:s.audit.rulesSaturated,
      matureLabels:s.audit.labelsMatured,
      skippedLabels:s.audit.labelsSkipped,pendingLabels:s.pending.length,
      bankTrades:0,status:"S1_RESEARCH_ONLY_ECONOMIC_CAUSALITY_UNVERIFIED"},
    learnedRules:learned,
    checkpoint:core.checkpoint(s)
  };
}
if(require.main===module){
 const args=process.argv.slice(2);
 if(args.length!==1)throw Error("Use: node replay_reconstructed_jan2023_s1.js private_export.json");
 const rows=JSON.parse(fs.readFileSync(args[0],"utf8"));
 const result=run(rows);
 // Only derived summary to stdout; raw prices, pending prices and checkpoint
 // remain in private memory/storage controlled by the researcher.
 console.log(JSON.stringify({audit:result.audit,learnedRules:result.learnedRules},null,2));
}
module.exports={run,make,feature,XAU,CME,SCHEMA};
