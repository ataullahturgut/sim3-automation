"use strict";
/**
 * V5: slow trend + cost-aware hysteresis guard on V4 phase recognition.
 * Pre-registered AFTER seeing 2026: retrospective exploratory only.
 * Strictly ordered, no end-of-period outcome in a decision.
 */
const fs=require("node:fs"),path=require("node:path");
const core=require("./engine"),feb=require("./monthly_runner");
const v3=require("./recovery_v3"),v4=require("./recovery_v4"),review=require("./v4_forward_review");
const selection=require("./scientific_promotion_gate");
const VERSION="V6_CROSS_ASSET_PORTFOLIO_SHADOW_20261015";
const FEE=.008,DAY=86400000;
const P=Object.freeze({
 fastEMAObservations:40,slowEMAObservations:120,slowWindowMaxDays:38,
 buyConfirmation:2,exitBankConfirmations:2,
 trendBelowSlowPct:1.5,entryPeakDrawdownPct:7.5,
 afterBuyHours:24,afterSellHours:24,
 halfEntryTarget:.5,fullTrendEntryTarget:1,
 minimumRebalanceNavFraction:.03,
 bankHoursTurkey:[9,12,15]
});
const TIME=new Intl.DateTimeFormat("sv-SE",{timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false});
const annualKeys=["2023","2024","2025"];

const PINS=Object.freeze([
 {path:"gold_axis_2026/apps/portfolio_guard_v1/data/CME_3H_ASOF_2023_2024_V6.csv",blob:"e8787df9823b412e31546c784f1e95a762126697"},
 {path:"gold_axis_2026/apps/portfolio_guard_v1/data/CME_3H_ASOF_2025_2026_V6.csv",blob:"2a2b42d0140fac3aea197013c443cd268db92b6d"}
]);
const EVENT_PANEL=Object.freeze({
 path:"gold_axis_2026/OLAY_02_96_TUM_VAKA_EVRENSEL_ORUNTU_MATRIKS_20261015.csv",
 blob:"4b6c8fd84ea291ae22ddc9b0d5d545ce2d8fa527"
});
function loadMacro(){
 const root=path.resolve(__dirname,"../../.."),data=new Map(),byYear={};
 for(const spec of PINS){
  const decoded=core.decodePinnedSource(spec,fs.readFileSync(path.join(root,spec.path))).rows;
  for(const row of decoded){
   if(data.has(row.tt))throw Error("DUPLICATE_CME_HOUR");
   const value={tt:row.tt,time:Date.parse(row.tt)};
   for(const k of ["nq6","nq24","zn6","zn24","si6","si24"])
    value[k]=row[k]===""?null:Number(row[k]);
   if(!Number.isFinite(value.time)||["nq6","nq24","zn6","zn24","si6","si24"].
      some(k=>value[k]!==null&&!Number.isFinite(value[k])))throw Error("INVALID_CME_VALUE");
   data.set(value.tt,value);
   const yy=value.tt.slice(0,4);byYear[yy]??={all:0,bothSixHour:0,silver:0};
   byYear[yy].all++;
   if(value.nq6!==null&&value.zn6!==null)byYear[yy].bothSixHour++;
   if(value.si6!==null)byYear[yy].silver++;
  }
 }
 if(data.size!==7682)throw Error("CME_COUNT_CHANGED");
 return {data,byYear};
}
function economicEvidence(){
 const input=core.decodePinnedSource(EVENT_PANEL,fs.readFileSync(
  path.join(path.resolve(__dirname,"../../.."),EVENT_PANEL.path))).rows;
 if(input.length!==96)throw Error("EVENT_CASES_CHANGED");
 const first=input.filter(x=>x.onset_firstprint_verified==="YES").length;
 const proven=input.filter(x=>x.mechanism_caused_proven==="YES").length;
 if(first!==0||proven!==0)throw Error("EVENT_EVIDENCE_STATUS_CHANGED_REVIEW");
 return {cases:input.length,verifiedFirstprints:first,provenMechanisms:proven,
  allowedAsCausalTradingInputs:false,source:EVENT_PANEL};
}
function regime(x){
 const unknown={state:"NO_CONSENSUS_OR_STALE",hasBoth:false,silver:"UNAVAILABLE",
  economicMechanism:"UNRESOLVED"};
 if(!x||x.nq6===null||x.zn6===null)return unknown;
 const n=x.nq6,z=x.zn6;
 const state=n<=-.8&&z<=-.08?"EQUITY_BOND_SELL_OFF":
  n<=-.8&&z>=.08?"SAFE_HAVEN_ROTATION":
  n>=.3&&z<=-.08?"YIELD_HEADWIND":
  n>=.6&&z>=0?"CROSS_RISK_ON":"NO_CONSENSUS_OR_STALE";
 return {state,hasBoth:true,silver:x.si6===null?"UNAVAILABLE":
   x.si6<=-.5&&n<=-.8?"METALS_LIQUIDATION_COEXISTS":"NO_SECONDARY_CONFIRMATION",
  NQ6:n,ZN6:z,SI6:x.si6,economicMechanism:"UNRESOLVED"};
}

function warmup(history,start){
 return history.filter(r=>r.time<start).slice(-P.slowEMAObservations);
}
function updateEma(prev,p,n){
 return prev===null?p:(p*2/(n+1)+prev*(1-2/(n+1)));
}
function run(rows,training,{initialUSD=100,id="V6",priorHistory=[],macroByTime=new Map()}={}){
 if(!Number.isFinite(initialUSD)||initialUSD<=0)throw Error("INVALID_INITIAL_USD");
 if(!rows.length)throw Error("EMPTY_SERIES");
 if(rows.some((r,i)=>!Number.isFinite(r.time)||!Number.isFinite(r.c)||r.c<=0||!Number.isFinite(r.p)||r.p<=0||
   (i&&r.time<=rows[i-1].time)))throw Error("INVALID_ASOF_INPUT");
 if(priorHistory.some(r=>r.time>=rows[0].time))throw Error("WARMUP_FUTURE_DATA");
 let fast=null,slow=null,seen=0,history=[],prev=null,phase="UNKNOWN";
 for(const r of priorHistory){
  fast=updateEma(fast,r.c,P.fastEMAObservations);
  slow=updateEma(slow,r.c,P.slowEMAObservations);
  history.push(r.time);if(history.length>P.slowEMAObservations)history.shift();
  seen++;
 }
 let cash=initialUSD,ounces=0,peak=0,lastBuy=-Infinity,lastSell=-Infinity;
 let recoveryStreak=0,trendStreak=0,riskConfirm=0,lastRiskDecision=-Infinity;
 let highNAV=initialUSD,maxDD=0;
 const actions=[],ledger=[];
 for(const r of rows){
  if(prev&&r.time-prev.time>12*3600000){phase="UNKNOWN";prev=null;recoveryStreak=0;trendStreak=0;riskConfirm=0;}
  fast=updateEma(fast,r.c,P.fastEMAObservations);
  slow=updateEma(slow,r.c,P.slowEMAObservations);
  history.push(r.time);if(history.length>P.slowEMAObservations)history.shift();
  seen++;
  const slowValid=history.length>=P.slowEMAObservations &&
   r.time-history[0]<=P.slowWindowMaxDays*DAY;
  const signal=v4.classify(r,prev,phase,training);
  recoveryStreak=signal.recovery?recoveryStreak+1:0;
  trendStreak=signal.trend?trendStreak+1:0;
  phase=signal.phase;
  if(ounces)peak=Math.max(peak,r.c);
  const macro=regime(macroByTime.get(r.tt));
  const marketOK=v3.isDecisionTime(r.time);
  let action=ounces?"HOLD_GOLD":"HOLD_CASH",reason="NO_ACTION",
   target=null,riskSlow=false,drawdownBreach=false;
  if(marketOK){
   const slowBear=slowValid &&r.c<slow*(1-P.trendBelowSlowPct/100)&&fast<slow&&r.r276< -1;
   const peakDD=ounces>0&&peak>0?100*(r.c/peak-1):0;
   const drawdown=ounces>0&&peakDD<=-P.entryPeakDrawdownPct &&r.c<fast&&r.r276<0;
   riskSlow=slowBear;drawdownBreach=drawdown;
   riskConfirm=(slowBear||drawdown)?
    (r.time-lastRiskDecision<=27*3600000?riskConfirm+1:1):0;
   lastRiskDecision=r.time;
   const stressConfirmed=macro.state==="EQUITY_BOND_SELL_OFF"&&r.r92<-1&&r.r276<-1&&
     ((slowValid&&fast<slow)||peakDD<=-5);
   const delayOrdinarySell=macro.state==="SAFE_HAVEN_ROTATION"&&r.r4>0&&r.r92>0&&!signal.emergency;
   const stop=(signal.emergency||stressConfirmed||
     riskConfirm>=P.exitBankConfirmations&&r.time-lastBuy>=P.afterBuyHours*3600000)&&
     !delayOrdinarySell;
   if(ounces>0&&stop){
    cash+=ounces*r.p*(1-FEE);ounces=0;peak=0;lastSell=r.time;
    action="SELL_TO_CASH";
    reason=signal.emergency?"EMERGENCY_CRASH":stressConfirmed?"GOLD_DOWN_WITH_EQUITY_BOND_STRESS":
      slowBear?"SLOW_BEAR_TREND_CONFIRMED":"PORTFOLIO_DRAWDOWN_CONFIRMED";
    riskConfirm=0;recoveryStreak=0;trendStreak=0;
   }else if(cash>initialUSD*1e-7&&r.time-lastSell>=P.afterSellHours*3600000){
    const comeback=recoveryStreak>=P.buyConfirmation;
    const trend=trendStreak>=P.buyConfirmation;
    const block=macro.state==="EQUITY_BOND_SELL_OFF"&&r.r92<0;
    if((comeback||trend)&&!signal.emergency&&!(slowValid&&slowBear)&&!block){
     // Strong uptrend must be confirmed by both the price phase and slow trend.
     const full=trend&&slowValid&&fast>=slow&&r.c>=slow&&r.r276>=0;
     // While below the slow trend, allow at most a half-sized exploratory
     // recovery entry. No repeated buy to reach 100% on noisy rebounds.
     const desiredWeight=(full?P.fullTrendEntryTarget:P.halfEntryTarget)*
      (macro.state==="YIELD_HEADWIND"&&r.r276<0?.5:1);
     const wealth=cash+ounces*r.p*(1-FEE);
     const current=ounces*r.p*(1-FEE);
     const allocation=Math.min(cash,Math.max(0,wealth*desiredWeight-current));
     if(allocation>Math.max(.01,wealth*P.minimumRebalanceNavFraction)){
      cash-=allocation;ounces+=allocation*(1-FEE)/r.p;
      peak=Math.max(peak,r.c);lastBuy=r.time;
      action="BUY_GOLD";reason=full?"SLOW_TREND_AND_PRICE_CONFIRMED":"TENTATIVE_RECOVERY_HALF";
      target=desiredWeight;
     }
    }
   }
  }else reason="NON_BANK_HOUR";
  const nav=cash+ounces*r.c*(1-FEE);
  highNAV=Math.max(highNAV,nav);maxDD=Math.max(maxDD,100*(1-nav/highNAV));
  const row={utc:r.tt,tr:TIME.format(new Date(r.time)),position:ounces?"GOLD":"CASH",
   action,reason,phase:signal.phase,marketHourEligible:marketOK,netUSD:Math.round(nav*1e4)/1e4,
   cashUSD:cash,goldOunces:ounces,
   asof:{r4:r.r4,r92:r.r92,r276:r.r276,rv:r.rv,dd276:r.dd276},
   slow:{ema40:fast,ema120:slow,valid:slowValid,bear:riskSlow,drawdownBreach},
   macro,causalMechanism:"UNRESOLVED"};
  ledger.push(row);
  if(action==="SELL_TO_CASH"||action==="BUY_GOLD")actions.push({...row,price:r.p,targetAllocation:target});
  prev=r;
 }
 const lastPrice=rows.at(-1).c;
 return {model:"macroEvidenceV6",version:VERSION,id,startUSD:initialUSD,
  finalUSD:cash+ounces*lastPrice*(1-FEE),
  maxDrawdownPct:maxDD,cashUSD:cash,goldOunces:ounces,
  terminalAsset:ounces?"GOLD":"CASH",actions,ledger,
  hypotheticalExitFeeDeducted:ounces>0};
}
function fullResearch(){
 const macroSource=loadMacro(),audit=economicEvidence();
 const hist=v3.loadHistorical(),yearly=[];
 for(const year of annualKeys){
  const d=Date.parse(year+"-01-01T00:00:00Z");
  const train=v4.trainBefore(hist,d);
  const rows=hist.filter(r=>r.tt.startsWith(year));
  const prior=warmup(hist,rows[0].time);
  const sim=run(rows,train,{initialUSD:100,id:year,priorHistory:prior,macroByTime:macroSource.data});
  const passive=100*(1-FEE)/rows[0].p*rows.at(-1).c*(1-FEE);
  yearly.push({year:Number(year),trainingEndUTC:train.trainingEndUTC,
   controls:rows.length,coverageWarning:year==="2023",
   finalUSD:sim.finalUSD,cashOnlyUSD:100,buyHoldUSD:passive,
   maxDrawdownPct:sim.maxDrawdownPct,buys:sim.actions.filter(x=>x.action==="BUY_GOLD").length,
   sells:sim.actions.filter(x=>x.action==="SELL_TO_CASH").length});
 }
 const opening=core.runAll().scenarios.event15m;
 if(opening.terminalAsset!=="CASH"||Math.abs(opening.finalUSD-119.75391720039644)>1e-8)
  throw Error("FROZEN_V1_OPENING_CHANGED");
 const jan=core.loadFrozen().rows.filter(r=>new Date(r.time).getUTCMinutes()===0&&new Date(r.time).getUTCHours()%3===0);
 const febRows=review.loadFebruary3h();
 const later=review.loadHoldout().rows.filter(r=>r.time<Date.parse("2026-09-30T21:00:00.000Z"));
 const train=v4.trainBefore(hist,Date.parse("2026-01-01T00:00:00Z"));
 const febWarmup=warmup([...hist,...jan],febRows[0].time);
 const all=[...febRows,...later];
 const sim=run(all,train,{initialUSD:opening.finalUSD,id:"FEB_TO_SEP_2026",priorHistory:febWarmup,macroByTime:macroSource.data});
 const months=["2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"];
 const monthly=[];
 let prev=opening.finalUSD;
 for(const month of months){
  const sub=sim.ledger.filter(x=>x.tr.slice(0,7)===month);
  if(sub.length<110)throw Error("V5_MISSING_MONTH "+month);
  const end=sub.at(-1),current=end.netUSD;
  monthly.push({month,initialUSD:prev,finalUSD:current,
   differenceUSD:current-prev,position:end.position,
   buys:sub.filter(x=>x.action==="BUY_GOLD").length,
   sells:sub.filter(x=>x.action==="SELL_TO_CASH").length,
   endExposurePct:end.goldOunces?100*end.goldOunces*all.find(x=>x.tt===end.utc).c*(1-FEE)/
       Math.max(1e-8,end.netUSD):0});
  prev=current;
 }
 const continuousV4=review.runForwardReview();
 const result={
  version:VERSION,status:"CROSS_ASSET_RETROSPECTIVE_NOT_BLIND",
  eventEvidence:audit,cmeByYear:macroSource.byYear,sourcePins:PINS,
  fixedPolicy:P,
  training:{originUTC:train.asOfUTC,trainingRows:train.trainBars,stressCases:train.episodeCount,
   causalMechanism:"UNRESOLVED",probabilityCalibrated:false},
  years:yearly,monthResults:monthly,
  fromFebThroughSeptember:{
   openingUSD:opening.finalUSD,finalUSD:sim.finalUSD,position:sim.terminalAsset,
   maxDrawdownPct:sim.maxDrawdownPct,
   trades:sim.actions.map(({utc,tr,action,reason,price,phase,asof,slow,cashUSD,goldOunces,macro})=>
    ({utc,tr,action,reason,price,phase,asof,slow,cashUSD,goldOunces,macro}))
  },
  comparison:{V4:continuousV4.actual.finalUSD,CASH:continuousV4.benchmarks.cashOnlyUSD,
   FIRST_BANK_BUY_HOLD:continuousV4.benchmarks.firstBankWindowBuyHoldUSD},
  warnings:["V5 proposed after 2026 Feb-Sep outcomes were inspected: no prospective OOS claims.",
   "Commission proxy only: bank bid-ask spread not included.",
   "2023 XAU training coverage incomplete; G05-C and G06-B remain unverified economic hypotheses.",
   "The portfolio state never resets between months; no future label is a decision input."],
  promotionAuthorized:false
 };
 const old=require("./recovery_v5").fullResearch();
 result.comparison.V5=old.fromFebThroughSeptember.finalUSD;
 const pair=yearly.filter(y=>y.year!==2023).map(y=>{
  const ref=old.years.find(o=>o.year===y.year);
  return {year:y.year,V6:y.finalUSD,V5:ref.finalUSD,buyHold:y.buyHoldUSD,
   v6Trades:y.buys+y.sells,v5Trades:ref.buys+ref.sells,
   beatsV5:y.finalUSD>ref.finalUSD,
   beatsHold:y.finalUSD>y.buyHoldUSD,
   doesNotAddTrades:y.buys+y.sells<=ref.buys+ref.sells};
 });
 result.scientificGate={status:"REJECT_AUTOMATIC_PROMOTION",authorized:false,
  testedFullYears:pair,beatsV5Both:pair.every(x=>x.beatsV5),
  beatsHoldBoth:pair.every(x=>x.beatsHold),
  noAddedTradesBoth:pair.every(x=>x.doesNotAddTrades),
  economicCauseProven:false,prospectiveBlind:false,realBankBidAsk:false};

 result.promotionAuthorized=result.scientificGate.authorized;
 return result;
}
module.exports={VERSION,P,PINS,EVENT_PANEL,loadMacro,economicEvidence,regime,warmup,updateEma,run,fullResearch};
