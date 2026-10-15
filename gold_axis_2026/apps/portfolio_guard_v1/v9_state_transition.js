"use strict";
/**
 * V9 research-only: state transitions, cost-aware shadow-policy consensus, 
 * delayed net opportunity labels, deferred next-bank-checkpoint execution.
 * All source records are strictly chronological and pinned by V8 loader.
 */
const {loadFullRows}=require("./v8_regret_engine");
const FEE=.008,HR=3600000;
const EXPERTS=["CARRY","TREND","BREAKOUT","RECOVERY","CASH"];
const bounds=(a,lo,hi)=>Math.min(hi,Math.max(lo,a));
function bankCheckpoint(t){
 const h=new Date(t).getUTCHours();
 return h===6||h===9||h===12;
}
function regime(r){
 const stress=(r.r4!=null&&r.r4<=-1&&r.nq6!=null&&r.nq6<=-1);
 const breakdown=(r.r1!=null&&r.r3!=null&&r.r1< -4&&r.r3< -3);
 if(stress||breakdown)return "STRESS";
 if(r.r1!=null&&r.r3!=null&&r.r1>1.2&&r.r3>1.2)return "UP";
 if(r.r1!=null&&r.r3!=null&&r.r1< -1.2&&r.r3< -1.2)return "DOWN";
 return "RANGE";
}
function policy(row,reg,state){
 const {r4,r1,r3,rv,nq6}=row;
 const notStress=reg!=="STRESS";
 const up=r1!=null&&r3!=null&&r1>0&&r3>0;
 const carry=notStress&&r1>-2&&r3>-2&&!(r4<-1.6);
 const trend=notStress&&r1>.4&&r3>.3&&(r4>-.9);
 const breakout=notStress&&r1>1.3&&r3>.4&&r4>.15&&
   (rv==null||rv<2.7)&&(nq6==null||nq6> -1.4);
 const recovery=notStress&&state.daysSinceStress<=24*26&&state.daysSinceStress>=24&&
   r4>.35&&r1>-.35&&r3> -1.3&&
   (nq6==null||nq6> -1.4)&&(rv==null||rv<2.3);
 return {CARRY:!!carry,TREND:!!trend,BREAKOUT:!!breakout,
   RECOVERY:!!(up||recovery),CASH:false};
}
function makePortfolio(initial=100){
 return {cash:initial,ounces:0,lastNav:initial,returns:[],navHistory:[],
  pending:null,transactions:[],lastBuy:-Infinity,lastSell:-Infinity};
}
function nav(p,r){
 return p.cash+p.ounces*r.c*(1-FEE);
}
function fill(p,row,desired,label){
 const next=!!desired;
 const has=p.ounces>0;
 if(next===has)return;
 if(next){
  const qty=p.cash*(1-FEE)/row.p;
  if(!Number.isFinite(qty)||qty<0)throw Error("BAD_BUY");
  p.ounces=qty;p.cash=0;p.lastBuy=Date.parse(row.tt);
 }else{
  p.cash=p.ounces*row.p*(1-FEE);p.ounces=0;p.lastSell=Date.parse(row.tt);
 }
 p.transactions.push({at:row.tt,side:next?"BUY":"SELL",mid:row.p,why:label,
   cash:p.cash,ounces:p.ounces});
}
function calcWeight(p,window=120){
 const a=p.navHistory;
 if(a.length<12)return 0;
 const start=Math.max(0,a.length-1-window),slice=a.slice(start);
 const gain=Math.log(Math.max(.01,slice.at(-1))/Math.max(.01,slice[0]));
 let peak=slice[0],dd=0;
 for(const v of slice){peak=Math.max(peak,v);dd=Math.max(dd,1-v/peak);}
 // Score trailing 6-8 weeks' realized, commission-inclusive PAPER performance.
 return bounds(gain-.6*dd,-1,1);
}
function labelsReady(pending,t,r,buckets,ledger){
 const queued=[];
 for(const x of pending){
  if(x.due>t){queued.push(x);continue;}
  if(t-x.due>78*HR)continue;
  const net=100*((1-FEE)**2*r.c/x.price-1);
  const bucket=buckets[x.h][x.reg];
  bucket.count++;bucket.win+=net>0?1:0;
  bucket.mean+=(net-bucket.mean)/bucket.count;
  bucket.loss+=(Math.abs(net)-bucket.loss)/bucket.count;
  bucket.lastMatured=t;
  ledger.push({origin:x.origin,matured:r.tt,h:x.h,regime:x.reg,
    netReturnPct:net,wouldProfit:net>0,
    afterLabelEnd:true,durationHours:(t-x.time)/HR});
 }
 return queued;
}
function onlinePosterior(bucket,horizonHours){
 // Adjacent 09:00 labels overlap. Discount effective sample size,
 // Bayesian shrinkage to neutral prior. Do NOT treat them as independent trials.
 const effective=bucket.count/(horizonHours/24);
 const alpha=2+effective*(bucket.count?bucket.win/bucket.count:0);
 return {nRaw:bucket.count,nEffective:effective,
   winProbability:alpha/(4+effective),
   meanNetPct:bucket.mean,lastMatured:bucket.lastMatured};
}
function replay(rows,options={}){
 const start=Date.parse(options.start||"2026-02-02T06:00:00Z");
 const end=Date.parse(options.end||"2026-09-30T12:00:00Z");
 const initial=options.initial??119.753917;
 const mode=options.mode||"ensemble";
 if(!["ensemble","equal","carry","trend","breakout","recovery","cash","no_label_gate"].includes(mode))throw Error("BAD_MODE");
 if(!Number.isFinite(start)||!Number.isFinite(end)||start>end)throw Error("BAD_RANGE");
 let paper=Object.fromEntries(EXPERTS.map(x=>[x,makePortfolio(100)]));
 let live=makePortfolio(initial),bucket={h96:{},h336:{}};
 for(const h of Object.keys(bucket))for(const k of ["STRESS","UP","DOWN","RANGE"])
    bucket[h][k]={count:0,win:0,mean:0,loss:0,lastMatured:null};
 const pendingLabels=[],labelLedger=[],decisions=[],history=[],monthly=[],selection=[];
 let labels=pendingLabels,lastStress=-Infinity,lastBank=null;
 for(let i=0;i<rows.length;i++){
  const row=rows[i],t=Number.isFinite(row.ts)?row.ts:Date.parse(row.tt);
  if(t>end)break;
  if(i>0&&t<=Date.parse(rows[i-1].tt))throw Error("V9_OUT_OF_ORDER");
  labels=labelsReady(labels,t,row,bucket,labelLedger);
  const rg=regime(row);
  if(rg==="STRESS")lastStress=t;
  if(new Date(t).getUTCHours()===6){
   for(const h of ["h96","h336"])labels.push({
    origin:row.tt,time:t,due:t+(h==="h96"?96:336)*HR,
    h,reg:rg,price:row.c
   });
  }
  if(!bankCheckpoint(t))continue;
  // First execute only decisions issued at an earlier bank checkpoint.
  for(const expert of EXPERTS){
    const p=paper[expert];
    if(p.pending&&p.pending.created<t){
      fill(p,row,p.pending.desired,"SHADOW_"+expert);
      p.pending=null;
    }
  }
  if(t>=start&&live.pending&&live.pending.created<t){
    fill(live,row,live.pending.desired,live.pending.reason);
    live.pending=null;
  }
  // Evaluate mark-to-market BEFORE making a new decision.
  for(const expert of EXPERTS){
   const p=paper[expert],now=nav(p,row);
   p.navHistory.push(now);p.lastNav=now;
  }
  if(t>=start){
    const now=nav(live,row),old=history.at(-1)?.netUSD??initial;
    history.push({utc:row.tt,netUSD:now,position:live.ounces?"GOLD":"CASH",month:new Date(t+3*HR).toISOString().slice(0,7)});
  }
  const state={daysSinceStress:(t-lastStress)/HR};
  const expertSignals=policy(row,rg,state);
  for(const expert of EXPERTS)
   paper[expert].pending={desired:expertSignals[expert],created:t};
  if(t<start)continue;
  const weights=Object.fromEntries(EXPERTS.map(key=>[key,mode==="equal"?1:
    Math.exp(7*calcWeight(paper[key]))]));
  const total=EXPERTS.reduce((sum,k)=>sum+weights[k],0);
  const vote=EXPERTS.reduce((s,k)=>s+weights[k]*(expertSignals[k]?1:0),0)/total;
  const posterior=onlinePosterior(bucket.h336[rg],336);
  const riskVeto=rg==="STRESS";
  const gateEnabled=mode!=="no_label_gate";
  const labelCanBuy=posterior.nEffective<4||posterior.winProbability>=.44;
  let desired=mode==="cash"?false:
    ["carry","trend","breakout","recovery"].includes(mode)?expertSignals[mode.toUpperCase()]:
    vote>.51;
  if(gateEnabled&&!labelCanBuy)desired=false;
  if(riskVeto)desired=false;
  // Prevent rapid reacquisition churn in fee-heavy bank account.
  const cooldown=t-live.lastSell>=72*HR;
  if(!live.ounces&&!cooldown)desired=false;
  const reason=riskVeto?"HARD_STRESS_VETO":
    !labelCanBuy&&gateEnabled?"MATURED_LABEL_VETO":
    "COST_AWARE_EXPERT_CONSENSUS";
  live.pending={desired,created:t,reason};
  decisions.push({utc:row.tt,regime:rg,desired:desired?"GOLD":"CASH",
    position:live.ounces?"GOLD":"CASH",signalCreated:t,
    nextBankExecutionNotSameBar:true,vote,weights,
    posterior,reason,knownLabelCutoffUTC:posterior.lastMatured});
 }
 if(!lastBank&&history.length)lastBank=history.at(-1);
 const last=history.at(-1);
 if(!last)throw Error("V9_NO_DECISIONS");
 const cash=live.cash,ounces=live.ounces;
 let prevMonth=null;
 for(const step of history){
  if(step.month!==prevMonth){
   monthly.push({month:step.month,initialUSD:monthly.length?monthly.at(-1).terminalUSD:initial,
     terminalUSD:step.netUSD,endPosition:step.position});
   prevMonth=step.month;
  }
  monthly.at(-1).terminalUSD=step.netUSD;
  monthly.at(-1).endPosition=step.position;
 }
 return {
  version:"V9_ONLINE_POLICY_MIXTURE_V1",mode,sourceRows:rows.length,
  start:new Date(start).toISOString(),end:new Date(end).toISOString(),
  initial,final:last.netUSD,profitPct:100*(last.netUSD/initial-1),
  costs:{feePerSide:FEE,realBankBidAsk:false},
  execution:{signalOneCheckpointBeforeFill:true,bankHoursTR:[9,12,15],
    futureLookingFeatureUsed:false},
  monthly,trades:live.transactions,labelsLearned:labelLedger.length,
  labelsByRegime:Object.fromEntries(["STRESS","UP","DOWN","RANGE"].map(x=>[x,
    {h96:onlinePosterior(bucket.h96[x],96),h336:onlinePosterior(bucket.h336[x],336)}])),
  labelSamples:options.includeLabels?labelLedger:undefined,
  decisions:options.includeDecisions?decisions:undefined,
  bankExecutionVerified:false,independentBlindTest:false,
  noLiveTrade:true,macroFirstprintVerified:0
 };
}
function runAudit(){
 const src=loadFullRows(),base=[
   {label:"2024",start:"2024-01-02T06:00:00Z",end:"2024-12-31T12:00:00Z",initial:100},
   {label:"2025",start:"2025-01-07T06:00:00Z",end:"2025-12-31T12:00:00Z",initial:100},
   {label:"2026_FebSep",start:"2026-02-02T06:00:00Z",end:"2026-09-30T12:00:00Z",initial:119.753917}
 ];
 const trials=[];
 for(const spec of base)for(const mode of ["ensemble","equal","carry","trend","breakout","recovery","cash","no_label_gate"]){
    const output=replay(src.rows,{...spec,mode});
    trials.push({year:spec.label,mode,initial:output.initial,final:output.final,
      profitPct:output.profitPct,trades:output.trades.length,labels:output.labelsLearned,
      byMonth:output.monthly});
 }
 return {version:"V9_ONLINE_POLICY_MIXTURE_RESEARCH",
    status:"CANDIDATES_NOT_AUTOMATICALLY_ACCEPTED",
    pinned:src.data,
    trials,
    policy:"2024 and 2025 are inspected design/validation years, 2026 is retrospective stress, no independent blind year",
    liveTrade:false,realBankBidAsk:false,sourceEventFirstprints:0};
}
module.exports={EXPERTS,FEE,regime,policy,calcWeight,onlinePosterior,labelsReady,replay,runAudit};
