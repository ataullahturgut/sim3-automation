#!/usr/bin/env node
"use strict";
/**
 * January 2026 retrospective replay using OWNED PRIVATE H1 vendor data.
 * Requires externally exported CSV; do NOT commit raw bank/vendor rows
 * to this PUBLIC repo. NO queries or live market/orders in this module.
 *
 * node jan2026_h1_fee008_replay.js /private/location/dukascopy_h1.csv
 * csv schema: utc,bid_open,bid_close,ask_open,ask_close,source_vintage
 *
 * Fee per side 0.008, simulated midpoint execution, NOT actual user bank BID/ASK.
 * Signal at current H1 OPEN uses ONLY PREVIOUS completed H1 bar features.
 * Fill assumed at H1 OPEN + one minute at unchanged OPEN midpoint. This is
 * optimistic execution approximation; not actual timestamped bank quote.
 */
const fs=require("fs");
const Core=require("./v18_kavis_dayaniqlilik");
const R2=require("./v20_atlas_r2_shadow");
const R3=require("./v20_atlas_r3_gate");
const FEE=.008, THRESHOLD=1.9;
const BANK_HOURS_UTC=[6,7,8,9,10,11,12,13];
const SOURCE="RETRIEVED_2026_10_08_NOT_PIT";
const validNumber=x=>Number.isFinite(x)&&x>0;
function csv(raw){
 const lines=raw.trim().split(/\r?\n/),h=lines.shift().split(",");
 for(const col of ["utc","bid_open","bid_close","ask_open","ask_close","source_vintage"])
  if(!h.includes(col))throw Error("MISSING_H1_FIELD_"+col);
 const a=lines.filter(Boolean).map(l=>{
  const v=l.split(","),o=Object.fromEntries(h.map((c,i)=>[c,v[i]]));
  const x={utc:o.utc,source_vintage:o.source_vintage,t:Date.parse(o.utc),
   bid_open:+o.bid_open,bid_close:+o.bid_close,
   ask_open:+o.ask_open,ask_close:+o.ask_close};
  if(!validNumber(x.bid_open)||!validNumber(x.bid_close)||
    !validNumber(x.ask_open)||!validNumber(x.ask_close)||
    x.ask_open<x.bid_open||x.ask_close<x.bid_close||
    !Number.isFinite(x.t)||x.source_vintage!==SOURCE)
   throw Error("INVALID_SOURCE_H1_ROW");
  x.midO=(x.bid_open+x.ask_open)/2;
  x.midC=(x.bid_close+x.ask_close)/2;
  return x;
 });
 for(let i=1;i<a.length;i++)if(a[i].t-a[i-1].t!==3600000)
  throw Error("GAP_OR_DUPLICATE_IN_SOURCE_H1");
 return a;
}
function fmt(x){return Math.round(x*1e6)/1e6;}
function run(rows){
 if(rows.length<700)throw Error("INSUFFICIENT_PRIOR_H1_HISTORY");
 const mid=i=>rows[i].midC;
 const pct=(i,j)=>100*Math.log(mid(i)/mid(j));
 function market(i){
  const last=i-1,ret=[];
  for(let j=last-11;j<=last;j++)ret.push(pct(j,j-1));
  const avg=ret.reduce((x,y)=>x+y,0)/ret.length;
  const high=Math.max(...rows.slice(Math.max(0,last-48),last+1).map(z=>z.midC));
  return {r4:pct(last,last-4),r1:pct(last,last-1),r3:pct(last,last-3),
   rv:Math.sqrt(ret.reduce((x,y)=>x+(y-avg)**2,0)/ret.length),
   dd:100*Math.log(mid(last)/high)};
 }
 const ids=[];
 for(let i=49;i<rows.length;i++){
  const z=rows[i],d=new Date(z.t),w=d.getUTCDay(),h=d.getUTCHours();
  if(z.utc.slice(0,7)!=="2026-01"||z.utc.slice(0,10)==="2026-01-01"||
   w===0||w===6||!BANK_HOURS_UTC.includes(h))continue;
  ids.push(i);
 }
 if(ids.length<80)throw Error("INSUFFICIENT_BANK_HOURS");
 const options={initialCapital:100,
  core:{feePerSide:FEE,bankCheckpointHoursUTC:BANK_HOURS_UTC,maxIntervalHours:80}};
 const models={
  V18:{mod:Core,engine:Core.create(options.core),cash:100,units:0,peak:100,mdd:0,trades:[]},
  R2:{mod:R2,engine:R2.create({...options,riskMode:"soft_penalty",maxDrawdownPct:15}),trades:[]},
  R3:{mod:R3,engine:R3.create({...options,riskMode:"alert",shadowGate:"gated",gateThreshold:THRESHOLD}),trades:[]}
 };
 for(const i of ids){
  const row=rows[i],asof=new Date(row.t).toISOString(),
   quoteAt=new Date(row.t+60000).toISOString(),
   m=market(i),midQuote=row.midO;
  for(const name of Object.keys(models)){
   const s=models[name],position=name==="V18"?(s.units>0?"GOLD":"CASH"):
    s.engine.inner.portfolio.position;
   const result=s.mod.signal(s.engine,{asof,featureAvailableAt:asof,
    position,market:m,
    bankFeeQuote:{feePerSide:FEE,availableAt:asof}});
   const q=s.mod.quote(s.engine,{at:quoteAt,price:midQuote,
    isBankCheckpoint:true,bankFeePerSide:FEE});
   if(!q.fill)throw Error("FAILED_BANK_CHECKPOINT_"+asof);
   if(result.ordersSent!==undefined&&result.ordersSent!==0||
     q.ordersSent!==0)throw Error("LIVE_ORDER_PROHIBITED");
   if(name==="V18"){
    if(q.fill.suggestedAction==="BUY"){
      s.units=s.cash*(1-FEE)/midQuote;s.cash=0;
    }else if(q.fill.suggestedAction==="SELL"){
      s.cash=s.units*midQuote*(1-FEE);s.units=0;
    }
    s.nav=s.cash+s.units*midQuote*(1-FEE);
    s.peak=Math.max(s.peak,s.nav);
    s.mdd=Math.max(s.mdd,100*(1-s.nav/s.peak));
   }else{
    s.nav=q.portfolio.capital;
    s.mdd=s.engine.inner.portfolio.maxDrawdownPct;
   }
   if(result.action!=="WAIT")s.trades.push({
     utc:asof,localTR:new Date(row.t+3*3600000).toISOString().slice(0,16).replace("T"," "),
     action:result.action,mid:fmt(midQuote),
     effectiveBuyPrice:fmt(midQuote/(1-FEE)),
     effectiveSellPrice:fmt(midQuote*(1-FEE)),navAfter:fmt(s.nav),
     reason:result.reason||(result.readiness?"V18_LEARNED":"V18_WARMUP")});
  }
 }
 const modelsResult={};
 for(const [name,s] of Object.entries(models)){
  const portfolio=name==="V18"?null:s.engine.inner.portfolio;
  modelsResult[name]={capital:fmt(name==="V18"?s.nav:portfolio.nav),
    maxDDPct:fmt(name==="V18"?s.mdd:portfolio.maxDrawdownPct),
    position:name==="V18"?(s.units>0?"GOLD":"CASH"):portfolio.position,
    learnedIntervals:name==="V18"?s.engine.learned:s.engine.inner.core.learned,
    tradeCount:s.trades.length,actions:s.trades,
    adviserInterventions:name==="R2"?s.engine.audit.specialistOverrides:
     name==="R3"?s.engine.audit.specialistOverrides:0};
 }
 const first=rows[ids[0]],last=rows[ids.at(-1)];
 return {status:"REAL_VENDOR_H1_RETROSPECTIVE_NO_BANK_QUOTES_NOT_PIT_NOT_OOS",
  source:{vintage:SOURCE,privateNeonRawUnpublished:true,h1Rows:rows.length,
   januaryRows:rows.filter(r=>r.utc.startsWith("2026-01")).length,
   eligibleHours:ids.length,first:first.utc,last:last.utc,
   bankFeePerSide:FEE,estimatedBankBuySellViaMidpoint:true,
   vendorBidAskUsedForMidpoint:true,
   noAdditionalVendorSpreadCharge:true,
   signalBasedOnPriorCompletedH1:true,
   assumedExecutionDelayMinutes:1},
  models:modelsResult,
  benchmarks:{cash:100,buyHold:fmt(100*(1-FEE)**2*last.midO/first.midO),
   firstObservedMid:fmt(first.midO),lastObservedMid:fmt(last.midO)}};
}
if(require.main===module){
 if(process.argv.length!==3)throw Error("PRIVATE_VENDOR_CSV_ARG_REQUIRED");
 const r=run(csv(fs.readFileSync(process.argv[2],"utf8")));
 console.log(JSON.stringify(r,null,2));
}
module.exports={csv,run};
