"use strict";
/* 3 Jan 2023, 09:00 Turkey: CME-derived historical gold MID PROXY,
   NOT retail bank bid/ask. As-of-only signal at 06/09 UTC, next
   allowed quote at 09/12 UTC, simulated 0.8% per-side fee. */
const fs=require("node:fs"),path=require("node:path"),
 crypto=require("node:crypto");
const R2=require("./v20_atlas_r2_shadow");
const Core=require("./v18_kavis_dayaniqlilik");
const START="2023-01-03T06:00:00.000Z",END="2023-01-31T14:00:00.000Z",
 HOUR=3600000,VERSION="V20_R2_JAN2023_HISTORICAL_MID_PROXY_ONLY";
const SPECS=[
 ["RECOVERY_HIST_3H_2020_2022_V1.csv","e19d69fbbf4a825420a07d7e5f678899d1e0f805"],
 ["RECOVERY_HIST_3H_2023_2025_V1.csv","a588b6745f893fcafc935fa486328a6349caa658"]
];
function blobHash(b){
 return crypto.createHash("sha1").update(Buffer.from("blob "+b.length+"\0"))
  .update(b).digest("hex");
}
function parseCSV(buffer){
 const lines=buffer.toString("utf8").trim().split(/\r?\n/);
 if(lines.shift()!=="tt,p,c,r4,r92,r276,dd276,v92,rv,ds,eff,loc,dd4")
  throw Error("JAN23_BAD_CSV_SCHEMA");
 const out=[];
 for(const line of lines){
  const fields=line.split(",");
  if(fields.length!==13)throw Error("JAN23_WRONG_CSV_FIELDS");
  const ts=Date.parse(fields[0]),p=Number(fields[1]);
  if(!Number.isFinite(ts)||!Number.isFinite(p)||p<=0)
    throw Error("JAN23_INVALID_PRICE");
  out.push({tt:fields[0],ts,p});
 }
 for(let i=1;i<out.length;i++)
  if(out[i].ts<=out[i-1].ts)throw Error("JAN23_UNSORTED_SOURCE");
 return out;
}
function loadPinned(){
 const chunks=[],lineage=[];
 for(const [filename,sha] of SPECS){
  const b=fs.readFileSync(path.join(__dirname,"data",filename)),
   normalized=blobHash(b)===sha?b:
    Buffer.from(b.toString("utf8").replace(/\r\n/g,"\n"));
  if(blobHash(normalized)!==sha)throw Error("JAN23_PINNED_SHA_DRIFT:"+filename);
  const rows=parseCSV(normalized);
  chunks.push(rows);
  lineage.push({file:filename,gitBlobSha1:sha,rows:rows.length,
   first:rows[0].tt,last:rows.at(-1).tt});
 }
 if(chunks[0].at(-1).ts>=Date.parse(START)||
    chunks[1][0].tt!==START)throw Error("JAN23_START_COVERAGE_INVALID");
 return {rows:chunks.flat(),lineage};
}
function features(past,ts){
 if(past.length<60)return null;
 const latest=past.at(-1),age=(ts-latest.ts)/HOUR;
 if(latest.ts>=ts)throw Error("JAN23_FUTURE_FEATURE");
 if(age>96)return null;
 const log=i=>Math.log(past[Math.max(0,past.length-1-i)].p);
 const ret=i=>100*(log(i)-log(i+1)),rr=[];
 for(let i=0;i<12;i++)rr.push(ret(i));
 const avg=rr.reduce((a,b)=>a+b,0)/rr.length;
 const rv=Math.sqrt(rr.reduce((a,b)=>a+(b-avg)**2,0)/rr.length);
 const high=Math.max(...past.slice(-50).map(x=>x.p));
 return {at:latest.tt,ageHours:age,price:latest.p,
  market:{r4:ret(0),r1:100*(log(0)-log(3)),
   r3:100*(log(0)-log(8)),rv,
   dd:100*Math.log(latest.p/high)}};
}
function walk(rows){
 const start=Date.parse(START),end=Date.parse(END),
  window=rows.filter(r=>r.ts<end).sort((a,b)=>a.ts-b.ts);
 for(let i=1;i<window.length;i++)
  if(window[i].ts<=window[i-1].ts)throw Error("JAN23_DUPLICATE_TIMESTAMP");
 const s=R2.create({riskMode:"alert",initialCapital:100,
  core:{feePerSide:.008,bankCheckpointHoursUTC:[6,9,12],
    maxIntervalHours:80}});
 const control=Core.create({feePerSide:.008,
    bankCheckpointHoursUTC:[6,9,12],maxIntervalHours:80});
 let prevSignal=null,firstExecutable=null,lastExecutable=null,sourceRows=0,
   priceHistory=[];
 const signals=[],fills=[],trades=[],skips=[];
 for(const row of window){
  if(row.ts<start){priceHistory.push(row);continue;}
  sourceRows++;
  const hour=new Date(row.ts).getUTCHours();
  if([6,9,12].includes(hour)){
   const quote={at:row.tt,price:row.p,bankFeePerSide:.008,
     isBankCheckpoint:true},
    executed=R2.quote(s,quote),baseline=Core.quote(control,quote);
   if(Boolean(executed.fill)!==Boolean(baseline.fill))
     throw Error("JAN23_FILL_MISMATCH_V18");
   if(executed.fill){
    if(!prevSignal||Date.parse(prevSignal)>=row.ts)
      throw Error("JAN23_SAME_BAR_FILL");
    if(executed.fill.suggestedAction!==baseline.fill.suggestedAction)
      throw Error("JAN23_ACTION_MISMATCH_V18");
    if(executed.portfolio.position!==baseline.fill.positionAfter)
      throw Error("JAN23_POSITION_MISMATCH_V18");
    fills.push({timeUTC:row.tt,priceMID:row.p,
      action:executed.fill.suggestedAction,
      position:executed.portfolio.position,
      nav:executed.portfolio.capital,
      learnedIntervals:s.inner.core.learned});
    if(executed.fill.suggestedAction!=="WAIT")
      trades.push({atUTC:row.tt,
        timeTR:new Date(row.ts+3*HOUR).toISOString().slice(0,16)+"+03:00",
        action:executed.fill.suggestedAction,priceMID:row.p,
        feeSide:.008,navAfter:executed.portfolio.capital,
        fromSignal:prevSignal});
    lastExecutable={utc:row.tt,price:row.p};
   }
   if(!firstExecutable&&row.ts>start)
     firstExecutable={utc:row.tt,price:row.p};
   if(hour===6||hour===9){
    const feat=features(priceHistory,row.ts);
    if(!feat){
     skips.push({at:row.tt,reason:"PAST_PRICES_MISSING_OR_STALE"});
    }else{
     const ob={asof:row.tt,featureAvailableAt:feat.at,
       position:s.inner.portfolio.position,market:feat.market,
       events:[],bankFeeQuote:{feePerSide:.008,availableAt:row.tt}};
     const advice=R2.signal(s,ob),reference=Core.signal(control,ob);
     if(advice.action!==reference.action)
       throw Error("JAN23_ALERT_MUST_EQUAL_FROZEN_V18");
     prevSignal=row.tt;
     signals.push({timeUTC:row.tt,
       timeTR:new Date(row.ts+3*HOUR).toISOString().slice(0,16)+"+03:00",
       position:ob.position,action:advice.action,reason:advice.reason,
       qEdge:reference.actionGap,learned:reference.learnedIntervals,
       featureAt:feat.at,featureAgeHours:feat.ageHours,
       market:feat.market,verifiedEconomicEvents:0,
       lastKnownNAV:s.inner.portfolio.nav,noLiveOrders:true});
    }
   }
  }
  // The current price becomes known only after the current decision.
  priceHistory.push(row);
 }
 if(signals[0]?.timeUTC!==START)
   throw Error("JAN23_INITIAL_SIGNAL_NOT_03JAN_09TR");
 if(signals.some(x=>Date.parse(x.featureAt)>=Date.parse(x.timeUTC)))
   throw Error("JAN23_FEATURE_LEAK");
 if(!firstExecutable||!lastExecutable||fills.length<1)
   throw Error("JAN23_NO_FILLS_OR_BENCHMARK");
 const passive=100*.992*.992*lastExecutable.price/firstExecutable.price;
 const byDay={};
 for(const x of signals){
  const day=x.timeUTC.slice(0,10);
  if(!byDay[day])byDay[day]={day,signals:[],trades:[]};
  byDay[day].signals.push({timeTR:x.timeTR,action:x.action,
   reason:x.reason,position:x.position,learned:x.learned});
 }
 for(const x of trades){
  const day=x.atUTC.slice(0,10);
  if(!byDay[day])byDay[day]={day,signals:[],trades:[]};
  byDay[day].trades.push(x);
 }
 return {version:VERSION,
  contract:"REAL_HISTORICAL_GOLD_MID_PROXY_NOT_BANK_BID_ASK",
  startUTC:START,endExclusiveUTC:END,
  startCapitalUSD:100,initialPosition:"CASH",
  endNAVUSD:s.inner.portfolio.nav,
  position:s.inner.portfolio.position,
  cashUSD:s.inner.portfolio.cash,goldUnits:s.inner.portfolio.units,
  maxDrawdownPct:s.inner.portfolio.maxDrawdownPct,
  tradesCount:trades.length,feeDebitedUSD:s.inner.portfolio.feeDollars,
  numberOfSignals:signals.length,numberOfFills:fills.length,
  sourceObservedRows:sourceRows,matured:s.inner.core.learned,
  riskAdvisorOverrides:s.audit.specialistOverrides,
  noEventsValidated:true,noRealBankBidAsk:true,
  benchmarks:{cashUSD:100,passiveGoldAfterTwoFeeLegsUSD:passive,
   firstEligibleFill:firstExecutable,lastEligibleQuote:lastExecutable},
  byDay:Object.values(byDay),trades,signals,fills,skips,
  checkpoint:R2.save(s),frozenV18:Core.save(control)};
}
function run(){
 const input=loadPinned();
 return {...walk(input.rows),dataLineage:input.lineage};
}
if(require.main===module){
 const r=run();
 console.log(JSON.stringify({
  status:r.contract,startUTC:r.startUTC,
  endExclusiveUTC:r.endExclusiveUTC,capital:r.endNAVUSD,
  maxDD:r.maxDrawdownPct,trades:r.tradesCount,
  feeDebited:r.feeDebitedUSD,position:r.position,
  signals:r.numberOfSignals,bankFills:r.numberOfFills,
  learned:r.matured,advisorOverrides:r.riskAdvisorOverrides,
  benchmarks:r.benchmarks,lineage:r.dataLineage,
  tradeLedger:r.trades,days:r.byDay,skipped:r.skips
 },null,2));
}
module.exports={loadPinned,features,walk,run,START,END};