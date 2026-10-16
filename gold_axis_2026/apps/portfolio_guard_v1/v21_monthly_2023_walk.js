#!/usr/bin/env node
"use strict";
/**
 * Forward-chaining V21 monthly learning, not tuning. Default input uses
 * research 3H GOLD price proxy, NOT executable bank BID/ASK. Strict previous
 * complete bar's covariates; quote next checkpoint with modeled fee 0.008.
 * Learner state and cash/units persist across calendar month boundaries.
 */
const fs=require("node:fs"),path=require("node:path"),crypto=require("node:crypto");
const Core=require("./v18_kavis_dayaniqlilik");
const FEE=.008,H=3600000,MONTHS=36,START="2023-01",END="2025-12";
const BANK_UTC=[6,9,12]; // TRT 09 / 12 / 15
function parseCsv(t){
 const rows=t.trim().split(/\r?\n/),header=rows.shift().split(",");
 return rows.filter(Boolean).map((line)=>{
  const v=line.split(",");
  return Object.fromEntries(header.map((k,i)=>[k,v[i]??""]));
 });
}
const num=x=>x===""||x===undefined||x===null?null:Number.isFinite(+x)?+x:null;
const sum=xs=>xs.reduce((a,b)=>a+b,0);
const round=(x,k=6)=>Number(x.toFixed(k));
function hash(x){return crypto.createHash("sha256").update(JSON.stringify(x)).digest("hex");}
function buildRows(gold,market){
 const x=gold.map(g=>{
  const t=Date.parse(g.tt),p=num(g.p),c=num(g.c);
  if(!Number.isFinite(t)||!(p>0)||!(c>0))
   throw Error("V21_INVALID_XAU_ROW");
  return {...g,t,price:c,observed:market.get(g.tt)||null};
 }).sort((a,b)=>a.t-b.t);
 for(let i=1;i<x.length;i++)if(x[i].t<=x[i-1].t)
  throw Error("V21_DUPLICATED_OR_UNSORTED_PRICE");
 return x;
}
function inputFeatures(prev,decisionT,variant){
 if(prev.t>=decisionT)throw Error("V21_CURRENT_BAR_LEAK");
 // Research panel is timestamped and may have 3h completion lag.
 if(decisionT-prev.t<3*H)throw Error("V21_BAR_NOT_MATURED");
 const q={r4:num(prev.r4),r1:num(prev.r92),r3:num(prev.r276),
  rv:num(prev.rv),dd:num(prev.dd276)};
 if([q.r4,q.r1,q.r3,q.rv,q.dd].some(x=>x===null))
  throw Error("V21_MISSING_PRICE_FEATURE");
 if(variant==="crossmarket"){
  const m=prev.observed;
  // As-of crossmarket records must be anchored to previous bar only.
  if(m){
   const age=num(m.age_nq),v=num(m.nq6);
   if(age!==null&&age>=1&&age<=12&&v!==null)q.nq6=v;
  }
 }
 return q;
}
function newAgent(variant){
 return {variant,engine:Core.create({feePerSide:FEE,maxIntervalHours:80,
  bankCheckpointHoursUTC:BANK_UTC,minimumMaturedIntervals:12}),
  position:"CASH",cash:100,units:0,peak:100,maxDD:0,trades:0,fees:0,
  grossGain:0,monthStartCapital:100,monthActions:[],lastNAV:100,
  signals:0,featuresPresent:0,featuresMissing:0};
}
function nav(s,price){return s.cash+s.units*price*(1-FEE);}
function settle(s,action,price){
 if(action==="BUY"){
  if(s.position!=="CASH")throw Error("V21_DOUBLE_BUY");
  s.fees+=s.cash*FEE;
  s.units=s.cash*(1-FEE)/price;s.cash=0;s.position="GOLD";s.trades++;
 }else if(action==="SELL"){
  if(s.position!=="GOLD")throw Error("V21_DOUBLE_SELL");
  const gross=s.units*price;s.fees+=gross*FEE;
  s.cash=gross*(1-FEE);s.units=0;s.position="CASH";s.trades++;
 }else if(action!=="WAIT")throw Error("V21_BAD_ACTION");
 const n=nav(s,price);
 s.peak=Math.max(s.peak,n);s.maxDD=Math.max(s.maxDD,100*(1-n/s.peak));
 s.lastNAV=n;
 return n;
}
function compatible(obs,cfg){
 if(obs.t< Date.parse("2023-01-01")||obs.t>=Date.parse("2026-01-01"))return false;
 const d=new Date(obs.t),h=d.getUTCHours(),dow=d.getUTCDay();
 return dow>0&&dow<6&&BANK_UTC.includes(h);
}
function replay(gold,cross,opts={}){
 const crossMap=new Map(cross.map(x=>[x.tt,x]));
 const rows=buildRows(gold,crossMap),agents=[newAgent("price_only"),newAgent("crossmarket")];
 let currentMonth=null,monthly=[],eligible=0,firstEntryPrice=null,finalPrice=null,
  skippedNoMature=0;
 function closeMonth(){
  if(!currentMonth)return;
  const report={month:currentMonth,eligibleCheckpoints:eligible,
   agents:Object.fromEntries(agents.map(s=>[s.variant,{
    startNAV:round(s.monthStartCapital),endNAV:round(s.lastNAV),
    netReturnPct:round(100*(s.lastNAV/s.monthStartCapital-1)),
    totalMaxDrawdownPct:round(s.maxDD),totalTrades:s.trades,
    monthTrades:s.monthActions.length,monthActions:s.monthActions,
    totalFeeDollars:round(s.fees),learnedIntervals:s.engine.learned,
    nqFeatureAvailable:s.featuresPresent,nqFeatureMissing:s.featuresMissing,
    endPosition:s.position,stateSHA256:hash({engine:Core.save(s.engine),
      cash:s.cash,units:s.units,position:s.position,peak:s.peak})}]))};
  monthly.push(report);eligible=0;
  for(const s of agents){s.monthActions=[];s.monthStartCapital=s.lastNAV;
   s.featuresPresent=0;s.featuresMissing=0;}
 }
 for(let i=1;i<rows.length;i++){
  const r=rows[i],prev=rows[i-1],month=r.tt.slice(0,7);
  if(month<START||month>END)continue;
  if(month!==currentMonth){closeMonth();currentMonth=month;}
  if(!compatible(r))continue;
  if(r.t-prev.t<3*H){skippedNoMature++;continue;}
  const ft=new Date(r.t).toISOString(),quoteAt=new Date(r.t+60000).toISOString();
  // Accept only complete prior features that did not originate in present interval
  for(const s of agents){
   const features=inputFeatures(prev,r.t,s.variant);
   const obs={asof:ft,featureAvailableAt:ft,position:s.position,
    market:features,bankFeeQuote:{feePerSide:FEE,availableAt:ft}};
   const signal=Core.signal(s.engine,obs);
   const q=Core.quote(s.engine,{at:quoteAt,price:r.price,
     isBankCheckpoint:true,bankFeePerSide:FEE});
   if(!q.fill||q.fill.suggestedAction!==signal.action)throw Error("V21_INVALID_FILL");
   if(s.variant==="crossmarket"){
    if(features.nq6!==undefined)s.featuresPresent++;
    else s.featuresMissing++;
   }
   const n=settle(s,signal.action,r.price);s.signals++;
   if(signal.action!=="WAIT")s.monthActions.push({
    asof:ft,tr:new Date(r.t+3*H).toISOString().slice(0,16).replace("T"," "),
    action:signal.action,quoteProxy:round(r.price,3),
    feePerSide:FEE,nav:round(n),
    learnedIntervals:signal.learnedIntervals,
    decisionScorePct:round(signal.actionGap,5),
    rawScorePct:round(signal.rawAdvantage,5)});
  }
  eligible++;if(firstEntryPrice===null)firstEntryPrice=r.price;
  finalPrice=r.price;
 }
 closeMonth();
 const cost=FEE;
 const summary={
  status:"RETROSPECTIVE_3H_PRICE_PROXY_NO_REAL_BANK_ASK_BID_NOT_BLIND",
  feePerSide:FEE,monthCount:monthly.length,
  completedMonths:monthly.map(m=>m.month),
  skippedWithoutMaturePreviousBar:skippedNoMature,
  priceRows:rows.length,crossRows:cross.length,
  eligiblePoints:monthly.reduce((a,b)=>a+b.eligibleCheckpoints,0),
  cashBaseline:100,
  passiveBuyHoldFinal:firstEntryPrice&&finalPrice?
    round(100*(1-cost)**2*finalPrice/firstEntryPrice):null,
  agents:Object.fromEntries(agents.map(s=>[s.variant,{
    endingNAV:round(s.lastNAV),totalTrades:s.trades,totalFees:round(s.fees),
    maxDDPct:round(s.maxDD),lastPosition:s.position,
    learnedIntervals:s.engine.learned,finalStateSHA256:hash(Core.save(s.engine))}])),
  monthly};
 if(opts.emitSnapshotsDir){
  fs.mkdirSync(opts.emitSnapshotsDir,{recursive:true});
  // Continuity checkpoints are written by same process; no data in the filenames.
  fs.writeFileSync(path.join(opts.emitSnapshotsDir,"V21_FINAL_LEARNED_STATE.json"),
   JSON.stringify({endMonth:currentMonth,agents:agents.map(s=>({
    variant:s.variant,engine:Core.save(s.engine),cash:s.cash,
    units:s.units,position:s.position,peak:s.peak,
    maxDD:s.maxDD,fees:s.fees,trades:s.trades,lastNAV:s.lastNAV}))},null,2));
 }
 return summary;
}
if(require.main===module){
 const [panel,cross,out,snapshots]=process.argv.slice(2);
 if(!panel||!cross||!out)throw Error("usage: node v21_monthly_2023_walk.js gold3h.csv cross3h.csv output.json [state_dir]");
 const report=replay(parseCsv(fs.readFileSync(panel,"utf8")),
  parseCsv(fs.readFileSync(cross,"utf8")),{emitSnapshotsDir:snapshots});
 fs.writeFileSync(out,JSON.stringify(report,null,2));
 console.log(JSON.stringify({status:report.status,months:report.monthCount,
  points:report.eligiblePoints,passive:report.passiveBuyHoldFinal,
  end:report.agents,output:out},null,2));
}
module.exports={parseCsv,buildRows,inputFeatures,replay,settle};
