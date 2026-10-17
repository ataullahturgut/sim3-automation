"use strict";
/** Read-only immutable aggregate adapter to actual Jan-2023 selectivity replay.
 * Never turn archived pre-release economic candidates into a trading rule.
 * The underlying replay uses Neon price data only inside GitHub Actions.
 */
const fs=require("node:fs");
const path=require("node:path");
const VERSION="GOLD_JAN2023_SELECTIVE_M1_S1_S2_S3_WALK_V1_20261017";
const dataFile=path.join(__dirname,"data","JAN_2023_SELECTIVE_CADENCE_REAL_CORE_AGGREGATES_20261017.json");
const sourceRun="https://github.com/ataullahturgut/sim3-automation/actions/runs/39058523336";
function read(){
 const v=JSON.parse(fs.readFileSync(dataFile,"utf8"));
 if(v.version!==VERSION||v.sourceWorkflowRun!==sourceRun||
    v.mode!=="CHRONOLOGICAL_ARCHIVE_REPLAY_NOT_REAL_TIME"||
    v.firstPrintMacroVerified!==false||v.goldBankExecution!==false||
    v.tradeAllowed!==false||v.prior.bars!==5865||
    v.observed.janM15!==1920||v.observed.gateCalls!==1920||
    v.observed.modelCalls!==1920||v.observed.actualBankTrades!==0||
    v.observed.acceptedTradeActions!==0||v.observed.macroPITFeaturesAccepted!==0||
    v.observed.retrospectiveMacroQuarantined!==2||
    v.observed.retrospectiveMacroWaves!==2||
    !Array.isArray(v.days)||v.days.length!==31)
  throw Error("SELECTIVE_SOURCE_CONTRACT_FAILED");
 let s=0,events=0,watch=0;
 v.days.forEach((d,i)=>{
  const date="2023-01-"+String(i+1).padStart(2,"0");
  if(d.date!==date||d.economicFeaturesPITAccepted!==0||
     d.ruleEvidence!=="RETROSPECTIVE_RESEARCH_HYPOTHESIS_NOT_MODEL_SIGNAL"||
     (d.snapshot&&
      (d.snapshot.s3.actualAction!==null||d.snapshot.s3.tradeAllowed!==false||
       d.snapshot.s3.researchAction!=="KEEP")))
   throw Error("SELECTIVE_DAY_SCIENTIFIC_CONTRACT_FAILED:"+date);
  s+=d.barCount;events+=d.eventCandidateCount;watch+=d.priceChangeWatchCount;
 });
 // End-of-UTC-month price bars outside the fixed UTC22 research month roll
 // are legitimately absent from the 31 day-labeled screen.
 if(s>v.observed.janM15||s<v.observed.janM15-12||events!==2||
    watch!==v.observed.priceWatch15mEvents)
  throw Error("SELECTIVE_DAILY_TOTAL_MISMATCH");
 return v;
}
module.exports={read,VERSION,sourceRun};
