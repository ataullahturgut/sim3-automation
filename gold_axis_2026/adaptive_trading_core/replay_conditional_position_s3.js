"use strict";
/**
 * GOLD-ADAPTIVE-MODEL-APP-01 / SAME CORE: paired economic-ON/OFF shadow replay.
 * Consumes PRIVATE as-of M15, completed slow sessions and admitted economic
 * features. Never commits raw quotes, historical publication captures or
 * user portfolios. This is DISCOVERY_FULL_ARCHIVE, NOT independent OOS.
 *
 * node replay_conditional_position_s3.js PRIVATE_M15.json PRIVATE_SLOW.json PRIVATE_EVENT_BUNDLE.json
 * Event bundle: {economicSources:{source_id:{kind:"EVENT",evidenceStatus:"..."}},
 *                checkpoints:[{asof:"...Z",features:{cpi_surprise_z:{value,...}}}]}
 * Unknown/unverified feature metadata MUST be refused by existing S1.
 */
const fs=require("node:fs"),crypto=require("node:crypto");
const core=require("./adaptive_market_core_s1_s2");
const FEE=.008,MODES=["ECONOMIC_ON","MARKET_ONLY"];
const iso=t=>new Date(t).toISOString();
function run(bars,sessions,bundle={economicSources:{},checkpoints:[]}){
 if(!Array.isArray(bars)||bars.length<2||!Array.isArray(sessions)||
   !bundle||!Array.isArray(bundle.checkpoints)||!bundle.economicSources)
   throw Error("CP_REPLAY_PRIVATE_INPUT_REQUIRED");
 const sourceId=bars[0].source_id;
 if(typeof sourceId!=="string"||!sourceId)throw Error("CP_REPLAY_SOURCE_REQUIRED");
 const research=Object.fromEntries(MODES.map(mode=>[mode,core.create({
   sourceId,learningMode:"DISCOVERY_FULL_ARCHIVE",
   sourceEvidence:"RECONSTRUCTED_MARKET_ASOF",
   shadowResearch:true,positionResearchMode:"CONDITIONAL_ECONOMIC_RESEARCH",
   economicSources:bundle.economicSources
 })]));
 const features=new Map();
 for(const e of bundle.checkpoints){
  if(!e||!e.asof||!Number.isFinite(Date.parse(e.asof))||!e.features||
     features.has(e.asof))throw Error("CP_REPLAY_BAD_OR_DUPLICATE_EVENT_CHECKPOINT");
  features.set(e.asof,e.features);
 }
 let prev=-Infinity,slowIndex=0,usedEvents=0,lastPrice=null,firstPrice=null;
 const trades=Object.fromEntries(MODES.map(m=>[m,[]]));
 for(const row of bars){
  const t=Date.parse(row.bar_start_utc),p=(+row.bid_close + +row.ask_close)/2;
  if(!Number.isFinite(t)||t<=prev||row.source_id!==sourceId||
     !(+row.bid_close>0)||!(+row.ask_close>=+row.bid_close))
    throw Error("CP_REPLAY_NONMONOTONIC_PRICE_OR_SOURCE");
  prev=t;
  const at=iso(t+900000);
  while(slowIndex<sessions.length&&
    Date.parse(sessions[slowIndex].session+"T22:00:00Z")<Date.parse(at)){
   const item=sessions[slowIndex++];
   if(item.source_id!==sourceId||!Number.isFinite(+item.close_price))
     throw Error("CP_REPLAY_UNSAFE_SLOW_SESSION");
   const s={...item,n:+item.n,valid_quotes:+item.valid_quotes,
     max_gap_minutes:+item.max_gap_minutes,close_price:+item.close_price};
   for(const model of Object.values(research))core.observeSlowSession(model,s);
  }
  firstPrice??=p;lastPrice=p;
  const event=features.get(at);
  if(event)usedEvents++;
  for(const [mode,model] of Object.entries(research)){
   const before=model.s3.paper.holding;
   const point={asof:at,barStartedAt:iso(t),barMinutes:15,
      priceAvailableAt:at,price:p,priceSource:sourceId};
   if(mode==="ECONOMIC_ON"&&event)point.economicFeatures=event;
   const result=core.observe(model,point);
   if(model.s3.paper.holding!==before)
    trades[mode].push({at,side:model.s3.paper.holding==="GOLD"?"BUY":"SELL",
      researchMid:p,reason:result.positionResearch.researchDecisionReason});
  }
 }
 if(usedEvents!==features.size)throw Error("CP_REPLAY_UNUSED_EVENT_CHECKPOINT");
 const stats=Object.fromEntries(MODES.map(mode=>{
  const s=core.summary(research[mode]),p=s.positionResearch.portfolio,
    cp=s.positionResearch.conditionalPositionMemory;
  return [mode,{endingNetUsd:p.liquidatableNetUsd,holding:p.cashHolding,
    shadowTrades:p.shadowTrades,maxDrawdownPct:p.maxDrawdownPct,
    decisions:s.positionResearch.audit.decisionsByReason,
    economicAnchors:cp.audit.economicAnchors,matured:cp.audit.labelsMatured,
    researchTrades:trades[mode],liveTradeAuthorized:false}];
 }));
 return {project:"GOLD-ADAPTIVE-MODEL-APP-01",schema:"S3_CONDITIONAL_PAIRED_RESEARCH_V1",
  mode:"DISCOVERY_FULL_ARCHIVE",tradeAllowed:false,scienceGate:"NOT_PROVEN",
  realBankBidAskIncluded:false,feePerLeg:FEE,sourceId,
  bars:bars.length,admittedEconomicCheckpoints:usedEvents,
  passiveGoldNetUsd:100*(1-FEE)**2*lastPrice/firstPrice,
  passiveCashNetUsd:100,models:stats,
  incrementalEconomicWealthUsd:stats.ECONOMIC_ON.endingNetUsd-
     stats.MARKET_ONLY.endingNetUsd,
  warning:"Same-source retrospective MID research; no firstprint/consensus PIT certification by this runner and no blind/OOS claim"};
}
if(require.main===module){
 if(process.argv.length!==5)throw Error("Supply PRIVATE_M15 PRIVATE_SLOW PRIVATE_EVENT_BUNDLE");
 const raw=process.argv.slice(2).map(p=>fs.readFileSync(p,"utf8"));
 const result=run(...raw.map(JSON.parse));
 const hashes=raw.map(x=>crypto.createHash("sha256").update(x).digest("hex").slice(0,16));
 console.log(JSON.stringify({inputHashes:hashes,...result},null,2));
}
module.exports={run,MODES};
