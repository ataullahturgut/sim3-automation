"use strict";
/**
 * Version-locked sequential JAN -> FEB 2026 replay.
 *
 * February starts in Jan's exact terminal portfolio state. Frozen V1
 * mechanical rules unchanged; event-analog V1 remains uncalibrated.
 * No Feb outcome, macro headline or forward labels may enter any choice.
 * Same source + seed + rules => identical result.
 */
const fs=require("node:fs");
const path=require("node:path");
const core=require("./engine");
const ROOT=path.resolve(__dirname,"../../..");
const FEB=Object.freeze({path:"gold_axis_2026/apps/portfolio_guard_v1/data/FEB_2026_V1_ASOF_PANEL.csv",blob:"8e3bb94acc3d38d12778439115292388b295734f"});
const ORIGIN=Date.parse("2026-01-31T21:00:00.000Z"); // 2026-02-01 00:00 TRT
const END=Date.parse("2026-02-28T21:00:00.000Z"); // 2026-03-01 00:00 TRT
const M15=15*60*1000,FEE=0.008;
const CLOCK=new Intl.DateTimeFormat("sv-SE",{timeZone:"Europe/Istanbul",year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit",hour12:false});
function loadFebruary(){
 const raw=fs.readFileSync(path.join(ROOT,FEB.path));
 const decoded=core.decodePinnedSource(FEB,raw);
 const rows=decoded.rows.map(row=>{
  const r={tt:row.tt,time:Date.parse(row.tt)};
  for(const [key,value]of Object.entries(row)){if(key!=="tt")r[key]=value===""?null:Number(value);}
  if(!Number.isFinite(r.time)||!Number.isFinite(r.p)||!Number.isFinite(r.c))throw Error("FEBRUARY_PANEL_INVALID_PRICE");
  return r;
 });
 if(rows.length!==1723||
    rows[0].tt!=="2026-02-02T03:45:00.000Z"||
    rows.at(-1).tt!=="2026-02-27T21:30:00.000Z")throw Error("FEBRUARY_FROZEN_PANEL_SHAPE_CHANGED");
 for(let i=1;i<rows.length;i++){
  if(rows[i].time<=rows[i-1].time)throw Error("FEBRUARY_PANEL_TIME_NOT_STRICT");
  if(rows[i].time<ORIGIN||rows[i].time>=END)throw Error("FEBRUARY_ROW_OUTSIDE_CALENDAR");
 }
 return {rows,blob:FEB.blob,checksumVerified:true};
}
function simulateFebruary(data,mode,openingCash){
 if(!["event15m","price15m","legacy3h"].includes(mode))throw Error("UNSUPPORTED_FEB_MODEL");
 if(!(openingCash>0)&&Number.isFinite(openingCash))throw Error("INVALID_OPENING_CASH");
 const {rows}=data,byTime=new Map(rows.map(r=>[r.time,r]));
 let cash=openingCash,gold=0,peak=0,lastSell=-Infinity,lastClose=null;
 let maxSeen=openingCash,maxDD=0,checks=0;
 const actions=[],ledger=[];
 const historical=core.loadFrozen().events;
 for(let t=ORIGIN;t<END;t+=M15){
  const row=byTime.get(t);
  const local=CLOCK.format(new Date(t));
  let action=gold?"HOLD_GOLD":"HOLD_CASH",reason="MARKET_CLOSED_OR_NO_COMPLETE_ASOF_BAR",phase="NO_NEW_BAR";
  let riskScore=null,distance=null,nearestCases=null;
  if(row){
   lastClose=row.c;
   const isDecision=mode!=="legacy3h"||(new Date(t).getUTCMinutes()===0&&new Date(t).getUTCHours()%3===0);
   if(isDecision){
    checks++;phase="PRICE_STATE_NO_VERIFIED_FEB_NEWS_CAUSALITY";
    if(mode==="event15m"){
     const v=core.analog(row,historical);
     riskScore=v.riskScore;distance=v.distance;nearestCases=v.nearest;
     if(v.distance>=1&&row.rv>=.8)phase="OUT_OF_DISTRIBUTION_CAUSE_UNRESOLVED";
    }
    if(gold){
     peak=Math.max(peak,row.c);
     const trail=100*(row.c/peak-1);
     let why=null;
     if(mode==="event15m"){
      const joint=row.r4<=-1&&row.nq6!==null&&row.nq6<=-1;
      const novelty=distance>=1&&row.rv>=.8;
      if(joint&&(riskScore>=.2||novelty))why="CROSS_MARKET_UNKNOWN_SHOCK";
      else if(row.r4<=-2&&row.rv>=1.2&&distance>=1)why="UNFAMILIAR_PRICE_SHOCK";
     }
     if(!why)why=trail<=-3.5?"TRAILING_DRAWDOWN":
      row.r4<=-2?"FAST_PRICE_DROP":
      row.r92<=-2&&row.r4<0?"MEDIUM_TREND_DOWN":
      row.r276<-2&&row.r4<-.5?"LONGER_TREND_DOWN":null;
     if(why){
      cash=gold*row.p*(1-FEE);gold=0;peak=0;lastSell=t;
      action="SELL_TO_CASH";reason=why;
      actions.push({utc:row.tt,tr:local,action,price:row.p,cashAfter:cash,reason,phase,riskScore,nearestDistance:distance,nearestCases});
     }else reason="NO_CONFIRMED_LARGE_DOWN";
    }else{
     const entry=row.r92>=1&&row.r276>=0&&row.r4>=-.25&&row.dd276>=-3.5&&row.v92<=4;
     if(entry&&t-lastSell>=12*3600*1000){
      gold=cash*(1-FEE)/row.p;cash=0;peak=row.p;
      action="BUY_GOLD";reason="FROZEN_FIVE_PRICE_QUESTIONS";
      actions.push({utc:row.tt,tr:local,action,price:row.p,ounces:gold,reason,phase,riskScore,nearestDistance:distance,nearestCases});
     }else reason="WAIT_NO_CONFIRMED_UP";
    }
   }else{reason="THREE_HOUR_SCHEDULE_WAIT";phase="PRICE_NO_DECISION_THIS_SLOT";}
  }
  const nav=gold&&lastClose!==null?gold*lastClose*(1-FEE):cash;
  maxSeen=Math.max(maxSeen,nav);maxDD=Math.max(maxDD,100*(1-nav/maxSeen));
  ledger.push({utc:new Date(t).toISOString(),turkey:local,hasNewBar:!!row,action,reason,
    phase,macroWindow:"NOT_VALIDATED",riskScore,caseDistance:distance,
    position:gold?"GOLD":"CASH",goldOunces:gold,cashUSD:cash,nav:Math.round(nav*10000)/10000});
 }
 const final=gold?gold*rows.at(-1).c*(1-FEE):cash;
 const first=rows[0].p,last=rows.at(-1).c;
 const hold=openingCash*(1-FEE)/first*last*(1-FEE);
 const days=[];
 for(let date=1;date<=28;date++){
  const label="2026-02-"+String(date).padStart(2,"0");
  const day=ledger.filter(x=>x.turkey.slice(0,10)===label);
  const lastItem=day.at(-1);
  if(!lastItem)throw Error("MISSING_FEB_CALENDAR_DAY_"+label);
  days.push({date:label,position:lastItem.position,netValue:lastItem.nav,
   completeBars:day.filter(x=>x.hasNewBar).length,
   actions:day.filter(x=>x.action==="BUY_GOLD"||x.action==="SELL_TO_CASH")
     .map(x=>({when:x.turkey.slice(11),action:x.action})),
   macroWindows:[]});
 }
 return {
  model:mode,version:"GOLD_GUARD_FEB2026_V1_FROZEN_FROM_JAN",
  period:"Şubat 2026",
  startUSD:openingCash,finalUSD:final,returnPct:100*(final/openingCash-1),
  cumulativeFrom100Pct:final-100,
  maxDrawdownPct:maxDD,benchmarkBuyHoldUSD:hold,
  benchmarkNote:"Şubat ilk uygun tamamlanmış veri anında AL ve son fiyatla tasfiye senaryosu",
  terminalAsset:gold?"GOLD":"CASH",goldOunces:gold,cashUSD:cash,
  markToMarketBeforeHypotheticalSale:gold?gold*last:cash,
  hypotheticalExitFeeDeducted:gold>0,
  checks,fullCalendarSlots:ledger.length,completePriceBars:rows.length,
  archiveCases:historical.length,actions,days,ledger
 };
}
function runFebruary(){
 const jan=core.runAll().scenarios;
 const start=jan.event15m.finalUSD;
 if(jan.event15m.terminalAsset!=="CASH"||Math.abs(start-119.7539172)>1e-5)
  throw Error("JANUARY_TERMINAL_STATE_NOT_FROZEN");
 const data=loadFebruary();
 const scenarios=Object.fromEntries(["event15m","price15m","legacy3h"]
  .map(mode=>[mode,simulateFebruary(data,mode,start)]));
 if(scenarios.event15m.fullCalendarSlots!==2688||
    scenarios.price15m.fullCalendarSlots!==2688)throw Error("FEB_CALENDAR_SLOT_CONTRACT_CHANGED");
 return {
  month:"2026-02",version:"GOLD_GUARD_FEB2026_V1_FROZEN_FROM_JAN",
  status:"RESEARCH_ONLY_NOT_LIVE",
  inputBalanceSource:"2026-01 frozen event15m terminal CASH 119.753917 USD",
  dataHashes:{...core.runAll().inputs,february: {gitBlob:data.blob,path:FEB.path}},
  bankSpreadIncluded:false,commissionPerSide:FEE,
  economicCausalityProven:false,independentOutOfSample:false,
  feedbackModelChangeSinceJanuary:false,
  comparison:["legacy3h","price15m","event15m"].map(x=>{
   const a=scenarios[x];return {...a,ledger:undefined};
  }),
  incrementalDNABenefitUSD:scenarios.event15m.finalUSD-scenarios.price15m.finalUSD,
  scenarios
 };
}
module.exports={FEB,loadFebruary,simulateFebruary,runFebruary};
