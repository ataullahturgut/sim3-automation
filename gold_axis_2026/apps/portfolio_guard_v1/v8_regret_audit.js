"use strict";
/** Research-only V8 audit. Does not promote, modify or replace legacy V1-V7. */
const {loadFullRows,replay}=require("./v8_regret_engine");
const {runResearch:runV7}=require("./adaptive_v7_app");
const VERSION="V8_REGRET_SHADOW_REJECT_PROMOTION_20261015";
let cache=null;
function assess(){
 if(cache)return cache;
 const src=loadFullRows(),rows=src.rows;
 const y24=replay(rows,{start:"2024-01-02T06:00:00Z",stop:"2024-12-31T12:00:00Z",initial:100});
 const y25=replay(rows,{start:"2025-01-02T06:00:00Z",stop:"2025-12-31T12:00:00Z",initial:100});
 const args={start:"2026-02-02T06:00:00Z",stop:"2026-09-30T12:00:00Z",initial:119.753917};
 const v8=replay(rows,{...args,includeErrors:true});
 const noRegret=replay(rows,{...args,mode:"no_regret"});
 const frozen=replay(rows,{...args,mode:"frozen",freeze_at:args.start});
 const withoutStress=replay(rows,{...args,mode:"no_shock"});
 const v7=runV7().primary;
 const close=(a,b)=>Math.abs(a-b)<.00002;
 if(!close(v8.final,117.33227601916045)||
    !close(noRegret.final,v8.final)||
    !close(frozen.final,103.64265250593279)||
    !close(y24.final,117.97611257516375)||
    !close(y25.final,145.67462846056316)||
    !close(v7.finalUSD,123.52954535978293))
   throw Error("V8_EXPERIMENT_SHA_OR_REFERENCE_REGRESSION_MISMATCH");
 const considered=v8.errors.filter(e=>e.origin>="2026-02-01"&&e.origin<="2026-10-01"&&e.positionAtOrigin!=="WARMUP");
 const monthly={};for(const q of considered){
  const key=q.origin.slice(0,7);
  if(!monthly[key])monthly[key]={month:key,missedUP:0,missedDOWN:0,avoidedDOWN:0,completedLabels:0,missedUpNetPctSum:0};
  const m=monthly[key];m.completedLabels++;
  if(q.errorType==="MISSED_UP"){m.missedUP++;m.missedUpNetPctSum+=q.opportunityPct;}
  if(q.errorType==="MISSED_DOWN")m.missedDOWN++;
  if(q.errorType==="AVOIDED_DOWN")m.avoidedDOWN++;
 }
 cache={
  version:VERSION,status:"REJECT_PROMOTION_SHADOW_ONLY",
  contract:{firstYear:"2023",trainingFromHistory:"2023-2024",
    yearsEvaluated:[2024,2025,2026],yearsPreviouslyInspected:true,
    macroFirstprintVerified:0,asofMaturedLabels:true,feePerSide:.008,
    bankBidAskIncluded:false,liveTradeAuthorized:false,automaticPromotionAuthorized:false},
  source:src.data,yearScores:[
   {year:2024,initialUSD:100,v8FinalUSD:y24.final,passiveGoldUSD:123.84971030121015,
      nTrades:y24.trades.length,direction96:y24.metric.short,direction336:y24.metric.long},
   {year:2025,initialUSD:100,v8FinalUSD:y25.final,passiveGoldUSD:160.4152649234894,
      nTrades:y25.trades.length,direction96:y25.metric.short,direction336:y25.metric.long},
   {year:"2026-02_to_09",initialUSD:119.753917,v8FinalUSD:v8.final,
      v7FinalUSD:v7.finalUSD,cashUSD:119.753917,nTrades:v8.trades.length,
      direction96:v8.metric.short,direction336:v8.metric.long}
  ],
  controls:{v8OnlineUSD:v8.final,
    v8RegretLearningOffUSD:noRegret.final,
    v8AllLearningFrozenUSD:frozen.final,
    v8StressSellOffUSD:withoutStress.final,
    referenceV7USD:v7.finalUSD,
    regretFeedbackChangedTradeDecision:!close(noRegret.final,v8.final)},
  trades:v8.trades,monthly:Object.entries(v8.months).map(([month,v])=>({month,...v})),
  errorsByMonth:Object.values(monthly).sort((a,b)=>a.month.localeCompare(b.month)),
  sampledLearningEvents:considered.filter(x=>x.errorType==="MISSED_UP"||x.errorType==="MISSED_DOWN").slice(0,12),
  labelsMatured:v8.learning.matureCount,missingDue:v8.learning.missedDue,
  scientificGate:{
   authorized:false,reason:"NET_UNDER_CASH_AND_V7__NO_INCREMENTAL_REGRET_POLICY_GAIN",
   testNotBlind:true,
   moreWork:["Check conditional calibration and label chronology",
     "Distinguish price experts from real source-verified economic event effects",
     "Learn episode-state action policy on non-overlapping prior regimes",
     "Block unresolved economic firstprints from trade inference",
     "Test true bank BID/ASK and future untouched period",
     "No automatic model promotion"]
  }
 };
 return cache;
}
module.exports={VERSION,assess};
