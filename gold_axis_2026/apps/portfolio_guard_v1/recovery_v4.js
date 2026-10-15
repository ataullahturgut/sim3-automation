"use strict";
/**
 * Portfolio Guard V4 — adaptive, cost-aware trend hold vs shock exits.
 * RESEARCH ONLY. 2023-25 history and Jan/Feb26 were already inspected.
 * No blind OOS claim, broker order, or confirmed economic mechanism.
 *
 * Separate pre-existing V1/V3 computations are never mutated.
 */
const v3=require("./recovery_v3"),core=require("./engine"),feb=require("./monthly_runner");
const VERSION="V4_ADAPTIVE_CARRY_GUARD_SHADOW_20261015";
const FEE=.008,DAY=86400000,H96=96*3600000;
const TIME=new Intl.DateTimeFormat("sv-SE",{timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false});
const PARAMETERS=Object.freeze({
 feedCadenceHours:3,bankDecisionHoursTurkey:[9,12,15],
 recoveryConfirmBars:2,trendConfirmBars:2,exitConfirmDecisionBars:2,
 afterSellCooldownHours:24,afterBuyProtectionHours:24,
 recoveryPortfolioTarget:.5,confirmedTrendPortfolioTarget:1,
 shockBuyFractionCut:.5,regularEntryMaxRvP95Factor:1.35,
 drawdownGuardPct:-5,veryFastDropPct:-3.5,
 outcomeEmbargoHours:96
});
function quantile(values,q){
 if(!values.length||q<0||q>1)throw Error("NO_QUANTILE");
 const v=values.slice().sort((a,b)=>a-b),i=(v.length-1)*q,k=Math.floor(i),f=i-k;
 return v[k]*(1-f)+v[Math.min(k+1,v.length-1)]*f;
}
function trainBefore(history,asOf){
 const rows=history.filter(x=>x.time<asOf),cut=asOf-H96;
 if(rows.length<1000)throw Error("TRAIN_SAMPLE_TOO_SMALL");
 const rv=rows.map(x=>x.rv).filter(Number.isFinite);
 const bank=v3.pastOnlyEpisodeBank(rows,asOf);
 if(bank.some(x=>x.knownAt>asOf))throw Error("FUTURE_LABEL_LEAK");
 const rvP75=quantile(rv,.75),rvP95=quantile(rv,.95);
 return {asOfUTC:new Date(asOf).toISOString(),trainingCutUTC:new Date(cut).toISOString(),
  trainingEndUTC:rows.at(-1).tt,trainBars:rows.length,bank,episodeCount:bank.length,
  rvP75,rvP95,calibrationType:"PAST_VOLATILITY_ONLY",
  economicDNA:"G05-C_OR_G06-B_UNRESOLVED",
  riskProbabilityCalibrated:false};
}
function classify(row,prev,previousPhase,training){
 const phase=v3.condition(row,prev,previousPhase);
 const shockThreshold=Math.max(1.6,training.rvP95*1.1);
 const emergency=row.r4<=PARAMETERS.veryFastDropPct&&row.r92<=-3&&row.rv>=shockThreshold;
 const breach=(row.r4<=-1.1&&row.r92<=-1.7&&row.rv>=Math.max(.9,training.rvP75))||
  (row.r4<=-1&&row.r92<=-2.5&&row.ds>=.62);
 const recovery=phase==="RECOVERY_CANDIDATE";
 const trend=phase==="UP_TREND"&&row.rv<=Math.max(1.6,training.rvP95*PARAMETERS.regularEntryMaxRvP95Factor);
 return {phase,emergency,breach,recovery,trend,
  severity:emergency?"EMERGENCY":breach?"DOWNSIDE_PRESSURE":recovery?"RECOVERY":"OTHER",
  marketCause:"UNRESOLVED"};
}
function simulate(rows,training,{initialUSD=100,id="V4"}={}){
 if(!(Number.isFinite(initialUSD)&&initialUSD>0))throw Error("INVALID_CASH");
 let cash=initialUSD,ounces=0,peak=0,prev=null,phase="UNKNOWN",lastClose=null;
 let recoveryStreak=0,trendStreak=0,breachDecisions=0,
  lastBuy=-Infinity,lastSell=-Infinity,lastRiskDecision=-Infinity;
 let observed=0,maxValue=initialUSD,maxDD=0,eligibleCount=0,confirmedRiskExits=0;
 const actions=[],ledger=[];
 for(const r of rows){
  if(!Number.isFinite(r.time)||!Number.isFinite(r.c)||!Number.isFinite(r.p)||r.c<=0||r.p<=0)
   throw Error("INVALID_ASOF_ROW");
  if(prev&&r.time<=prev.time)throw Error("NONMONOTONIC_SOURCE");
  if(prev&&r.time-prev.time>12*3600000){
   recoveryStreak=0;trendStreak=0;breachDecisions=0;prev=null;phase="UNKNOWN";
  }
  const sig=classify(r,prev,phase,training);
  recoveryStreak=sig.recovery?recoveryStreak+1:0;
  trendStreak=sig.trend?trendStreak+1:0;
  phase=sig.phase;observed++;lastClose=r.c;
  if(ounces)peak=Math.max(peak,r.c);
  const eligible=v3.isDecisionTime(r.time);
  let action=ounces?"HOLD_GOLD":"HOLD_CASH",reason="COST_AWARE_NO_ACTION";
  let target=null;
  if(eligible){
   eligibleCount++;
   const gap=r.time-lastRiskDecision;
   breachDecisions=sig.breach ? (gap<=12*3600000?breachDecisions+1:1):0;
   lastRiskDecision=r.time;
   const trailing=ounces&&100*(r.c/peak-1)<=PARAMETERS.drawdownGuardPct&&r.r4<=-.8&&r.r92<=-1.5;
   const noImmediateFlip=(r.time-lastBuy)>=PARAMETERS.afterBuyProtectionHours*3600000;
   const sustainedDown=breachDecisions>=PARAMETERS.exitConfirmDecisionBars&&(r.r276<0||trailing);
   if(ounces&&(sig.emergency||(noImmediateFlip&&sustainedDown))){
    const sold=ounces*r.p*(1-FEE);cash+=sold;ounces=0;peak=0;lastSell=r.time;
    breachDecisions=0;recoveryStreak=0;trendStreak=0;
    action="SELL_TO_CASH";reason=sig.emergency?"EMERGENCY_SHOCK":"MULTI_CONFIRM_DOWN_AFTER_HOLD";
    confirmedRiskExits++;
   }else if(cash>initialUSD*1e-7 &&
     r.time-lastSell>=PARAMETERS.afterSellCooldownHours*3600000){
    const recoveryConfirmed=recoveryStreak>=PARAMETERS.recoveryConfirmBars;
    const trendConfirmed=trendStreak>=PARAMETERS.trendConfirmBars;
    if(recoveryConfirmed||trendConfirmed){
     const nav=cash+ounces*r.p*(1-FEE);
     let riskWeight=1;
     const evidence=v3.neighbors(r,training.bank);
     if(evidence.nMatched>=6&&evidence.caseDownFraction!==null&&evidence.caseDownFraction>=.5)
      riskWeight=PARAMETERS.shockBuyFractionCut;
     const desired=nav*(trendConfirmed?PARAMETERS.confirmedTrendPortfolioTarget:
       PARAMETERS.recoveryPortfolioTarget)*riskWeight;
     const current=ounces*r.p*(1-FEE);
     // Realistic cost-aware target: do not buy negligible position differences.
     const investment=Math.min(cash,Math.max(0,desired-current));
     if(investment>Math.max(.01,nav*.03)){
      cash-=investment;ounces+=investment*(1-FEE)/r.p;
      peak=Math.max(peak,r.c);lastBuy=r.time;
      action="BUY_GOLD";reason=trendConfirmed?"TREND_CONTINUATION_BUY":"RECOVERY_PHASE_HALF_ENTRY";
      target=desired/nav;
     }
    }
   }
  } else reason="OUTSIDE_TR_09_17";
  const nav=cash+ounces*r.c*(1-FEE);
  maxValue=Math.max(maxValue,nav);maxDD=Math.max(maxDD,100*(1-nav/maxValue));
  const rowOut={utc:r.tt,tr:TIME.format(new Date(r.time)),action,reason,phase:sig.phase,
   severity:sig.severity,position:ounces>0?"GOLD":"CASH",price:r.p,
   goldOunces:ounces,cashUSD:cash,nav:Math.round(nav*10000)/10000,
   economicCause:"UNRESOLVED",bankHourEligible:eligible};
  ledger.push(rowOut);
  if(action==="BUY_GOLD"||action==="SELL_TO_CASH")actions.push({...rowOut,shareTarget:target,
   decisionData:{r4:r.r4,r92:r.r92,r276:r.r276,rv:r.rv,ds:r.ds,dd276:r.dd276},
   trainingEndUTC:training.trainingEndUTC,
   fullBankSpreadIncluded:false});
  prev=r;
 }
 if(lastClose===null)throw Error("EMPTY_TRADING_ROWS");
 const finalUSD=cash+ounces*lastClose*(1-FEE);
 return {model:"recoveryV4",version:VERSION,period:id,startUSD:initialUSD,
  finalUSD,returnPct:100*(finalUSD/initialUSD-1),maxDrawdownPct:maxDD,
  cashUSD:cash,goldOunces:ounces,terminalAsset:ounces?"GOLD":"CASH",
  hypotheticalExitFeeDeducted:ounces>0,completePriceBars:observed,
  checks:eligibleCount,bankHoursTurkey:PARAMETERS.bankDecisionHoursTurkey,
  confirmedRiskExits,actions,ledger};
}
function compareAnnual(history){
 const years=[2023,2024,2025];
 return years.map(year=>{
  const t=Date.parse(year+"-01-01T00:00:00Z");
  const training=trainBefore(history,t);
  const current=history.filter(x=>x.tt.startsWith(String(year)));
  const result=simulate(current,training,{initialUSD:100,id:String(year)});
  const passive=100*(1-FEE)/current[0].p*current.at(-1).c*(1-FEE);
  return {year,trainingUntil:training.trainingEndUTC,trainingCount:training.trainBars,
   historicalStressEpisodes:training.episodeCount,coverageWarning:year===2023,
   completeBars:current.length,V4:result.finalUSD,buyHoldUSD:passive,cashUSD:100,
   V4ReturnPct:result.returnPct,maxDrawdownPct:result.maxDrawdownPct,
   trades:result.actions.length,buys:result.actions.filter(x=>x.action==="BUY_GOLD").length,
   sells:result.actions.filter(x=>x.action==="SELL_TO_CASH").length,
   firstDecision:result.actions[0]?{utc:result.actions[0].utc,action:result.actions[0].action,reason:result.actions[0].reason}:null};
 });
}
function runResearch(){
 const hist=v3.loadHistorical(),annual=compareAnnual(hist);
 const train=trainBefore(hist,Date.parse("2026-01-01T00:00:00Z"));
 const januaryRows=core.loadFrozen().rows.filter(r=>new Date(r.time).getUTCMinutes()===0&&new Date(r.time).getUTCHours()%3===0);
 const februaryRows=feb.loadFebruary().rows.filter(r=>new Date(r.time).getUTCMinutes()===0&&new Date(r.time).getUTCHours()%3===0);
 const baseline=core.runAll().scenarios.event15m;
 if(Math.abs(baseline.finalUSD-119.75391720039644)>1e-6||baseline.terminalAsset!=="CASH")
  throw Error("FROZEN_JAN_REFERENCE_CHANGED");
 const january=simulate(januaryRows,train,{id:"JAN2026_100USD_INDEPENDENT",initialUSD:100});
 const february=simulate(februaryRows,train,{id:"FEB2026_FROM_FROZEN_JAN_V1",initialUSD:baseline.finalUSD});
 return {
  version:VERSION,status:"EXPLORATORY_NOT_BLIND_OOS",sourceHashes:v3.HIST,
  training:{asOfUTC:train.asOfUTC,trainBars:train.trainBars,
   episodeCount:train.episodeCount,rvP75:train.rvP75,rvP95:train.rvP95,
   riskProbabilityCalibrated:train.riskProbabilityCalibrated},
  candidatePolicy:PARAMETERS,annual,
  january:{finalUSD:january.finalUSD,startUSD:100,actionCount:january.actions.length,
   terminalAsset:january.terminalAsset,actions:january.actions},
  february:{finalUSD:february.finalUSD,startUSD:baseline.finalUSD,
   terminalAsset:february.terminalAsset,maxDrawdownPct:february.maxDrawdownPct,
   actionCount:february.actions.length,actions:february.actions},
  baseline:{v1JanUSD:baseline.finalUSD,v1FebUSD:feb.runFebruary().scenarios.price15m.finalUSD,
   v3FebUSD:v3.runJanuaryFebruary().february.finalUSD,
   febCashUSD:baseline.finalUSD,
   febBuyHoldFirstMarketRowUSD:baseline.finalUSD*(1-FEE)/feb.loadFebruary().rows[0].p*feb.loadFebruary().rows.at(-1).c*(1-FEE)},
  chronology:"TRAIN_PAST_VOL_PERCENTILES_FROZEN_AT_CALENDAR_ORIGIN",
  economicCauseVerified:false,bankBidAskSpreadIncluded:false,
  warning:"February 2026 was already seen. Any observed gains are retrospective; model is not authorized for bank trading."
 };
}
module.exports={VERSION,PARAMETERS,quantile,trainBefore,classify,simulate,compareAnnual,runResearch};
