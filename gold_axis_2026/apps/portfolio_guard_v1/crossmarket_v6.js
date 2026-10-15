"use strict";
/**
 * V6 cross-market as-of factual confirmation gate.
 * Hypothesis first: use CLOSED NQ+ZN H1 bars to defer buy / accelerate
 * downside exit when independent market stress coincides with XAU risk.
 *
 * Does NOT claim that NQ/ZN prices prove G05-C or G06-B causality.
 * Macro events without verified firstprint are audit-only metadata.
 * The thresholds are fixed before V6 historical P&L is calculated.
 * All 2023–26 returns are retrospective (already observed in the project).
 */
const fs=require("node:fs"),path=require("node:path");
const core=require("./engine"),v3=require("./recovery_v3"),v4=require("./recovery_v4");
const feb=require("./monthly_runner"),forward=require("./v4_forward_review");
const REPO=path.resolve(__dirname,"../../..");
const VERSION="V6_CROSSMARKET_CONFIRMATION_PROVISIONAL_20261015";
const FEE=.008;
const SPECS=Object.freeze([
 {path:"gold_axis_2026/apps/portfolio_guard_v1/data/CROSSMARKET_ASOF_2023_2024_3H_V1.csv",blob:"20f237093d8f073664baeab2f61bcca4c00a6d16"},
 {path:"gold_axis_2026/apps/portfolio_guard_v1/data/CROSSMARKET_ASOF_2025_2026_3H_V1.csv",blob:"392a505456355cb39485253c601760dc0f09b6e6"}
]);
const EVENTS=Object.freeze({
 path:"gold_axis_2026/OLAY_02_96_TUM_VAKA_EVRENSEL_ORUNTU_MATRIKS_20261015.csv",
 blob:"4b6c8fd84ea291ae22ddc9b0d5d545ce2d8fa527"
});
const POLICY=Object.freeze({
 nqDrawdown6hPct:-.8,znFall6hPct:-.12,
 xauSlowDownPct:-1.3,xauFastDownPct:-.5,
 maximumH1AgeHours:4,
 bankHoursTurkey:[9,12,15],
 sideCost:.008,
 causalAttribution:"UNRESOLVED",
 stressInterpretation:"NQ_AND_ZN_COPRICE_STRESS_ONLY_NOT_NEWS_CAUSALITY"
});
const TR=new Intl.DateTimeFormat("sv-SE",{timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false});
function loadCross(){
 const rows=SPECS.flatMap(spec=>core.decodePinnedSource(spec,fs.readFileSync(path.join(REPO,spec.path))).rows);
 if(rows.length!==4107)throw Error("CROSS_SOURCE_COUNT_CHANGED");
 const store=new Map(),years={};
 for(const row of rows){
  const tt=row.tt,time=Date.parse(tt);
  if(!Number.isFinite(time)||!tt.endsWith("00:00.000Z"))throw Error("INVALID_CROSS_TIMESTAMP");
  if(store.has(time))throw Error("CROSS_TIME_DUPLICATE");
  const x={tt,time};
  for(const k of ["nq6","zn6","si6","cl6","age_nq","age_zn","age_si","age_cl"])
   x[k]=row[k]===""?null:Number(row[k]);
  for(const symbol of ["nq","zn","si","cl"]){
   const val=x[symbol+"6"],age=x["age_"+symbol];
   if(val!==null&&(!Number.isFinite(val)||!Number.isInteger(age)||age<1||age>POLICY.maximumH1AgeHours))
    throw Error("CROSS_FUTURE_OR_STALE_CANDLE");
  }
  if(![6,9,12].includes(new Date(time).getUTCHours()))throw Error("NOT_BANK_HOUR_UTC");
  const yr=tt.slice(0,4);
  years[yr]??={rows:0,matchedNq:0,matchedZn:0,matchedNqZn:0,matchedSilver:0};
  years[yr].rows++;
  if(x.nq6!==null)years[yr].matchedNq++;
  if(x.zn6!==null)years[yr].matchedZn++;
  if(x.nq6!==null&&x.zn6!==null)years[yr].matchedNqZn++;
  if(x.si6!==null)years[yr].matchedSilver++;
  store.set(time,x);
 }
 return {store,years,sourceHashes:SPECS};
}
function auditEventDNA(){
 const rows=core.decodePinnedSource(EVENTS,fs.readFileSync(path.join(REPO,EVENTS.path))).rows;
 const stats={totalCases:rows.length,confirmedFirstprints:0,provenCauses:0,
  economicCandidates:[],asOfValidatedForTrading:0,hasEconomicFirstprintEvidence:false};
 const groups=new Set();
 for(const e of rows){
  if(e.onset_firstprint_verified==="YES")stats.confirmedFirstprints++;
  if(e.mechanism_caused_proven==="YES")stats.provenCauses++;
  if(e.asof_action_validated==="YES")stats.asOfValidatedForTrading++;
  if(e.candidate_DNA)groups.add(e.candidate_DNA);
 }
 stats.economicCandidates=[...groups].sort();
 stats.hasEconomicFirstprintEvidence=stats.confirmedFirstprints>0;
 return stats;
}
function classifyCross(row){
 if(!row||row.nq6===null||row.zn6===null)
  return {state:"UNKNOWN_DATA",source:"NQ_ZN",causalMechanism:"UNRESOLVED"};
 if(row.nq6<=POLICY.nqDrawdown6hPct&&row.zn6<=POLICY.znFall6hPct)
  return {state:"BROAD_COSELL_PRICE_PROXY",source:"NQ_ZN",causalMechanism:"UNRESOLVED"};
 return {state:"NO_JOINT_STRESS",source:"NQ_ZN",causalMechanism:"UNRESOLVED"};
}
function simulate(rows,training,cross,{startUSD=100,id="V6",overlay=false}={}){
 if(!(Number.isFinite(startUSD)&&startUSD>0))throw Error("INVALID_CASH");
 let cash=startUSD,ounces=0,peak=0,prev=null,phase="UNKNOWN",lastClose=null;
 let recoveryStreak=0,trendStreak=0,breachDecisions=0,
  lastBuy=-Infinity,lastSell=-Infinity,lastRiskDecision=-Infinity;
 let maxValue=startUSD,maxDD=0,observed=0,eligibleCount=0;
 const actions=[],ledger=[],gates={matched:0,unmatched:0,stress:0,blockedBuy:0,acceleratedSell:0};
 for(const r of rows){
  if(!Number.isFinite(r.time)||!Number.isFinite(r.c)||!Number.isFinite(r.p)||r.c<=0||r.p<=0)throw Error("INVALID_ASOF_ROW");
  if(prev&&r.time<=prev.time)throw Error("NONMONOTONIC_SOURCE");
  if(prev&&r.time-prev.time>12*3600000){
   recoveryStreak=0;trendStreak=0;breachDecisions=0;prev=null;phase="UNKNOWN";
  }
  const sig=v4.classify(r,prev,phase,training);
  recoveryStreak=sig.recovery?recoveryStreak+1:0;
  trendStreak=sig.trend?trendStreak+1:0;
  phase=sig.phase;observed++;lastClose=r.c;
  if(ounces)peak=Math.max(peak,r.c);
  const eligible=v3.isDecisionTime(r.time);
  const quote=eligible?cross.store.get(r.time):null;
  const m=eligible?classifyCross(quote):{state:"NOT_DECISION_SLOT"};
  const macroStress=eligible&&m.state==="BROAD_COSELL_PRICE_PROXY";
  if(eligible){
   if(m.state==="UNKNOWN_DATA")gates.unmatched++;
   else gates.matched++;
   if(macroStress)gates.stress++;
  }
  let action=ounces?"HOLD_GOLD":"HOLD_CASH",reason="COST_AWARE_NO_ACTION",target=null;
  if(eligible){
   eligibleCount++;
   const gap=r.time-lastRiskDecision;
   breachDecisions=sig.breach?(gap<=12*3600000?breachDecisions+1:1):0;
   lastRiskDecision=r.time;
   const trailing=ounces&&100*(r.c/peak-1)<=v4.PARAMETERS.drawdownGuardPct&&r.r4<=-.8&&r.r92<=-1.5;
   const noImmediateFlip=(r.time-lastBuy)>=v4.PARAMETERS.afterBuyProtectionHours*3600000;
   const sustainedDown=breachDecisions>=v4.PARAMETERS.exitConfirmDecisionBars&&(r.r276<0||trailing);
   const macroExit=overlay&&macroStress&&r.r92<=POLICY.xauSlowDownPct&&r.r4<=POLICY.xauFastDownPct;
   if(ounces&&(sig.emergency||(noImmediateFlip&&(sustainedDown||macroExit)))){
    if(macroExit&&!sustainedDown&&!sig.emergency)gates.acceleratedSell++;
    cash+=ounces*r.p*(1-FEE);ounces=0;peak=0;lastSell=r.time;
    breachDecisions=0;recoveryStreak=0;trendStreak=0;
    action="SELL_TO_CASH";reason=sig.emergency?"EMERGENCY_SHOCK":
     sustainedDown?"V4_SUSTAINED_DOWNSIDE":"CROSSMARKET_NQ_ZN_PRICED_STRESS";
   }else if(cash>startUSD*1e-7&&r.time-lastSell>=v4.PARAMETERS.afterSellCooldownHours*3600000){
    const confirmRecovery=recoveryStreak>=v4.PARAMETERS.recoveryConfirmBars;
    const confirmTrend=trendStreak>=v4.PARAMETERS.trendConfirmBars;
    if(confirmRecovery||confirmTrend){
     if(overlay&&macroStress){gates.blockedBuy++;}
     else{
      const nav=cash+ounces*r.p*(1-FEE);
      let riskWeight=1;
      const evidence=v3.neighbors(r,training.bank);
      if(evidence.nMatched>=6&&evidence.caseDownFraction!==null&&
         evidence.caseDownFraction>=.5)riskWeight=v4.PARAMETERS.shockBuyFractionCut;
      const desired=nav*(confirmTrend?v4.PARAMETERS.confirmedTrendPortfolioTarget:
        v4.PARAMETERS.recoveryPortfolioTarget)*riskWeight;
      const current=ounces*r.p*(1-FEE);
      const allocation=Math.min(cash,Math.max(0,desired-current));
      if(allocation>Math.max(.01,nav*.03)){
       cash-=allocation;ounces+=allocation*(1-FEE)/r.p;
       peak=Math.max(peak,r.c);lastBuy=r.time;
       action="BUY_GOLD";
       reason=confirmTrend?"TREND_CONTINUATION_BUY":"RECOVERY_PHASE_HALF_ENTRY";
       target=desired/nav;
      }
     }
    }
   }
  }else reason="OUTSIDE_TR_09_17";
  const nav=cash+ounces*r.c*(1-FEE);
  maxValue=Math.max(nav,maxValue);maxDD=Math.max(maxDD,100*(1-nav/maxValue));
  const rowOut={utc:r.tt,tr:TR.format(new Date(r.time)),action,reason,
   macroState:m.state,phase:sig.phase,price:r.p,
   cashUSD:cash,goldOunces:ounces,nav:Math.round(nav*1e4)/1e4};
  ledger.push(rowOut);
  if(action==="BUY_GOLD"||action==="SELL_TO_CASH")actions.push({...rowOut,target,asof:{
   nq6:quote?quote.nq6:null,zn6:quote?quote.zn6:null,
   ageNq:quote?quote.age_nq:null,ageZn:quote?quote.age_zn:null,
   xauR4:r.r4,xauR92:r.r92},economicDNA:"UNRESOLVED"});
  prev=r;
 }
 if(lastClose===null)throw Error("EMPTY_SERIES");
 return {version:VERSION,model:overlay?"V6_CROSS":"V4_CLONE",id,startUSD,finalUSD:cash+ounces*lastClose*(1-FEE),
  terminalAsset:ounces?"GOLD":"CASH",cashUSD:cash,goldOunces:ounces,
  hypotheticalExitFeeDeducted:ounces>0,maxDrawdownPct:maxDD,
  controls:observed,checks:eligibleCount,gateStats:gates,
  actions,ledger};
}
function runResearch(){
 const hist=v3.loadHistorical(),cross=loadCross();
 const years=[2023,2024,2025].map(yr=>{
  const rows=hist.filter(r=>r.tt.startsWith(String(yr)));
  const training=v4.trainBefore(hist,Date.parse(yr+"-01-01T00:00:00Z"));
  const off=simulate(rows,training,cross,{startUSD:100,id:"YEAR_"+yr,overlay:false});
  const v4ref=v4.simulate(rows,training,{startUSD:100,id:"YEAR_"+yr});
  if(Math.abs(off.finalUSD-v4ref.finalUSD)>1e-8||off.actions.length!==v4ref.actions.length)
   throw Error("V4_COUNTERFACTUAL_DIVERGENCE_"+yr);
  const on=simulate(rows,training,cross,{startUSD:100,id:"YEAR_"+yr,overlay:true});
  const hold=100*(1-FEE)/rows[0].p*rows.at(-1).c*(1-FEE);
  return {year:yr,sourceCoverageWarning:yr===2023,trainUntil:training.trainingEndUTC,
   V4:off.finalUSD,V6:on.finalUSD,change:on.finalUSD-off.finalUSD,
   buyHoldUSD:hold,cashOnlyUSD:100,
   v4DrawdownPct:off.maxDrawdownPct,v6DrawdownPct:on.maxDrawdownPct,
   v4TradeCount:off.actions.length,v6TradeCount:on.actions.length,
   gateStats:on.gateStats,
   edits:on.actions};
 });
 const training=v4.trainBefore(hist,Date.parse("2026-01-01T00:00:00Z"));
 const opening=core.runAll().scenarios.event15m;
 if(Math.abs(opening.finalUSD-119.75391720039644)>1e-8)throw Error("BASE_JAN_CHANGED");
 const observations=[...forward.loadFebruary3h(),...forward.loadHoldout().rows.filter(
   r=>r.time<Date.parse("2026-09-30T21:00:00.000Z"))];
 const off=simulate(observations,training,cross,{startUSD:opening.finalUSD,id:"2026_FEB_SEP",overlay:false});
 const ref=forward.runForwardReview();
 if(Math.abs(off.finalUSD-ref.actual.finalUSD)>1e-8||off.actions.length!==ref.actions.length)
  throw Error("V4_CONTINUOUS_2026_DIVERGENCE");
 const on=simulate(observations,training,cross,{startUSD:opening.finalUSD,id:"2026_FEB_SEP",overlay:true});
 const months=["02","03","04","05","06","07","08","09"].map(m=>{
  const y="2026-"+m,loc=r=>r.tr.slice(0,7)===y;
  const a=off.ledger.filter(loc),b=on.ledger.filter(loc);
  if(!a.length||!b.length)throw Error("MISSING_MONTH_"+y);
  return {month:y,V4:a.at(-1).nav,V6:b.at(-1).nav,
   V4actions:a.filter(x=>x.action==="BUY_GOLD"||x.action==="SELL_TO_CASH").length,
   V6actions:b.filter(x=>x.action==="BUY_GOLD"||x.action==="SELL_TO_CASH").length};
 });
 return {
  version:VERSION,status:"EXPLORATORY_CROSSMARKET_PRICE_CONFIRMATION_NOT_CAUSALITY",
  frozenPolicy:POLICY,sourceHashes:cross.sourceHashes,eventsSourceHash:EVENTS.blob,
  dataCoverage:cross.years,caseAudit:auditEventDNA(),
  annual:years,months,
  continuity:{openingCashUSD:opening.finalUSD,v4USD:off.finalUSD,v6USD:on.finalUSD,
   v4MaxDDPct:off.maxDrawdownPct,v6MaxDDPct:on.maxDrawdownPct,
   v4Trades:off.actions.length,v6Trades:on.actions.length,
   v6GateStats:on.gateStats,v6Orders:on.actions,
   initialAsset:"CASH",finalAsset:on.terminalAsset},
  evidence:{verifiedEconomicCausality:false,
   validatedFuturePerformance:false,prospectivelyBlind:false,
   actualBankBidAskIncluded:false,macroH1BarEndLagHours:1,commissionPerSide:FEE,
   asofDescription:"latest completed CME H1 (ts_event <= decisionUTC-1h), max4h age, valid prior 6 bars span <=9h",
   silentSilverExclusion:"SI hourly not sufficiently fresh at most bank slots"},
  automaticPromotionAuthorized:false
 };
}
module.exports={VERSION,POLICY,SPECS,EVENTS,loadCross,auditEventDNA,classifyCross,simulate,runResearch};
