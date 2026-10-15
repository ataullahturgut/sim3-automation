"use strict";
/** Full unbroken 2023-2026 run vs reset-on-2026 evaluation.
 * Scientific diagnosis only; no parameter refitting or trade permission. */
const {loadFullRows}=require("./v8_regret_engine");
const {dataset}=require("./v11_ann_research");
const {memoryTimeline}=require("./v12_rehber_agent");
const START="2023-01-03T06:00:00Z",END="2026-09-30T12:00:00Z";
function diag(){
 const src=loadFullRows(),ds=dataset(src.rows);
 const run=memoryTimeline(ds,{start:START,end:END,initial:100,
   variant:"REHBER_CORE",includeDecisions:true});
 const isolated2026=memoryTimeline(ds,{start:"2026-02-02T06:00:00Z",end:END,
   initial:119.753917,variant:"REHBER_CORE"});
 const bank=ds.bank.filter(r=>r.ts<=Date.parse(END));
 const firstEntry=bank.find(r=>r.ts>Date.parse(START)),lastExit=bank.at(-1);
 const passiveBuyAndHold=100*(1-.008)**2*lastExit.p/firstEntry.p;
 const byYear=[];
 for(let year=2023;year<=2026;year++){
  const yr=String(year),signals=run.decisions.filter(x=>x.asOf.startsWith(yr));
  const cashReady=signals.filter(x=>x.gates&&x.position==="CASH");
  const count=k=>cashReady.filter(x=>x.gates[k]).length;
  const lastMonth=run.monthly.filter(m=>m.month.startsWith(yr)).at(-1);
  byYear.push({year,yearEndUSD:lastMonth?.nav||null,signals:signals.length,
   memoryReadyDays:signals.filter(x=>x.gates).length,
   cashOpportunityDays:cashReady.length,
   buyNetGainGateDays:count("profit"),
   buyProbabilityGateDays:count("probability"),
   buyTailRiskGateDays:count("tail"),
   buyStressGateDays:count("stressFree"),
   allBuyGatesDays:cashReady.filter(x=>["profit","probability","tail","stressFree"].every(k=>x.gates[k])).length,
   filledTrades:run.trades.filter(x=>x.at.startsWith(yr)).length,
   allPredicted14BelowZero:signals.filter(x=>x.gates).every(x=>x.predictedNet14<=0)});
 }
 const firstReady=run.decisions.find(x=>x.gates)?.asOf??null;
 if(firstReady!=="2023-03-17T06:00:00.000Z")throw Error("V12_READINESS_DRIFT");
 if(run.trades[0]?.at!=="2026-01-30T09:00:00.000Z")throw Error("V12_FIRST_TRADE_DRIFT");
 if(Math.abs(run.final-100.07688106607975)>1e-5)throw Error("V12_FULL_RUN_DRIFT");
 if(Math.abs(isolated2026.final-135.66380806850964)>1e-5)throw Error("V12_SHORT_RUN_DRIFT");
 if(byYear.find(x=>x.year===2024).buyNetGainGateDays!==0||
    byYear.find(x=>x.year===2025).buyProbabilityGateDays!==0)
     throw Error("V12_NO_BUY_REASON_DRIFT");
 return {version:"V12_EARLIEST_UNBROKEN_CHRONOLOGICAL_AUDIT_20261016",
   status:"FAILED_GENERALIZATION_NO_MODEL_PROMOTION",
   continuous:{start:START,end:END,initialUSD:100,
    finalUSD:run.final,returnPct:run.netPct,
    totalTrades:run.trades.length,trades:run.trades,
    monthly:run.monthly,yearly:byYear,
    maturedMemoryLabels:run.completedAnalogLabels,
    distinctFourteenDayBlocks:run.independentEpisodeBlocks,
    firstCompleted14DayLabel:ds.samples[0].exit14UTC,
    earliestMemoryReady:firstReady,
    firstFilledTrade:run.trades[0],
    learningChanges:run.learning.updates},
   resetFeb2026:{initialUSD:119.753917,finalUSD:isolated2026.final,
    trades:isolated2026.trades.length,
    WARNING:"NOT_AN_UNBROKEN_2023_PORTFOLIO"},
   passiveGold:{initialUSD:100,finalUSD:passiveBuyAndHold,
    buyAt:firstEntry.tt,buyPrice:firstEntry.p,
    sellAt:lastExit.tt,sellPrice:lastExit.p,
    bankFeeEachLeg:.008},
   rootCause:{
    onlyTechnicalMarketFeatures:true,
    fixed14DayBankFeeNetTarget:true,
    fixedProfitProbabilityThreshold:.58,
    regimeDurationLearnerAbsent:true,
    2024Failure:"ZERO_DAYS_PASSED_POSITIVE_NET_GAIN_GATE",
    2025Failure:"ZERO_DAYS_PASSED_58_PERCENT_PROFIT_PROBABILITY",
    specialistReliabilityAblationNoTradeChange:true,
    decisionMarginAblationNoTradeChange:true,
    maturedNewMemoryCanChangeActions:true
   },
   auditLimitations:{eventsFirstprintVerified:0,
    trueBankBidAsk:false,alreadyInspected2023To2026:true,
    prospectiveBlindPeriod:false,canTradeLive:false,
    commissionAppliedAsSyntheticPriceFee:true},
   scientificGate:{promote:false,reason:"NO_PERSISTENT_UPTREND_RECOGNITION_OR_UNSEEN_PROSPECTIVE_TEST"}};
}
module.exports={diag};
