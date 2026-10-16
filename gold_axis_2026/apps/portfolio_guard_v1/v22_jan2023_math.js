#!/usr/bin/env node
"use strict";
/** V22 January 2023 ONLY: original adaptive mathematical decision engine.
 * No other markets, event rules, future outcomes, or hand-optimized January thresholds.
 * Price-only causal multi-horizon online prediction, AdaGrad and Hedge feedback.
 */
const fs=require("node:fs"),path=require("node:path");
const HORIZONS=[1,4,16,64],STEP=.004,ETA=.25,FEE=.008,BAR_MS=900000;
const START=Date.parse("2023-01-01T00:00:00Z"),END=Date.parse("2023-02-01T00:00:00Z");
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const round=(v,n=6)=>Number(v.toFixed(n));
function parseCsv(s){
 const a=s.trim().split(/\r?\n/),h=a.shift().split(",");
 for(const k of ["tt","close","p"])if(!h.includes(k))throw Error("V22_MISSING_"+k);
 return a.filter(Boolean).map(line=>{
  const r=line.split(","),x=Object.fromEntries(h.map((k,i)=>[k,r[i]??""]));
  const t=Date.parse(x.tt),close=+x.close,open=+x.p;
  if(!Number.isFinite(t)||!(close>0)||!(open>0))
   throw Error("V22_INVALID_SOURCE_ROW");
  return {t,tt:x.tt,close,open};
 });
}
function contig(a,start,end){
 if(start<0||end>=a.length||start>end)return false;
 return a[end].t-a[start].t===(end-start)*BAR_MS;
}
function vector(a,i){
 if(i<64||!contig(a,i-64,i))return null;
 const price=j=>a[j].close;
 const ret=(j,k)=>100*Math.log(price(j)/price(k));
 const changes=[];for(let j=i-15;j<=i;j++)changes.push(ret(j,j-1));
 const mean=changes.reduce((x,y)=>x+y,0)/changes.length;
 const stdev=Math.sqrt(changes.reduce((x,y)=>x+(y-mean)**2,0)/changes.length);
 const hi=Math.max(...a.slice(i-63,i+1).map(z=>z.close));
 return [1,clamp(ret(i,i-1)/.5,-3,3),
  clamp(ret(i,i-4)/1,-3,3),
  clamp(ret(i,i-16)/2,-3,3),
  clamp(ret(i,i-64)/4,-3,3),
  clamp(stdev/.5,0,3),
  clamp((100*Math.log(price(i)/hi))/3,-3,0),
  clamp((ret(i,i-4)/4-ret(i,i-16)/16)/.1,-3,3)];
}
const dot=(a,b)=>a.reduce((s,v,i)=>s+v*b[i],0);
function head(h){
 return {h,w:Array(8).fill(0),acc:Array(8).fill(.001),
  n:0,loss:1,bias:0,var:1,MAE:0,MSE:0,
  maxAbsWeight:0,updates:0};
}
function create(){
 return {initial:100,cash:100,units:0,pos:"CASH",peak:100,mdd:0,
  fees:0,trades:[],lastTradeIndex:-Infinity,metaWeights:[.25,.25,.25,.25],
  heads:HORIZONS.map(head),pending:HORIZONS.map(()=>[]),
  totalTargets:0,totalNonzeroUpdates:0,decisions:[],learning:[],
  dayStats:{},totalBarObservations:0};
}
function mature(s,a,i){
 const price=a[i].close;
 for(let j=0;j<HORIZONS.length;j++){
  const h=HORIZONS[j],queue=s.pending[j],e=queue.length?queue[0]:null;
  // Entries ordered; for one appended each observation.
  while(queue.length&&queue[0].due<=i){
   const task=queue.shift();
   if(task.due!==i||!contig(a,task.start,i))continue;
   const y=clamp(100*Math.log(price/task.originPrice),-12,12);
   const hd=s.heads[j],err=clamp(task.pred-y,-25,25);
   const n0=hd.n,loss=Math.min(16,(err*err)/(1+y*y));
   const gradScale=2*err/(1+dot(task.x,task.x));
   let nonzero=false;
   for(let k=0;k<hd.w.length;k++){
    const g=clamp(gradScale*task.x[k]+.001*hd.w[k],-50,50);
    hd.acc[k]=Math.min(1e6,hd.acc[k]+g*g);
    const before=hd.w[k];
    hd.w[k]=clamp(hd.w[k]-STEP*g/Math.sqrt(hd.acc[k]),-25,25);
    if(Math.abs(hd.w[k]-before)>1e-14)nonzero=true;
   }
   hd.bias=.9*hd.bias+.1*(y-task.pred);
   hd.var=.9*hd.var+.1*(err*err);
   hd.loss=n0===0?loss:.92*hd.loss+.08*loss;
   hd.MAE=(hd.MAE*n0+Math.abs(err))/(n0+1);
   hd.MSE=(hd.MSE*n0+err*err)/(n0+1);
   hd.n++;hd.updates++;s.totalTargets++;
   if(nonzero)s.totalNonzeroUpdates++;
   hd.maxAbsWeight=Math.max(hd.maxAbsWeight,...hd.w.map(Math.abs));
  }
 }
 const avail=s.heads.map(h=>h.n>=8);
 // Hedge based only on already-matured prediction errors.
 const raw=s.heads.map((hd,j)=>avail[j]?Math.exp(-ETA*hd.loss):0);
 const den=raw.reduce((x,y)=>x+y,0);
 s.metaWeights=den>0?raw.map(x=>x/den):[.25,.25,.25,.25];
}
function score(s,x){
 const active=s.heads.filter(h=>h.n>=8);
 if(active.length===0)return {ready:false,edge:0,risk:0,
  predicts:s.heads.map(h=>({h:h.h,n:h.n,mu:null}))};
 const predicts=s.heads.map((h,i)=>({
   h:h.h,n:h.n,weight:s.metaWeights[i],
   mu:clamp(dot(h.w,x)+h.bias,-15,15),
   uncertainty:Math.sqrt(Math.max(.0001,h.var))
 }));
 const edge=predicts.reduce((tot,p)=>{
  return tot+(p.n>=8?p.weight*p.mu:0);
 },0);
 const risk=predicts.reduce((tot,p)=>{
  return tot+(p.n>=8?p.weight*.25*p.uncertainty:0);
 },0);
 return {ready:true,edge,risk,predicts};
}
function localTr(t){return new Date(t+3*3600000).toISOString().slice(0,16).replace("T"," ");}
function bankWindow(t){const d=new Date(t),h=d.getUTCHours(),weekday=d.getUTCDay();
 return weekday>=1&&weekday<=5&&h>=6&&h<14; }
function nav(s,px){return s.cash+s.units*px*(1-FEE);}
function execute(s,act,open,index,sig){
 if(!["BUY","SELL"].includes(act))throw Error("V22_WRONG_ACTION");
 if(act==="BUY"){
  if(s.pos!=="CASH")throw Error("V22_DOUBLE_BUY");
  s.fees+=s.cash*FEE;
  s.units=s.cash*(1-FEE)/open;s.cash=0;s.pos="GOLD";
 }else{
  if(s.pos!=="GOLD")throw Error("V22_DOUBLE_SELL");
  const gross=s.units*open;
  s.fees+=gross*FEE;
  s.cash=gross*(1-FEE);s.units=0;s.pos="CASH";
 }
 s.lastTradeIndex=index;
 const d={timeUTC:new Date(sig.t).toISOString(),timeTR:localTr(sig.t),
  action:act,proxyOpen:round(open,3),
  effectivePrice:round(act==="BUY"?open/(1-FEE):open*(1-FEE),4),
  score:round(sig.edge),uncertainty:round(sig.risk),
  totalTargets:s.totalTargets,navAfter:round(nav(s,open)),
  sideFeeRate:FEE};
 s.trades.push(d);return d;
}
function forward(a,opts={}){
 if(!Array.isArray(a)||a.length<66)throw Error("V22_NEED_ENOUGH_JAN_ROWS");
 for(let i=1;i<a.length;i++)if(a[i].t<=a[i-1].t)
  throw Error("V22_UNSORTED_OR_DUPLICATE");
 if(a.some(z=>z.t<START||z.t>=END+BAR_MS))
  throw Error("V22_OUTSIDE_JAN_2023");
 const s=create(),daily={},eligible=[],firstEligibleOpen=null;
 for(let i=0;i<a.length;i++){
  const row=a[i],x=vector(a,i);
  // Only mature predictions from earlier observations once outcome is known.
  mature(s,a,i);s.totalBarObservations++;
  const beforeWeights=s.heads.map(h=>h.w.slice());
  const sc=x?score(s,x):{ready:false,edge:0,risk:0,predicts:[]};
  const day=localTr(row.t-BAR_MS).slice(0,10);
  const stat=daily[day]??={observations:0,scoreReady:0,targets:0,actions:0,
   startWeights:s.heads.map(h=>h.w.slice()),endWeights:null,mae:null,
   endNAV:100,position:"CASH",exposures:0};
  stat.observations++;if(sc.ready)stat.scoreReady++;
  let action="WAIT",filled=null;
  // The NEXT row's open is an actual unknown at signal time.
  // Only after storing action do we simulate next-bar fill with p.
  const canAct=bankWindow(row.t)&&
   i+1<a.length&&a[i+1].t-row.t===BAR_MS&&
   bankWindow(a[i+1].t)&&row.t<END&&sc.ready;
  if(firstEligibleOpen===null&&bankWindow(row.t)&&
    i+1<a.length&&a[i+1].t-row.t===BAR_MS&&bankWindow(a[i+1].t))
    firstEligibleOpen=a[i+1].open;
  if(canAct&&i-s.lastTradeIndex>=16){
    if(s.pos==="CASH"&&sc.edge-sc.risk>100*(-Math.log(1-FEE)*2))
      action="BUY";
    else if(s.pos==="GOLD"&& -sc.edge-sc.risk>100*(-Math.log(1-FEE)*2))
      action="SELL";
  }
  // Train on next bar ONLY on subsequent loop, never here.
  if(canAct){
   const d={asof:row.tt,tr:localTr(row.t),positionBefore:s.pos,action,
     edge:round(sc.edge),risk:round(sc.risk),
     cutoffPct:round(100*(-Math.log(1-FEE)*2)),
     nTargets:s.totalTargets,
     metaWeights:s.metaWeights.map(x=>round(x,4)),
     forecasts:sc.predicts.map(p=>({
      horizonBars:p.h,mu:round(p.mu),n:p.n,weight:round(p.weight,4)}))};
   s.decisions.push(d);eligible.push(d);
   if(action!=="WAIT"){
     filled=execute(s,action,a[i+1].open,i,{t:row.t,edge:sc.edge,risk:sc.risk});
     stat.actions++;
   }
  }
  if(x)for(let j=0;j<HORIZONS.length;j++)
   s.pending[j].push({start:i,due:i+HORIZONS[j],
    originPrice:row.close,x,pred:dot(s.heads[j].w,x)});
  stat.targets=s.totalTargets;
  stat.endWeights=s.heads.map(h=>h.w.slice());
  stat.mae=s.heads.map(h=>round(h.MAE,5));
  stat.endNAV=round(nav(s,row.close));stat.position=s.pos;
  if(s.pos==="GOLD")stat.exposures++;
  const net=nav(s,row.close);
  s.peak=Math.max(s.peak,net);
  s.mdd=Math.max(s.mdd,100*(1-net/s.peak));
 }
 const close=a.at(-1).close;
 const startPrice=firstEligibleOpen??a[0].open;
 const buyHold=100*(1-FEE)*(close/startPrice)*(1-FEE);
 const report={
  experiment:"V22_JAN_2023_PRICE_ONLY_AUTONOMOUS_MATH_ADAGRAD_HEDGE",
  scope:"2023-01 ONLY; price-only; no macro, NQ, ETF, other months",
  disclaimer:"EXPOST_HISTORICAL_M15_PRICE_PROXY_NOT_ACTUAL_BANK_BIDASK_NOT_OOS",
  feePerSide:FEE,roundTripCostPct:1.6,initialUSD:100,
  bars:a.length,totalTargetsMatured:s.totalTargets,
  nonzeroMathematicalUpdates:s.totalNonzeroUpdates,
  acceptedBankChecks:eligible.length,realTrades:s.trades.length,
  finalPosition:s.pos,
  endingCash:s.cash,endingGoldUnits:s.units,
  endingNetLiquidationUSD:round(nav(s,close)),
  returnPct:round(100*(nav(s,close)/100-1)),
  maxDDPct:round(s.mdd),feesPaidUSD:round(s.fees),
  benchCashUSD:100,benchPassiveGoldUSD:round(buyHold),
  passiveStartPrice:round(startPrice,3),finalMark:round(close,3),
  hasLearnedParameters:s.heads.some(h=>h.w.some(w=>Math.abs(w)>1e-10)),
  heads:s.heads.map((h,i)=>({horizonBars:h.h,n:h.n,
    mae:round(h.MAE),rmse:round(Math.sqrt(h.MSE)),
    residualBias:round(h.bias),residualStd:round(Math.sqrt(h.var)),
    hedgeWeight:round(s.metaWeights[i]),weights:h.w.map(x=>round(x,7))})),
  trades:s.trades,
  daily:Object.entries(daily).map(([date,v])=>({date,
    observations:v.observations,scoreReady:v.scoreReady,
    targetsAtEnd:v.targets,actions:v.actions,netNAV:v.endNAV,
    position:v.position,exposureBars:v.exposures,
    headsMAE:v.mae})),
  metadata:{monthCount:1,manualRetuning:false,liveTrading:false,
    usingOtherMarketFeatures:false,predictionsEvaluatedAfterMaturity:true,
    oneStepAheadOpenProxy:true,bankWindow:"weekday TRT 09-17",
    lastMarketObservation:a.at(-1).tt,
    firstMarketObservation:a[0].tt}};
 if(opts.fullAudit){
  report.decisionAudit=s.decisions.map(d=>d);
 }
 return report;
}
if(require.main===module){
 const panel=process.argv[2],out=process.argv[3],audit=process.argv[4];
 if(!panel||!out)throw Error("usage: node v22_jan2023_math.js panel.csv out.json [audit.json]");
 const report=forward(parseCsv(fs.readFileSync(panel,"utf8")),{fullAudit:!!audit});
 fs.mkdirSync(path.dirname(out),{recursive:true});
 fs.writeFileSync(out,JSON.stringify({...report,decisionAudit:undefined},null,2));
 if(audit)fs.writeFileSync(audit,JSON.stringify(report.decisionAudit,null,2));
 const {daily,heads,trades,...summary}=report;
 console.log(JSON.stringify({summary,heads,trades},null,2));
}
module.exports={parseCsv,contig,vector,create,mature,score,forward,execute,bankWindow};
