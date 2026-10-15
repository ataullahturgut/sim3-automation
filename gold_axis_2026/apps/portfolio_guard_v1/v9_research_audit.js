"use strict";
/** Fail-closed research registry for as-of V9 candidate failures and ablations. */
const {runAudit:naive}=require("./v9_state_transition");
const {audit:episodes}=require("./v9_episode_guard");
const {audit:selector}=require("./v9_shadow_selector");
const {runResearch:v7Report}=require("./adaptive_v7_app");
const {assess:v8Report}=require("./v8_regret_audit");
const VERSION="V9_STATE_REGRET_SCIENTIFIC_AUDIT_20261015";
let memo;
function report(){
 if(memo)return memo;
 const n=naive(),e=episodes(),m=selector(),v7=v7Report().primary,v8=v8Report();
 const snap=(arr,name,year)=>arr.find(x=>x.variant===name&&x.year===year);
 const score=(arr,name,year)=>arr.find(x=>x.name===name&&x.year===year);
 const close=(a,b)=>Number.isFinite(a)&&Math.abs(a-b)<.00008;
 if(!close(snap(e.results,"BASE","2024").final,125.12907032005278)||
    !close(snap(e.results,"SLOW_EXIT","2025").final,148.03111496963868)||
    !close(snap(e.results,"POSTERIOR","2026").final,119.753917)||
    !(score(m.results,"VOTE_42D","2026").final>114.70&&score(m.results,"VOTE_42D","2026").final<114.72)||
    !close(v7.finalUSD,123.52954535978293)||
    !close(v8.controls.v8OnlineUSD,117.33227601916045))
   throw Error("V9_SHADOW_REFERENCE_CHANGED_ABORT");
 const passives={"2024":123.84971030121015,"2025":160.4152649234894};
 const candidates=[
  ...e.results.map(x=>({...x,family:"EPISODE"})),
  ...m.results.map(x=>({...x,variant:x.name,family:"ONLINE_SHADOW_META"})),
  ...n.trials.map(x=>({...x,variant:x.mode,family:"NAIVE_COSTED_POLICY_MIXTURE",
    final:x.final,trades:x.trades}))
 ];
 const years=["2024","2025"];
 const passing=candidates.filter(x=>x.year==="2024"&&years.every(y=>{
    const same=candidates.find(q=>q.family===x.family&&q.variant===x.variant&&q.year===y);
    return same&&same.final>passives[y];
 }));
 const candidates2026=candidates.filter(x=>x.year==="2026"||x.year==="2026_FebSep");
 const best2026=candidates2026.reduce((a,b)=>!a||b.final>a.final?b:a,null);
 const c2026=119.753917;
 const rows=[
  {model:"2024 episode BASE",cashUSD:100,finalUSD:snap(e.results,"BASE","2024").final,
    passiveGoldUSD:passives["2024"]},
  {model:"2025 episode SLOW_EXIT",cashUSD:100,finalUSD:snap(e.results,"SLOW_EXIT","2025").final,
    passiveGoldUSD:passives["2025"]},
  {model:"2026 no-overlap-label posterior",cashUSD:c2026,
    finalUSD:snap(e.results,"POSTERIOR","2026").final,tradeCount:0},
  {model:"2026 V9 42-checkpoint online selector",cashUSD:c2026,
    finalUSD:score(m.results,"VOTE_42D","2026").final},
  {model:"2026 previous V8 regret",cashUSD:c2026,
    finalUSD:v8.controls.v8OnlineUSD},
  {model:"2026 previous V7",cashUSD:c2026,finalUSD:v7.finalUSD},
 ];
 if(passing.length>0)throw Error("V9_GATE_POLICY_REVIEW_REQUIRED");
 memo={
  version:VERSION,status:"REJECT_V9_PROMOTION_SAVE_LEARNING_EXPERIMENTS",
  coverage:{historyStart:"2023-01-03",end:"2026-09-30",
    sourceRows:e.source.total,verified2025Overlap:e.source.overlapVerified},
  execution:{
    bankHoursTR:[9,12,15],nextCheckpointFill:true,
    sameCheckpointSignalFill:false,feePerSide:.008,
    bankBidAsk:false,bankQuoteProvenance:false
  },
  method:{
    onlineRealizedNetExpertRanking:true,
    cashExpertAbstention:true,
    regimeHysteresis:true,
    multiWeekNonOverlapping336hTrainingLabels:true,
    isolatedErrorsTracked:true,
    futureMonthOracleUsedAsSignal:false,
    prospectiveBlindPeriod:false,
    reviewed2026DuringDevelopment:true,
    economicFirstprintsVerified:0
  },
  tables:rows,
  naiveMixture:n.trials.map(t=>({year:t.year,policy:t.mode,finalUSD:t.final,trades:t.trades})),
  episodeCandidates:e.results,
  shadowCandidates:m.results.map(x=>({variant:x.name,year:x.year,initial:x.initial,final:x.final,trades:x.trades})),
  best2026RetrospectiveAmongTried:{
    family:best2026.family,variant:best2026.variant,finalUSD:best2026.final,
    WARNING:"SELECTION_AFTER_SEEING_2026_NOT_A_MODEL"
  },
  pre2026PassBothPassive:{
    count:passing.length,policyKeys:passing.map(x=>x.family+":"+x.variant)
  },
  comparisons:{V7_2026:v7.finalUSD,V8_2026:v8.controls.v8OnlineUSD,
    cash_2026:c2026},
  gate:{
    promote:false,reason:"NO_V9_POLICY_BEATS_2024_AND_2025_PASSIVE_BUY_HOLD_BOTH;_2026_NONE_BEATS_V7",
    modelChosenBy2026Results:false,
    canTradeLive:false
  },
  researchObservations:[
   "Instant policy switching overtrades at 1.6% roundtrip; avoid ex-post short-horizon oracle-as-target.",
   "A state hysteresis policy can beat buy-hold in 2024 but failed 2025 and 2026.",
   "Retrospective best policy selection on 2026 is data snooping, not an executable decision.",
   "Shadow experts update weights from past costed NAV; failed to robustly adapt at 2026 regime change.",
   "Non-overlapping fourteen-day labels trade sample size for less pseudoreplication, but were too sparse.",
   "Live spread, economic firstprint and untouched independent period still missing."
  ],
  versionProtected:["V1","V2","V3","V4","V5","V6","V7","V8"],
  liveInstructions:false
 };
 return memo;
}
module.exports={VERSION,report};
