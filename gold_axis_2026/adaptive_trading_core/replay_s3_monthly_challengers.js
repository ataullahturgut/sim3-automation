"use strict";
/**
 * One consistent fee + quote + time lineage for ALL 3 research S3 modes.
 * Uses PRIVATE reconstructed price rows. Historical discovery, not S4/S5
 * scientific acceptance, bank executable quotes, or investment advice.
 *
 * node replay_s3_monthly_challengers.js PRIVATE_M15_2023.json PRIVATE_SLOW_2023.json
 * The 15m rows use {bar_start_utc,source_id,bid_close,ask_close}; slow rows
 * are from S2_SLOW_EV_DUKA_SESSION_AUDIT_2020_2025.sql.
 */
const crypto=require("node:crypto"),fs=require("node:fs");
const core=require("./adaptive_market_core_s1_s2");
const MODES=["LEGACY_M15","MULTI_SESSION_RESEARCH","INTEGRATED_LONG_RESEARCH"];
const FEE=.008;
function run(bars,sessions){
 if(!Array.isArray(bars)||bars.length<2||!Array.isArray(sessions))
   throw Error("S3_COMPARISON_ROWS_REQUIRED");
 const sourceId=bars[0].source_id;
 if(typeof sourceId!=="string"||!sourceId)throw Error("S3_COMPARISON_SOURCE_INVALID");
 const runs=Object.fromEntries(MODES.map(mode=>[mode,core.create({
  sourceId,shadowResearch:true,learningMode:"DISCOVERY_FULL_ARCHIVE",
  positionResearchMode:mode})]));
 let prev=-Infinity,slowIndex=0,first=null,last=null,oldMonth=null;
 const trades=[],months=[];
 const monthSnap=(month)=>({month,...Object.fromEntries(MODES.map(mode=>{
  const s=runs[mode].s3.paper;
  return[mode,{holding:s.holding,wealthNetIfLiquidated:s.cash+
    s.goldOunces*last.price*(1-FEE),trades:runs[mode].s3.audit.shadowTrades}];
 }))});
 for(const bar of bars){
  const t=Date.parse(bar.bar_start_utc);
  if(!Number.isFinite(t)||t<=prev||bar.source_id!==sourceId||
   !(Number(bar.bid_close)>0)||!(Number(bar.ask_close)>=Number(bar.bid_close)))
   throw Error("S3_COMPARISON_NONMONOTONIC_OR_INVALID_PRICE_SOURCE");
  const month=new Date(t).toISOString().slice(0,7);
  if(oldMonth!==null&&oldMonth!==month)months.push(monthSnap(oldMonth));
  oldMonth=month;prev=t;
  const price=(Number(bar.bid_close)+Number(bar.ask_close))/2,end=t+900000;
  while(slowIndex<sessions.length&&
     Date.parse(sessions[slowIndex].session+"T22:00:00Z")<end){
   const a=sessions[slowIndex++];
   if(a.source_id!==sourceId||!a.session||!Number.isFinite(+a.close_price))
    throw Error("S3_COMPARISON_SLOW_SOURCE_INVALID");
   const s={...a,n:+a.n,valid_quotes:+a.valid_quotes,
    max_gap_minutes:+a.max_gap_minutes,close_price:+a.close_price};
   for(const model of Object.values(runs))core.observeSlowSession(model,s);
  }
  first??={at:new Date(end).toISOString(),price};
  last={at:new Date(end).toISOString(),price};
  for(const [mode,model] of Object.entries(runs)){
   const was=model.s3.paper.holding;
   const q=core.observe(model,{asof:last.at,priceAvailableAt:last.at,
    barStartedAt:new Date(t).toISOString(),barMinutes:15,
    priceSource:sourceId,price});
   if(model.s3.paper.holding!==was){
    trades.push({mode,at:last.at,action:model.s3.paper.holding==="GOLD"?"BUY":"SELL",
     executionResearchMid:price,researchDecisionReason:q.positionResearch.researchDecisionReason});
   }
  }
 }
 months.push(monthSnap(oldMonth));
 const summaries=Object.fromEntries(MODES.map(mode=>{
  const s=core.summary(runs[mode]),p=s.positionResearch.portfolio;
  return[mode,{endNetUsd:p.liquidatableNetUsd,totalShadowTrades:p.shadowTrades,
   holding:p.cashHolding,maxDrawdownPct:p.maxDrawdownPct,
   feesUsd:p.feeUsdShadow,decisionCounts:s.positionResearch.audit.decisionsByReason,
   s1Predictions:s.positionResearch.audit.s1ResearchForecastReceived,
   slowSessionsAccepted:s.audit.slowAccepted,
   sessionLabelsMatured:s.positionResearch.positionMemory.audit.maturedLabels,
   longCycleLabelsMatured:s.positionResearch.longCycleMemory.audit.mature14+
       s.positionResearch.longCycleMemory.audit.mature56,
   longCycleMissedUp:s.positionResearch.longCycleMemory.audit.missedUp,
   longCycleAvoidedLoss:s.positionResearch.longCycleMemory.audit.avoidedLoss,
   shadowModeOnly:true}];
 }));
 return {schema:"S3_CHALLENGERS_V1",project:"GOLD-ADAPTIVE-MODEL-APP-01",
  modelMode:"DISCOVERY_FULL_ARCHIVE",priceProvenance:"RECONSTRUCTED_MID_NOT_BANK_QUOTE",
  scientificApproval:false,tradeAllowed:false,autoTrade:false,sourceId,
  bars:bars.length,first,last,feePerLeg:FEE,
  cashBaselineUsd:100,
  passiveGoldNetUsd:100*(1-FEE)**2*last.price/first.price,
  models:summaries,monthly:months,trades,
  warning:"2023 has been viewed during development; in-sample shadow research, no blind edge proof"};
}
if(require.main===module){
 if(process.argv.length!==4)throw Error("Supply PRIVATE_M15 and PRIVATE_SLOW JSON paths");
 const a=fs.readFileSync(process.argv[2],"utf8"),
   b=fs.readFileSync(process.argv[3],"utf8");
 const runId=crypto.createHash("sha256").update(a).update(b).digest("hex");
 console.log(JSON.stringify({runId:runId.slice(0,20),
  barInputHash:crypto.createHash("sha256").update(a).digest("hex"),
  slowInputHash:crypto.createHash("sha256").update(b).digest("hex"),
  ...run(JSON.parse(a),JSON.parse(b))},null,2));
}
module.exports={MODES,run};
