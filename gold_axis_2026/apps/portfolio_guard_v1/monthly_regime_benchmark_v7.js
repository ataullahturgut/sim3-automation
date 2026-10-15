"use strict";
/**
 * V7 independent monthly CASH vs buy-then-liquidate GOLD benchmark.
 * HINDSIGHT best is a diagnostic, NEVER an as-of signal.
 * Baseline previous-month winner is chosen only after previous month finishes.
 */
const {loadRows,runResearch}=require("./adaptive_v7_app");
const PER_SIDE_FEE=.008;
const FIRST_MONTH="2026-02",END_MONTH="2026-09",INITIAL_CASH=119.753917;

function calendarMonth(time){
 return new Date(Date.parse(time)+3*3600000).toISOString().slice(0,7);
}
function monthlyChoices(rows,year="2026"){
 const groups=new Map();
 for(const r of rows){
  const hour=new Date(r.tt).getUTCHours();
  if(![6,9,12].includes(hour))continue;
  const month=calendarMonth(r.tt);
  if(!month.startsWith(year+"-"))continue;
  if(!groups.has(month))groups.set(month,[]);
  groups.get(month).push(r);
 }
 return [...groups].sort(([a],[b])=>a.localeCompare(b)).map(([month,d])=>{
  const first=d[0],last=d.at(-1);
  if(!Number.isFinite(first.p)||!Number.isFinite(last.c)||first.p<=0||last.c<=0)throw Error("INVALID_MONTH_PROXY:"+month);
  if(d.length<40)throw Error("MONTH_TOO_SPARSE:"+month);
  const factor=last.c/first.p*(1-PER_SIDE_FEE)**2;
  return {
   month,checks:d.length,entryUTC:first.tt,exitUTC:last.tt,
   entryMid:first.p,exitMid:last.c,
   goldGrossPct:100*(last.c/first.p-1),goldNetPct:100*(factor-1),
   cashNetPct:0,goldNetFactor:factor,
   hindsightWinner:factor>1?"GOLD":"CASH",
   knownAfterUTC:last.tt
  };
 });
}
function replayMonthlyDecision(rows,config={}){
 const year=config.year||"2026";
 const firstMonth=config.firstMonth||FIRST_MONTH,lastMonth=config.lastMonth||END_MONTH;
 const initial=config.initialUSD??INITIAL_CASH;
 const universe=monthlyChoices(rows,year),prior=new Map(universe.map((x,i)=>[x.month,universe[i-1]]));
 const selected=universe.filter(x=>x.month>=firstMonth&&x.month<=lastMonth);
 if(!selected.length)throw Error("NO_MONTHS");
 let oracle=initial,lagged=initial;
 const comparison=[];
 for(const month of selected){
  const predecessor=prior.get(month.month);
  if(!predecessor||Date.parse(predecessor.knownAfterUTC)>=Date.parse(month.entryUTC))
   throw Error("MISSING_CHRONOLOGIC_PREVIOUS_MONTH:"+month.month);
  const beforeOracle=oracle,beforeLagged=lagged;
  // Oracle is an AFTER-THE-FACT upper benchmark for one trade per month, not a signal.
  const hindsight=month.hindsightWinner;
  oracle*=hindsight==="GOLD"?month.goldNetFactor:1;
  // Lag policy uses ONLY last completed month's hindsight label, available before this month opens.
  const lagAction=predecessor.hindsightWinner;
  lagged*=lagAction==="GOLD"?month.goldNetFactor:1;
  comparison.push({
   ...month,oracleSelected:hindsight,laggedSelected:lagAction,
   predecessorMonth:predecessor.month,predecessorKnownUTC:predecessor.knownAfterUTC,
   oracleInitialUSD:beforeOracle,oracleTerminalUSD:oracle,
   laggedInitialUSD:beforeLagged,laggedTerminalUSD:lagged,
   lagChoiceCorrect:lagAction===hindsight
  });
 }
 const v7=config.skipV7?null:runResearch().primary;
 const v7Months=v7?new Map(v7.months.map(x=>[x.month,x])):null;
 if(v7&&comparison.some(x=>!v7Months.has(x.month)))throw Error("V7_MONTH_ALIGNMENT_FAIL");
 return {
  status:"RETROSPECTIVE_BENCHMARK_HINDSIGHT_NOT_ASOF",
  basis:"SAME_3H_GOLD_PRICE_PROXY_AS_V7",
  definitions:{
   oracle:"Each calendar month the CASH/GOLD decision is picked after seeing the month's outcome. NONTRADEABLE, monthly entry and exit only, costed.",
   lagged:"Pick this month's CASH/GOLD decision from the previous completely ended month's winning policy. ASOF_VALID but not good.",
   monthGold:"Buy first 09:00 Turkey three-hour checkpoint and sell last 15:00 Turkey checkpoint, 0.8% fee on EACH side.",
   cost:"MID proxy, no real bank bid-ask spread / execution slippage.",
   warning:"Monthly oracle not an upper bound for intramonth or more complex strategies; 2026 already known when V7 was designed."
  },
  initialUSD:initial,months:comparison.map(x=>({...x,v7TerminalUSD:v7Months?.get(x.month)?.nav??null,
    v7Position:v7Months?.get(x.month)?.position??null})),
  endUSD:{hindsightMonthlyOracle:oracle,previousMonthWinner:lagged,cash:initial,
   v7:v7?.finalUSD??null,passiveGold:v7?.passiveGoldUSD??null},
  horizon:{firstMonth,lastMonth},
  lagCorrectMonths:comparison.filter(x=>x.lagChoiceCorrect).length,
  lagTotalMonths:comparison.length,
  v7VsMonthlyOracleGapUSD:v7?oracle-v7.finalUSD:null,
  v7CaptureOfMonthlyOracleProfitPct:v7&&oracle!==initial?
     100*(v7.finalUSD-initial)/(oracle-initial):null,
  hindsightChoiceIsNotModelPrediction:true,independentBlindTest:false,
  verifiedMacroCausality:false,bankBidAskIncluded:false,
  acceptedForLiveTrading:false
 };
}
module.exports={PER_SIDE_FEE,calendarMonth,monthlyChoices,replayMonthlyDecision};
