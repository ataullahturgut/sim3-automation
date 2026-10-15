"use strict";
/**
 * Hindsight maximum on a discrete 3H, bank-window XAU MID checkpoint panel.
 * NEVER an as-of strategy and NEVER an attainable banking execution promise.
 * Starts every calendar month in CASH and ends every month in CASH.
 */
const {loadRows}=require("./adaptive_v7_app");
const FEE=.008;
function trMonth(utc){
 const v=Date.parse(utc);
 if(!Number.isFinite(v))throw Error("INVALID_UTC");
 return new Date(v+10800000).toISOString().slice(0,7);
}
function quoteByMonth(rows,year="2026"){
 const m=new Map();
 for(const r of rows){
  const hour=new Date(r.tt).getUTCHours(),month=trMonth(r.tt);
  if(![6,9,12].includes(hour)||!month.startsWith(year+"-"))continue;
  const price=r.p;
  if(!Number.isFinite(price)||price<=0)throw Error("BAD_PRICE:"+r.tt);
  if(!m.has(month))m.set(month,[]);
  m.get(month).push({utc:r.tt,time:Date.parse(r.tt),price});
 }
 return [...m].sort((x,y)=>x[0].localeCompare(y[0])).map(([month,quotes])=>{
  quotes.sort((x,y)=>x.time-y.time);
  if(quotes.length<40)throw Error("MISSING_MONTH:"+month);
  for(let i=1;i<quotes.length;i++)if(quotes[i].time<=quotes[i-1].time)throw Error("DUPLICATE_OR_BAD_TIME");
  return {month,quotes};
 });
}
function maximizeCompletedRounds(quotes,maxRounds=1,minHoldHours=0){
 if(!Number.isSafeInteger(maxRounds)||maxRounds<1||maxRounds>25)throw Error("INVALID_MAX_ROUNDS");
 if(!Number.isFinite(minHoldHours)||minHoldHours<0)throw Error("INVALID_MIN_HOLD");
 const starter={value:100,actions:[]};
 let cash=Array.from({length:maxRounds+1},(_,i)=>i===0?starter:null);
 let gold=Array(maxRounds+1).fill(null);
 for(const q of quotes){
  const nextCash=cash.slice(),nextGold=gold.slice();
  for(let k=0;k<=maxRounds;k++){
    if(cash[k]){
      const proposal={value:cash[k].value*(1-FEE)/q.price,
        buyTime:q.time,actions:[...cash[k].actions,{side:"BUY",utc:q.utc,mid:q.price}]};
      if(!nextGold[k]||proposal.value>nextGold[k].value)nextGold[k]=proposal;
    }
    if(k<maxRounds&&gold[k]&&q.time-gold[k].buyTime>=minHoldHours*3600000){
      const proposal={value:gold[k].value*q.price*(1-FEE),
         actions:[...gold[k].actions,{side:"SELL",utc:q.utc,mid:q.price}]};
      if(!nextCash[k+1]||proposal.value>nextCash[k+1].value)nextCash[k+1]=proposal;
    }
  }
  cash=nextCash;gold=nextGold;
 }
 const best=cash.reduce((best,current)=>current&&(!best||current.value>best.value)?current:best,null);
 if(!best)throw Error("ORACLE_NO_CASH");
 return {startingUSD:100,finalUSD:best.value,netPct:best.value-100,
    buys:best.actions.filter(x=>x.side==="BUY").length,
    actions:best.actions,realTimeAvailable:false};
}
function runIntramonthOracle(rows=loadRows()){
 const months=quoteByMonth(rows,"2026").map(m=>{
  const base=100*(1-FEE)**2*m.quotes.at(-1).price/m.quotes[0].price;
  const single=maximizeCompletedRounds(m.quotes,1);
  const double=maximizeCompletedRounds(m.quotes,2);
  const cap15=maximizeCompletedRounds(m.quotes,15);
  const cap15hold24=maximizeCompletedRounds(m.quotes,15,24);
  return {month:m.month,firstUTC:m.quotes[0].utc,lastUTC:m.quotes.at(-1).utc,
    checkpoints:m.quotes.length,firstQuote:m.quotes[0].price,lastQuote:m.quotes.at(-1).price,
    holdGoldNetUSD:base,bestOfMonthlyCashGoldUSD:Math.max(100,base),
    bestOneRound:single,bestTwoRounds:double,bestAnyUpTo15Rounds:cap15,
    bestUpTo15MinHold24h:cap15hold24
  };
 });
 const portfolio={cashMonthly:119.753917,one:119.753917,two:119.753917,upto15:119.753917,hold24:119.753917};
 for(const m of months.filter(x=>x.month>="2026-02")){
   portfolio.cashMonthly*=m.bestOfMonthlyCashGoldUSD/100;
   portfolio.one*=m.bestOneRound.finalUSD/100;
   portfolio.two*=m.bestTwoRounds.finalUSD/100;
   portfolio.upto15*=m.bestAnyUpTo15Rounds.finalUSD/100;
   portfolio.hold24*=m.bestUpTo15MinHold24h.finalUSD/100;
 }
 return {status:"EX_POST_UNTRADEABLE_ORACLE",
    method:"DISCRETE_HINDSIGHT_DYNAMIC_PROGRAM_CASH_GOLD_FULLY_LIQUIDATED_MONTHLY",
    scope:"XAU 3H MID checkpoints, only TS 09:00/12:00/15:00",
    costs:{eachSide:FEE,realBankBidAsk:false,slippage:false},
    constraints:{monthStartsCash:true,monthEndsCash:true,
      noSameCheckpointBuyAndSell:true,oneRoundMeansAtMostOneCompleteBuySell:true},
    months,continuationUSD:portfolio,
    warnings:[
     "Uses every future quote of each month when selecting buy/sell; impossible to follow as an as-of algorithm.",
     "Is a mathematical maximum only on this sampled grid, within a limited trade-count policy; not true market-wide maximum.",
     "Real bank BID/ASK and quote timing unverified; cannot infer executable returns.",
     "Unlike V7, forces liquidating at each calendar month-end; requires a normalized execution contract for fair comparisons."
    ],independentBlindTest:false,liveTradingAuthorized:false
 };
}
module.exports={FEE,trMonth,quoteByMonth,maximizeCompletedRounds,runIntramonthOracle};
