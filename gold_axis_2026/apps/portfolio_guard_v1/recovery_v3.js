"use strict";
/**
 * GOLD GUARD V3 | Exploratory regime model.
 * Only completed, origin-safe bars drive decisions. Calendar time and
 * position state are first-class; events do not establish economic causality.
 *
 * IMPORTANT: Feb 2026 was seen before V3 design. This code cannot be
 * represented as a blinded Feb test nor as investment advice.
 */
const fs=require("node:fs"),path=require("node:path");
const core=require("./engine"),feb=require("./monthly_runner");
const ROOT=path.resolve(__dirname,"../../..");
const HIST=Object.freeze([
 {path:"gold_axis_2026/apps/portfolio_guard_v1/data/RECOVERY_HIST_3H_2020_2022_V1.csv",blob:"e19d69fbbf4a825420a07d7e5f678899d1e0f805"},
 {path:"gold_axis_2026/apps/portfolio_guard_v1/data/RECOVERY_HIST_3H_2023_2025_V1.csv",blob:"a588b6745f893fcafc935fa486328a6349caa658"}
]);
const VERSION="RECOVERY_HOLD_V3_FINITE_STATE_SHADOW_20261015",FEE=.008,H96=96*3600000,H24=24*3600000;
const T=new Intl.DateTimeFormat("sv-SE",{timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false});
const REQUIRED=["p","c","r4","r92","r276","dd276","v92","rv","ds","eff","loc","dd4"];
const POLICY=Object.freeze({
 decisionHoursTurkey:[9,12,15], // no bank order after 17:00 local
 confirmObservations:2,episodeEmbargoHours:96,
 buyCandidateShare:.5,highRiskShare:.25,
 minAfterSaleHours:24,
 feePerSide:FEE,
 maxCrossWindowHours:96,
 maxJoinDistance:1.5,
 minAnalogCasesForSizeReduction:6,
 highDownFraction:.5
});
function loadHistorical(){
 const a=HIST.flatMap(spec=>core.decodePinnedSource(spec,fs.readFileSync(path.join(ROOT,spec.path))).rows);
 const rows=a.map(r=>{
  const v={tt:r.tt,time:Date.parse(r.tt)};
  for(const k of REQUIRED)v[k]=r[k]===""?null:Number(r[k]);
  if(!Number.isFinite(v.time)||REQUIRED.some(k=>!Number.isFinite(v[k])))throw Error("HIST_BAD_FEATURE");
  return v;
 });
 if(rows.length!==10850)throw Error("HIST_COUNT_CHANGED");
 for(let i=1;i<rows.length;i++)if(rows[i].time<=rows[i-1].time)throw Error("HIST_TIME_NONMONOTONIC");
 return rows;
}
function condition(row,prior,prevPhase){
 if(!row||REQUIRED.some(k=>!Number.isFinite(row[k])))return "UNKNOWN";
 if(row.r4<=-2.5&&row.rv>=1.6)return "CAPITULATION_CANDIDATE";
 if(row.r4<=-1.2&&(row.rv>=.9||row.ds>=.68))return "FALLING_FAST";
 if((prevPhase==="RECOVERY_CANDIDATE"||prevPhase==="UP_TREND")&&row.r4<-1.1&&row.r92<0)return "FAILED_REBOUND";
 if(row.r276<-2&&row.r92>=.5&&row.r4>.2&&row.ds<.72&&row.loc>.4)return "RECOVERY_CANDIDATE";
 if(row.r92>=1&&row.r276>=0&&row.dd276>-3&&row.rv<1.6)return "UP_TREND";
 if(row.r276<-2&&row.r92>=-1&&row.r4>-.3&&row.rv<1.8)return "STABILIZING";
 if(prior&&row.r4>0&&row.r92>0&&row.rv<prior.rv&&row.ds<.6&&row.dd276<-2)return "STABILIZING";
 return "UNKNOWN";
}
function pastOnlyEpisodeBank(hist,asof){
 // An episode is an initial falling/capitulation mark, separated by 96h;
 // its future extrema are NEVER predictors. Use only mature histories.
 const events=[];let last=-Infinity,prev=null,phase="UNKNOWN";
 for(let i=0;i<hist.length;i++){
  const r=hist[i];if(r.time+H96>asof)break;
  if(prev&&r.time-prev.time>12*3600000){prev=null;phase="UNKNOWN";}
  const newPhase=condition(r,prev,phase);
  if(["FALLING_FAST","CAPITULATION_CANDIDATE"].includes(newPhase)&&r.time-last>=H96){
   const forward=[];
   for(let j=i+1;j<hist.length&&hist[j].time<=r.time+H96;j++)forward.push(hist[j].c);
   if(forward.length>=6){
    events.push({id:"EP_"+r.tt,asof:r.tt,time:r.time,
     features:{r4:r.r4,r92:r.r92,r276:r.r276,rv:r.rv,ds:r.ds,dd276:r.dd276},
     low96:100*(Math.min(...forward)/r.c-1),
     high96:100*(Math.max(...forward)/r.c-1),
     chartPhase:newPhase,
     causalMechanism:"UNRESOLVED",possibleDNA:["G05-C","G06-B"],
     knownAt:r.time+H96});
    last=r.time;
   }
  }
  prev=r;phase=newPhase;
 }
 return events;
}
function neighbors(row,bank){
 // Risk fraction is selective shock-episode proportion, NOT a probability.
 const features=["r4","r92","r276","rv","ds","dd276"],scales=[2,5,9,1,.5,7];
 const n=bank.map(e=>{
  let d=0;
  for(let k=0;k<features.length;k++)d+=((row[features[k]]-e.features[features[k]])/scales[k])**2;
  return {caseId:e.id,d:Math.sqrt(d/features.length),low96:e.low96};
 }).sort((a,b)=>a.d-b.d).slice(0,9);
 const matched=n.filter(x=>x.d<=POLICY.maxJoinDistance);
 return {nMatched:matched.length,nearest:n.slice(0,3),caseDownFraction:
    matched.length?matched.filter(x=>x.low96<=-3).length/matched.length:null,
   calibrated:false,selectionBias:"STRESS_EPISODES_ONLY",causalMechanism:"UNRESOLVED"};
}
function isDecisionTime(ms){
 const date=T.format(new Date(ms)),hour=Number(date.slice(11,13));
 return POLICY.decisionHoursTurkey.includes(hour);
}
function execute(rows,{startUSD=100,bank=[],id="sample",endUTC=null}={}){
 if(!Number.isFinite(startUSD)||startUSD<=0)throw Error("INVALID_CASH");
 let cash=startUSD,ounces=0,peak=null,lastSale=-Infinity,prev=null,phase="UNKNOWN";
 let streak=0,prevStreakPhase=null,lastClose=null,highNAV=startUSD,dd=0;
 const trades=[],ledger=[];let observationCount=0;
 for(const r of rows){
  if(endUTC&&r.time>=endUTC)break;
  const stale=prev&&r.time-prev.time>12*3600000;
  if(stale){prev=null;phase="UNKNOWN";streak=0;prevStreakPhase=null;}
  if(!Number.isFinite(r.p)||!Number.isFinite(r.c))throw Error("NO_PRICE");
  const freshPhase=condition(r,prev,phase);
  streak=freshPhase===prevStreakPhase?streak+1:1;prevStreakPhase=freshPhase;
  phase=freshPhase;lastClose=r.c;observationCount++;
  if(ounces)peak=Math.max(peak??r.c,r.c);
  const eligible=isDecisionTime(r.time);
  const a=neighbors(r,bank);
  const lowEvidence=a.nMatched>=POLICY.minAnalogCasesForSizeReduction&&
    a.caseDownFraction>=POLICY.highDownFraction;
  const isConfirmed=streak>=POLICY.confirmObservations;
  let action=ounces?"HOLD_GOLD":"HOLD_CASH",reason="NO_POSITION_SWITCH",share=0;
  if(eligible){
   const emergency=(r.r4<=-2.5&&r.rv>=1.6&&r.r92<=-3);
   const sustainedBreak=(r.r4<=-1.2&&r.r92<=-2&&r.rv>=.9);
   const trailingBreak=ounces>0&&peak!==null&&100*(r.c/peak-1)<=-4&&r.r4<-.9;
   if(ounces>0&&(emergency||sustainedBreak||trailingBreak)){
    cash+=ounces*r.p*(1-FEE);
    ounces=0;peak=null;lastSale=r.time;streak=0;prevStreakPhase=null;
    action="SELL_TO_CASH";reason=emergency?"EMERGENCY_FALLING_FAST":sustainedBreak?"SUSTAINED_DOWN_CONFIRMED":"DRAWDOWN_AND_PRICE_WEAKNESS";
   }else if(cash>1e-8&&r.time-lastSale>=POLICY.minAfterSaleHours*3600000){
    const confirmRecovery=freshPhase==="RECOVERY_CANDIDATE"&&isConfirmed;
    const confirmTrend=freshPhase==="UP_TREND"&&isConfirmed;
    if(confirmRecovery||confirmTrend){
     // Step into risk; severe shocks receive a smaller exposure.
     share=confirmTrend?1:lowEvidence?POLICY.highRiskShare:POLICY.buyCandidateShare;
     const allocated=cash*share;
     ounces+=allocated*(1-FEE)/r.p;cash-=allocated;
     peak=Math.max(peak??r.c,r.c);
     action="BUY_GOLD";reason=confirmTrend?"CONTINUED_TREND_CONFIRMED":"RECOVERY_TWO_OBSERVATIONS";
     streak=0;prevStreakPhase=null;
    }
   }
  }else reason="NO_BANK_TRANSACTION_OUTSIDE_09_17";
  if(action==="BUY_GOLD"||action==="SELL_TO_CASH"){
   trades.push({tr:T.format(new Date(r.time)),utc:r.tt,action,price:r.p,reason,phase:freshPhase,
    cashAfter:cash,goldAfter:ounces,share,caseEvidence:a,causality:"UNRESOLVED"});
  }
  const nav=cash+ounces*r.c*(1-FEE);
  highNAV=Math.max(nav,highNAV);dd=Math.max(dd,100*(1-nav/highNAV));
  ledger.push({utc:r.tt,turkey:T.format(new Date(r.time)),hasNewBar:true,action,reason,
    phase:freshPhase,position:ounces>0?"GOLD":"CASH",
    goldOunces:ounces,cashUSD:cash,nav:Math.round(nav*10000)/10000,
    knownCaseMatches:a.nMatched,calibrated:false,
    causalMechanism:"UNRESOLVED",decisionClockAllowed:eligible});
  prev=r;
 }
 if(lastClose===null)throw Error("NO_DATA");
 const finalUSD=cash+ounces*lastClose*(1-FEE);
 return {id,model:"recoveryV3",version:VERSION,startUSD,finalUSD,
  returnPct:100*(finalUSD/startUSD-1),maxDrawdownPct:dd,
  terminalAsset:ounces?"GOLD":"CASH",goldOunces:ounces,cashUSD:cash,
  hypotheticalExitFeeDeducted:ounces>0,
  completePriceBars:observationCount,actions:trades,ledger,
  decisionHoursTurkey:POLICY.decisionHoursTurkey,
  economicCausalityProven:false,independentOutOfSample:false};
}
function annualWalk(){
 const hist=loadHistorical();const byYear=[];
 for(const year of [2023,2024,2025]){
  const cutoff=Date.parse(year+"-01-01T00:00:00Z");
  const bank=pastOnlyEpisodeBank(hist.filter(x=>x.time<cutoff),cutoff);
  const rows=hist.filter(x=>x.tt.slice(0,4)===String(year));
  const v=execute(rows,{startUSD:100,bank,id:"BACKTEST_"+year});
  const first=rows[0].p,last=rows.at(-1).c;
  const hold=100*(1-FEE)/first*last*(1-FEE);
  byYear.push({year,trainThrough:year-1,bankEpisodes:bank.length,
   rows:rows.length,startUSD:100,finalUSD:v.finalUSD,cashOnlyUSD:100,
   buyHoldUSD:hold,returnPct:v.returnPct,
   maxDrawdownPct:v.maxDrawdownPct,actions:v.actions.length,
   buyCount:v.actions.filter(x=>x.action==="BUY_GOLD").length,
   sellCount:v.actions.filter(x=>x.action==="SELL_TO_CASH").length,
   firstAction:v.actions[0]||null,fullTemporalCoverage:false});
 }
 return byYear;
}
function runJanuaryFebruary(){
 const hist=loadHistorical(),bank=pastOnlyEpisodeBank(hist,Date.parse("2026-01-01T00:00:00Z"));
 const jan=core.loadFrozen().rows.filter(r=>new Date(r.time).getUTCMinutes()===0&&new Date(r.time).getUTCHours()%3===0);
 const january=execute(jan,{startUSD:100,bank,id:"JAN2026_V3_EXPLORATORY"});
 const original=core.runAll().scenarios.event15m;
 if(Math.abs(original.finalUSD-119.75391720039644)>1e-6)throw Error("REFERENCE_MODIFIED");
 const fe=feb.loadFebruary().rows.filter(r=>new Date(r.time).getUTCMinutes()===0&&new Date(r.time).getUTCHours()%3===0);
 const february=execute(fe,{startUSD:original.finalUSD,bank,id:"FEB2026_V3_SHADOW_FROM_V1_CASH"});
 const annual=annualWalk();
 return {version:VERSION,policy:POLICY,status:"EXPLORATORY_RETROSPECTIVE_NOT_OOS",
  sourceHashes:HIST,
  history:{totalRows:hist.length,trainEpisodesMatureBeforeJan:bank.length,byYear:hist.reduce((a,r)=>(a[r.tt.slice(0,4)]=(a[r.tt.slice(0,4)]||0)+1,a),{})},
  sourcePriceHistory2023Incomplete:true,annual,
  january:{
   ...january,days:groupDays(january.ledger,"2026-01",31,100),ledger:undefined,
   archiveCases:bank.length,fullCalendarSlots:2976,checks:jan.length,
   benchmarkBuyHoldUSD:core.runAll().scenarios.event15m.benchmarkBuyHoldUSD,
   period:"Ocak 2026"
  },
  february:{
   ...february,days:groupDays(february.ledger,"2026-02",28,original.finalUSD),ledger:undefined,
   archiveCases:bank.length,fullCalendarSlots:2688,checks:fe.length,
   benchmarkBuyHoldUSD:original.finalUSD*(1-FEE)/feb.loadFebruary().rows[0].p*feb.loadFebruary().rows.at(-1).c*(1-FEE),
   benchmarkNote:"Şubat ilk tam barda AL ve ay sonu teorik SAT",
   period:"Şubat 2026"
  },
  frozenOriginalJanuaryCashUSD:original.finalUSD,
  hardStop:"V3 does not replace live trading decisions; comparisons are exploratory only.",
  scientificLearning:"G05-C/G06-B both candidate economic mechanisms, firstprint/causal evidence not verified."
 };
}
function groupDays(ledger,month,n,openingValue){
 const groups=[];
 for(let d=1;d<=n;d++){
  const date=month+"-"+String(d).padStart(2,"0");
  const day=ledger.filter(x=>x.turkey.startsWith(date));
  groups.push({date,netValue:day.length?day.at(-1).nav:null,position:day.length?day.at(-1).position:null,
   completeBars:day.length,
   actions:day.filter(x=>x.action==="BUY_GOLD"||x.action==="SELL_TO_CASH")
    .map(x=>({when:x.turkey.slice(11),action:x.action})),macroWindows:[]});
 }
 // Last observed level carries through market-closed days.
 let last=openingValue,position="CASH";
 for(const g of groups){if(g.netValue===null){g.netValue=last;g.position=position;}else{last=g.netValue;position=g.position;}}
 return groups;
}
module.exports={VERSION,HIST,POLICY,loadHistorical,condition,pastOnlyEpisodeBank,neighbors,isDecisionTime,execute,annualWalk,runJanuaryFebruary};
