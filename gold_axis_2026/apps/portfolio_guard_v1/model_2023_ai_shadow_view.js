"use strict";
/** Read only, strictly validated actual 2023 chronology exported from CI. */
const fs=require("node:fs"),path=require("node:path");
const VERSION="GOLD_2023_JAN_FEB_ACTUAL_CORE_WITH_GPT_HANDOFF_V1_20261017";
const SOURCE_RUN="https://github.com/ataullahturgut/sim3-automation/actions/runs/39064426333";
const name="JAN_FEB_2023_AI_SHADOW_CHRONOLOGICAL_20261017.json";
function read(){
 const x=JSON.parse(fs.readFileSync(path.join(__dirname,"data",name),"utf8"));
 const a=x.portfolioAudit;
 if(x.version!==VERSION||x.sourceRun!==SOURCE_RUN||!a||
   x.pretrain?.bars!==5865||x.pretrain.ruleCount!==3||
   x.janFebBars!==3750||x.coreCalls!==3750||x.gateCalls!==3750||
   !Array.isArray(x.dates)||x.dates.length!==59||
   x.aiProviderConnected!==false||x.aiSubmitted!==0||
   a.inputAICount!==0||a.aiUsed!==0||a.aiResultsGrounded!==false||
   a.gptRuntimeConnected!==false||
   a.originalPITEventVerified!==false||a.bankTradeAuthorized!==false||
   a.modelScienceAccepted!==false||a.observations!==3750||
   a.attentionCount!==156||a.quarantinedEconomicEvents!==4||
   a.reference?.buyHoldLiquidatableUSD!==98.26375||
   a.arms?.CORE?.finalLiquidatableUSD!==100||
   a.arms?.AI?.transactions?.length!==0||
   a.arms?.HYBRID?.transactions?.length!==0||
   a.arms?.AI?.finalLiquidatableUSD!==100||
   a.arms?.HYBRID?.finalLiquidatableUSD!==100)
  throw Error("JAN_FEB_AI_RESEARCH_AGGREGATE_INVALID");
 let bars=0,attention=0,releases=0;
 x.dates.forEach((d,i)=>{
  const date=new Date(Date.UTC(2023,0,i+1)).toISOString().slice(0,10);
  if(d.date!==date||!Number.isInteger(d.bars)||d.bars<0||
     !Number.isInteger(d.attention)||d.attention<0||
     !Array.isArray(d.decisions)||d.decisions.length!==0||
     d.core?.s3?.tradeAllowed===true||
     d.core?.s3?.actualAction)
   throw Error("JAN_FEB_AI_DAY_INVALID:"+date);
  bars+=d.bars;attention+=d.attention;releases+=d.observedArchiveMacroWaves;
 });
 // UTC month archive includes 2023-03-01 research roll at Feb28 22Z;
 // only February's final 8 UTC bars are excluded from the labelled table.
 if(bars!==x.janFebBars-8||attention!==a.attentionCount||
   releases!==4)throw Error("JAN_FEB_AI_DAILY_COVERAGE_MISMATCH");
 return x;
}
module.exports={read,VERSION};
