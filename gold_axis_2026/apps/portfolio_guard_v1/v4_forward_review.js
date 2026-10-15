"use strict";
/**
 * Preregistered V4 carry-forward review: Feb through September 2026.
 *
 * No tuning, no lookahead, no artificial monthly portfolio reset.
 * Frozen V4 originally designed after seeing Feb 2026, so this is a
 * controlled retrospective extension, NOT prospective blind OOS.
 */
const fs=require("node:fs"),path=require("node:path");
const engine=require("./engine"),feb=require("./monthly_runner");
const v3=require("./recovery_v3"),v4=require("./recovery_v4");
const ROOT=path.resolve(__dirname,"../../..");
const FEE=.008;
const PIN=Object.freeze({
 path:"gold_axis_2026/apps/portfolio_guard_v1/data/RECOVERY_HOLDOUT_2026_MAR_SEP_3H_ASOF_V1.csv",
 blob:"860917258c84a86a210d8c7f44655d46d878470e"
});
const COLS=["p","c","r4","r92","r276","dd276","v92","rv","ds","eff","loc","dd4"];
function loadHoldout(){
 const bytes=fs.readFileSync(path.join(ROOT,PIN.path));
 const parsed=engine.decodePinnedSource(PIN,bytes);
 const rows=parsed.rows.map(x=>{
  const r={tt:x.tt,time:Date.parse(x.tt)};
  for(const k of COLS)r[k]=x[k]===""?null:Number(x[k]);
  if(!Number.isFinite(r.time)||COLS.some(k=>!Number.isFinite(r[k])|| (["p","c"].includes(k)&&r[k]<=0)))
   throw Error("INVALID_2026_HOLDOUT_FEATURE");
  return r;
 });
 if(rows.length!==1123||rows[0].tt!=="2026-03-02T06:00:00.000Z"||
    rows.at(-1).tt!=="2026-09-30T21:00:00.000Z")
  throw Error("HOLDOUT_SCOPE_CHANGED");
 for(let i=0;i<rows.length;i++){
  if(!/^2026-0[3-9]/.test(rows[i].tt))throw Error("NON_HOLDOUT_TIMESTAMP");
  if(i&&rows[i].time<=rows[i-1].time)throw Error("NONMONOTONIC_HOLDOUT");
 }
 const byUTCMonth=Object.fromEntries(["03","04","05","06","07","08","09"].map(m=>[
  "2026-"+m,rows.filter(r=>r.tt.startsWith("2026-"+m)).length
 ]));
 if(Object.values(byUTCMonth).some(n=>n<120))throw Error("HOLDOUT_MONTH_MISSING_DATA");
 return {rows,byUTCMonth,gitBlob:PIN.blob,linesCRLFConverted:parsed.windowsLineEndingsNormalized};
}
function loadFebruary3h(){
 const source=feb.loadFebruary().rows;
 const rows=source.filter(r=>new Date(r.time).getUTCMinutes()===0&&new Date(r.time).getUTCHours()%3===0);
 if(rows.length!==149||rows[0].tt!=="2026-02-02T06:00:00.000Z"||
    rows.at(-1).tt!=="2026-02-27T21:00:00.000Z")throw Error("FEBRUARY_3H_BAD");
 return rows;
}
function buyingAtFirstBankTime(rows,initialUSD){
 const row=rows.find(r=>v3.isDecisionTime(r.time));
 if(!row||new Date(row.time).getUTCHours()!==6)throw Error("NO_FIRST_BANK_WINDOW");
 return {entryUTC:row.tt,entryTR:"2026-02-02 09:00",
  price:row.p,ounces:initialUSD*(1-FEE)/row.p,feePerDirection:FEE};
}
function readMonthlyCurve(ledger,months,openingUSD){
 const totals=[];
 let prev=openingUSD,rollingPeak=openingUSD;
 for(const month of months){
  const data=ledger.filter(r=>r.tr.slice(0,7)===month);
  if(data.length<110)throw Error("MONTH_COVERAGE_MISSING: "+month+" "+data.length);
  const end=data.at(-1),startUSD=prev;
  const actions=data.filter(x=>x.action==="BUY_GOLD"||x.action==="SELL_TO_CASH");
  let worstDrawdown=0;
  for(const x of data){
   rollingPeak=Math.max(rollingPeak,x.nav);
   worstDrawdown=Math.max(worstDrawdown,100*(1-x.nav/rollingPeak));
  }
  prev=end.nav;
  totals.push({
   month,initialNetUSD:startUSD,terminalNetUSD:end.nav,
   changeUSD:end.nav-startUSD,changePct:100*(end.nav/startUSD-1),
   position:end.position,netGoldOunces:end.goldOunces,cashUSD:end.cashUSD,
   bars:data.length,buys:actions.filter(x=>x.action==="BUY_GOLD").length,
   sells:actions.filter(x=>x.action==="SELL_TO_CASH").length,
   maxCumulativeDrawdownPct:worstDrawdown,
   firstSeenUTC:data[0].utc,lastSeenUTC:end.utc
  });
 }
 return totals;
}
function runForwardReview(){
 const initial=engine.runAll().scenarios.event15m;
 if(initial.terminalAsset!=="CASH"||Math.abs(initial.finalUSD-119.75391720039644)>1e-8)
  throw Error("JAN_INITIAL_CASH_NOT_FROZEN");
 const train=v4.trainBefore(v3.loadHistorical(),Date.parse("2026-01-01T00:00:00Z"));
 const february=loadFebruary3h();
 const remaining=loadHoldout();
 // Sept 30, 21:00 UTC is Oct 1, 00:00 Turkey, so exclude it
 // from a September month-end result. Source stays byte-for-byte pinned.
 const cutoffTurkeyMonth=Date.parse("2026-09-30T21:00:00.000Z");
 const observations=[...february,...remaining.rows.filter(r=>r.time<cutoffTurkeyMonth)];
 const actual=v4.simulate(observations,train,{initialUSD:initial.finalUSD,id:"FROZEN_V4_FEB_TO_SEP_2026"});
 const febOnly=v4.simulate(february,train,{initialUSD:initial.finalUSD,id:"REFERENCE_FEB_ONLY"});
 const months=["2026-02","2026-03","2026-04","2026-05","2026-06","2026-07","2026-08","2026-09"];
 const monthly=readMonthlyCurve(actual.ledger,months,initial.finalUSD);
 if(Math.abs(febOnly.finalUSD-monthly[0].terminalNetUSD)>0.00011)
  throw Error("CONTINUATION_RETROACTIVELY_CHANGED_FEB");
 if(Math.abs(febOnly.finalUSD-122.86790914239303)>1e-7)
  throw Error("V4_LOCKED_FEB_RESULT_CHANGED");
 const buyHold=buyingAtFirstBankTime(february,initial.finalUSD);
 const passiveValue=buyHold.ounces*observations.at(-1).c*(1-FEE);
 const cashValue=initial.finalUSD;
 const monthlyBenchmarks=monthly.map(x=>{
  const priceRow=observations.find(r=>r.tt===x.lastSeenUTC);
  const hold=buyHold.ounces*priceRow.c*(1-FEE);
  return {month:x.month,cashOnlyUSD:cashValue,
   firstBankWindowBuyHoldUSD:hold,
   V4USD:x.terminalNetUSD,
   V4MinusCashUSD:x.terminalNetUSD-cashValue,
   V4MinusBuyHoldUSD:x.terminalNetUSD-hold};
 });
 const severeGaps=[];
 for(let i=1;i<observations.length;i++){
  const ms=observations[i].time-observations[i-1].time;
  if(ms>72*3600000)severeGaps.push({
   before:observations[i-1].tt,after:observations[i].tt,gapHours:ms/3600000
  });
 }
 return {
  version:"V4_UNCHANGED_POLICY_FORWARD_REVIEW_20261015",
  status:"PRE_REGISTERED_RETROSPECTIVE_NOT_PROSPECTIVE_BLIND",
  unchangedPolicy:v4.VERSION,thresholdCalibrationCutoffUTC:train.asOfUTC,
  source:{...PIN,expectedRows:1123,months:remaining.byUTCMonth,
   februarySource:feb.FEB.path,coverageWarning:"2023 training source coverage is incomplete"},
  startingCashUSD:initial.finalUSD,initialPosition:"CASH",feePerSide:FEE,
  actual:{finalUSD:actual.finalUSD,returnPct:actual.returnPct,
   totalBuys:actual.actions.filter(x=>x.action==="BUY_GOLD").length,
   totalSells:actual.actions.filter(x=>x.action==="SELL_TO_CASH").length,
   endPosition:actual.terminalAsset,endGoldOunces:actual.goldOunces,
   endCashUSD:actual.cashUSD,maxDrawdownPct:actual.maxDrawdownPct},
  benchmarks:{cashOnlyUSD:cashValue,firstBankWindowBuyHoldUSD:passiveValue,
   firstBankWindowBuyHoldEntry:buyHold.entryTR,
   holdIsCounterfactualWithFullLookback:false},
  monthly,monthlyBenchmarks,
  actions:actual.actions.map(({utc,tr,action,price,reason,phase,decisionData,cashUSD,goldOunces})=>
   ({utc,tr,action,price,reason,phase,decisionData,cashUSD,goldOunces})),
  monthEndCarryVerified:monthly.every((m,i)=>i===0||
    Math.abs(m.initialNetUSD-monthly[i-1].terminalNetUSD)<1e-9),
  observations:observations.length,monthEndTurkeyUTC:"2026-09-30T21:00:00.000Z",largeGaps:severeGaps,
  economicMechanismVerified:false,bankBidAskIncluded:false,
  futureLabelAsDecisionFeature:false,
  hasProspectiveBlindValidation:false,
  preregistration:"V4_POST_FEB_2026_PRE_REGISTERED_EVALUATION_20261015.md",
  decision:"DESCRIPTIVE_AUDIT_ONLY_NO_AUTOMATED_V4_PROMOTION"
 };
}
module.exports={PIN,loadHoldout,loadFebruary3h,buyingAtFirstBankTime,readMonthlyCurve,runForwardReview};
