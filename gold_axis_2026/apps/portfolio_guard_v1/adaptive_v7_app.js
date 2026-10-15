"use strict";
/** Read-only adapter for retrospective V7 research. Does not update legacy V1-V6. */
const fs=require("node:fs");
const path=require("node:path");
const crypto=require("node:crypto");
const {parseCSV,replayV6}=require("./adaptive_v7_engine");
const DATA_PATH=path.resolve(__dirname,"..","..","adaptive_volatility_learning",
 "portfolio_protection","verified_3h_asof_features_2025_2026_v0.csv");
const DATA_BLOB_SHA="db9a2777b5daf0bc4dab64157a176f71a30a9df5";
const VERSION="V7_ADAPTIVE_DUAL_HORIZON_RESEARCH_20261015";
function blobHash(buffer){
 return crypto.createHash("sha1").update(Buffer.from("blob "+buffer.length+"\0")).update(buffer).digest("hex");
}
function loadRows(){
 const raw=fs.readFileSync(DATA_PATH);
 const normalized=blobHash(raw)===DATA_BLOB_SHA?raw:Buffer.from(raw.toString("utf8").replace(/\r\n/g,"\n"),"utf8");
 if(blobHash(normalized)!==DATA_BLOB_SHA)throw Error("V7_SOURCE_SHA_MISMATCH_FAIL_CLOSED");
 const rows=parseCSV(normalized.toString("utf8"));
 if(rows.length!==3511||rows[0].tt!=="2025-01-07T00:00:00.000Z"||
   rows.at(-1).tt!=="2026-09-30T21:00:00.000Z")throw Error("V7_BAD_SOURCE_SCOPE");
 return rows;
}
let cached;
function runResearch(){
 if(cached)return cached;
 const rows=loadRows();
 const actual=replayV6(rows);
 const frozen=replayV6(rows,{freeze_learning_at:"2026-01-01T00:00:00Z"});
 const noStress=replayV6(rows,{disable_stress:true});
 const priceOnly=replayV6(rows,{price_only:true});
 const year2025=replayV6(rows,{
   start:"2025-01-07T06:00:00Z",
   stop:"2025-12-31T12:00:00Z",
   initial_usd:100
 });
 const jan2026=replayV6(rows,{
   start:"2026-01-02T06:00:00Z",
   stop:"2026-01-30T12:00:00Z",
   initial_usd:100
 });
 const near=(v,t)=>Math.abs(v-t)<0.00001;
 if(!near(actual.final_usd,123.52954535978293)||
   !near(frozen.final_usd,105.18177145259395)||
   !near(noStress.final_usd,108.44434219692778)||
   !near(priceOnly.final_usd,actual.final_usd)||
   actual.trades.length!==4||actual.training_counts.verifiedEconomicCheckpoints!==0){
   throw Error("V7_EXPECTED_REPLAY_MISMATCH");
 }
 cached={
   version:VERSION,status:"EX_POST_RESEARCH_NOT_BLIND",
   scientificGate:{promote:false,bankTradeAuthorized:false,economicCausalityProven:false,
     warnings:["2026 results inspected before model design",
       "Economic event firstprint verification is missing",
       "Real bank BID/ASK spread and slippage unavailable",
       "V7 differs in price panel and timing from original V4/V5"]},
   source:{checkpoints:3511,blobSHA:DATA_BLOB_SHA,
     path:"gold_axis_2026/adaptive_volatility_learning/portfolio_protection/verified_3h_asof_features_2025_2026_v0.csv"},
   primary:{
      initialUSD:actual.configuration.initial,
      finalUSD:actual.final_usd,
      netReturnPct:actual.net_return_pct,
      passiveGoldUSD:actual.hold_gold_usd,
      cashUSD:actual.cash_usd,
      feesPerSide:actual.configuration.fee_each_leg,
      trades:actual.trades,
      months:Object.entries(actual.per_month).map(([month,v])=>({month,...v})),
      modelMetrics:actual.metrics,
      trainingCounts:actual.training_counts,
      regretDiagnostics:actual.opportunity_regret_diagnostic
   },
   ablations:{
      learningFrozenUSD:frozen.final_usd,
      stressRuleDisabledUSD:noStress.final_usd,
      priceOnlyWithStressUSD:priceOnly.final_usd
   },
   negativeControls:{
      year2025:{initialUSD:100,finalUSD:year2025.final_usd,passiveGoldUSD:year2025.hold_gold_usd},
      january2026:{initialUSD:100,finalUSD:jan2026.final_usd,passiveGoldUSD:jan2026.hold_gold_usd}
   }
 };
 return cached;
}
module.exports={VERSION,DATA_BLOB_SHA,loadRows,runResearch};
