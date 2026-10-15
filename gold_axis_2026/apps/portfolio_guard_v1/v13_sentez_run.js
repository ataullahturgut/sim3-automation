"use strict";
/** Scientific chronological trading harness for V13 SENTEZ.
 * Signals are 09:00 Turkish time; proxy execution is next 12:00 checkpoint.
 * All 14d/56d training targets are strictly matured prior to online update.
 * 2026 has been seen before: RETROSPECTIVE only, never blind validation.
 */
const H=require("./v13_sentez_core");
const VERSIONS=Object.freeze(["SENTEZ_HYBRID","NO_ANN","NO_FUZZY","NO_GATED_MEMORY","NO_LONG_HORIZON"]);
const BLOCK14=14*H.DAY,BLOCK56=28*H.DAY;
const same=(x,y)=>Math.abs(x-y)<.00001;
let memo;
function build(){
 const src=H.loadFullRows();
 const primary=H.dataset(src.rows),extended=H.addExtendedLabels(primary);
 return {src,primary,extended};
}
function one(built,opt={}){
 const variant=opt.variant||"SENTEZ_HYBRID";
 if(!VERSIONS.includes(variant))throw Error("INVALID_SENTEZ_VARIANT");
 const start=Date.parse(opt.start||"2023-01-03T06:00:00Z"),
  end=Date.parse(opt.end||"2026-09-30T12:00:00Z"),
  initial=opt.initial??100,ds=built.extended;
 if(!Number.isFinite(start)||!Number.isFinite(end)||start>=end)throw Error("INVALID_SENTEZ_TIME");
 const disableANN=variant==="NO_ANN",disableFuzzy=variant==="NO_FUZZY",
  disableGate=variant==="NO_GATED_MEMORY",disableLong=variant==="NO_LONG_HORIZON";
 const state=H.create(),q14=[],q56=[],recentlyUsed14=new Set(),recentlyUsed56=new Set();
 let cash=initial,ounces=0,pending=null,lastBuy=-Infinity,lastExit=-Infinity,year=0,
  network=null,modelTrainedYear=null,lastRecordTime=-Infinity;
 const trades=[],signalled=[],monthly=[],diagnostics=[],events=[];
 for(const row of ds.bank){
  const now=row.ts;if(now>end)break;
  if(now<=lastRecordTime)throw Error("BANK_DATA_NON_MONOTONIC");
  lastRecordTime=now;
  // Apply labels matured PRIOR to the current instant. Entries are
  // chronological on their maturity dates.
  for(const [queue,horizon] of [[q14,14],[q56,56]]){
  while(queue.length&&queue[0].exitTs<now){
   const e=queue.shift();
   H.applyOutcome(state,{...e}, {now},horizon,disableFuzzy);
   events.push({time:row.tt,origin:e.origin,which:horizon,
     actual:e.target,forecast:horizon===14?e.forecast.net14:e.forecast.net56});
  }
  }
  if(now>=start&&pending&&pending.ts<now){
   const target=pending.position;
   if(target==="GOLD"&&!ounces){
    ounces=cash*(1-H.FEE)/row.p;cash=0;lastBuy=now;
    trades.push({at:row.tt,asOf:pending.at,side:"BUY",price:row.p,
      why:pending.why});
   }else if(target==="CASH"&&ounces){
    cash=ounces*row.p*(1-H.FEE);ounces=0;lastExit=now;
    trades.push({at:row.tt,asOf:pending.at,side:"SELL",price:row.p,
      why:pending.why});
   }
   pending=null;
  }
  const net=cash+ounces*row.c*(1-H.FEE);
  if(now>=start){
   const m=new Date(now+3*H.HR).toISOString().slice(0,7);
   if(monthly.at(-1)?.month!==m)monthly.push({month:m,netUSD:net,
     position:ounces?"GOLD":"CASH"});
   else {monthly.at(-1).netUSD=net;monthly.at(-1).position=ounces?"GOLD":"CASH";}
  }
  // Annual ANN fit is historical-only and source time is pre-year cutoff.
  if(new Date(now).getUTCHours()!==6)continue;
  const yr=new Date(now).getUTCFullYear();
  if(yr!==year){
   year=yr;
   network=disableANN?null:H.frozenANN(built.primary,year);
   modelTrainedYear=network?.lastTrainOrigin??null;
  }
  const origin=ds.byOrigin.get(row.tt);
  const features=ds.featuresByOrigin.get(row.tt);
  if(!features)throw Error("ASOF_FEATURE_NOT_AVAILABLE");
  if(!disableGate)state.gated=H.gatedState(state.gated,features);
  const pred=H.predict(state,features,network?.weights?network:null,
    {disableANN,disableFuzzy,disableGate,disableLong});
  const proposed=H.decision(pred,{
    hoursSinceExit:(now-lastExit)/H.HR,hoursHeld:(now-lastBuy)/H.HR
  },ounces?"GOLD":"CASH",{uncertainty:true});
  // Queue only one origin per label correlation block for independent-ish
  // feedback. 56d labels spaced 28d are still overlapping 2x.
  if(origin){
   const key14=Math.floor(now/BLOCK14),key56=Math.floor(now/BLOCK56);
   if(origin.y14!==null&&!recentlyUsed14.has(key14)){
    recentlyUsed14.add(key14);
    q14.push({origin:row.tt,exitTs:origin.exit14Ts,target:origin.y14,forecast:pred});
   }
   if(origin.y56!==null&&!recentlyUsed56.has(key56)&&!disableLong){
    recentlyUsed56.add(key56);
    q56.push({origin:row.tt,exitTs:origin.exit56Ts,target:origin.y56,forecast:pred});
   }
  }
  if(now>=start){
   if(proposed.position!==(ounces?"GOLD":"CASH")&&!pending){
    pending={position:proposed.position,at:row.tt,ts:now,why:proposed.reason};
    signalled.push({...pending,net14:pred.net14,net56:pred.net56});
   }
   diagnostics.push({at:row.tt,
    net14:pred.net14,net56:pred.net56,regimeTrend:pred.regime.trend,
    regimeStress:pred.regime.stress,uncertainty56:pred.uncertainty56,
    n14:pred.n14,n56:pred.n56,
    action:proposed.position,position:ounces?"GOLD":"CASH",
    reason:proposed.reason});
  }
 }
 if(!monthly.length)throw Error("NO_BANK_ROWS_IN_PERIOD");
 const last=monthly.at(-1);
 const initialBank=ds.bank.find(r=>r.ts>start&&r.ts<=end);
 const finalBank=ds.bank.filter(r=>r.ts<=end).at(-1);
 const passive=(initialBank&&finalBank)?initial*(1-H.FEE)**2*
  finalBank.p/initialBank.p:null;
 for(const tr of trades)if(!(Date.parse(tr.at)>Date.parse(tr.asOf)))
   throw Error("FUTURE_FILL");
 return{version:"V13_SENTEZ_MULTI_HORIZON_HYBRID_20261016",variant,
  initial,final:last.netUSD,netPct:100*(last.netUSD/initial-1),
  passiveGoldUSD:passive,bankProxyClose:finalBank.tt,
  tradeCount:trades.length,trades,monthly,signalCount:signalled.length,
  labelsApplied14:state.labelsApplied14,labelsApplied56:state.labelsApplied56,
  residual:state.residual,feedbackCount:events.length,
  trainedANNThroughOrigin:modelTrainedYear,
  diagnostic:opt.includeDiagnostics?diagnostics:undefined,
  feedback:opt.includeFeedback?events:undefined,
  assumptions:{eachFee:.008,bankBidAsk:false,
   execution:"NEXT_BANK_CHECKPOINT",asof:"09TR",
   learning14SpacingDays:14,learning56SpacingDays:28,
   allHorizonOutcomesStrictlyMatured:true,
   long56LabelsOverlapAcross28DayBlocks:true},
  scientificGate:{promote:false,blind:false,liveTrade:false}};
}
function audit(){
 if(memo)return memo;
 const b=build(),periods=[
  {name:"2023_TO_2026",start:"2023-01-03T06:00:00Z",
   end:"2026-09-30T12:00:00Z",initial:100},
  {name:"2024",start:"2024-01-02T06:00:00Z",
   end:"2024-12-31T12:00:00Z",initial:100},
  {name:"2025",start:"2025-01-07T06:00:00Z",
   end:"2025-12-31T12:00:00Z",initial:100},
  {name:"2026_FEB_SEP",start:"2026-02-02T06:00:00Z",
   end:"2026-09-30T12:00:00Z",initial:119.753917}
 ];
 const experiments=[];
 for(const p of periods){
  for(const variant of VERSIONS){
   const x=one(b,{...p,variant});
   experiments.push({period:p.name,variant,initialUSD:x.initial,finalUSD:x.final,
     pct:x.netPct,buyHoldUSD:x.passiveGoldUSD,trades:x.trades.length,
     outcome14:x.labelsApplied14,outcome56:x.labelsApplied56,
     perMonth:x.monthly,ledger:x.trades});
  }
 }
 const full=experiments.filter(x=>x.variant==="SENTEZ_HYBRID");
 const consistent2024=full.find(x=>x.period==="2024"),
   consistent2025=full.find(x=>x.period==="2025");
 memo={version:"V13_SENTEZ_RESEARCH_AUDIT_20261016",
    status:"SHADOW_EXPERIMENT_NO_AUTOMATIC_PROMOTION",
    architecture:{
      ANN:"Real trainable backprop MLP 14x12x8x2, frozen each calendar year",
      ANFIS:"Six normalized Sugeno fuzzy rules with matured-label adaptive consequents",
      LSTM:"LSTM-inspired recurrent forget/update gated state; gates are deterministic NOT trained LSTM",
      objective:"Bank-cost net 14d + 56d opportunity, not a future optimal trade oracle",
      feedbackSpacing14Days:14,feedbackSpacing56Days:28
    },
    source:{rows:b.src.rows.length,originLabels:b.primary.samples.length},
    experiments,scientificGate:{
      promote:false,liveTrading:false,blind2026:false,
      alreadyInspected2023To2026:true,
      bankBidAskVerified:false,macroFirstprintsVerified:0,
      riskOfOverfitting:true,
      passedBothEarlyYearsAgainstPassive:
        consistent2024.finalUSD>consistent2024.buyHoldUSD&&
        consistent2025.finalUSD>consistent2025.buyHoldUSD
    }};
 return memo;
}
module.exports={VERSIONS,build,one,audit};
