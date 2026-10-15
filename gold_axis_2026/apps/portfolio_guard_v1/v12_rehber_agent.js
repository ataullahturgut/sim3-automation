"use strict";
/**
 * V12 REHBER: novel error-correcting episode-memory trading policy.
 * NOT an ANN, optimised oracle, or bank execution system.
 * Its learnable entities are situation memories, specialist reliability,
 * and action threshold updated only after delayed realized outcomes.
 */
const {loadFullRows}=require("./v8_regret_engine");
const {dataset}=require("./v11_ann_research");
const E=require("./v12_episodic_memory");
const HR=E.HR,DAY=E.DAY,FEE=E.FEE,clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const VARIANTS=Object.freeze({
 REHBER_CORE:{adapt:true,stressExit:true,reliabilityAdaptive:true,margin:.6,prob:.58},
 REHBER_FIXED_MARGIN:{adapt:false,stressExit:true,reliabilityAdaptive:true,margin:.6,prob:.58},
 REHBER_NO_RELIABILITY:{adapt:true,stressExit:true,reliabilityAdaptive:false,margin:.6,prob:.58},
 REHBER_NO_STRESS:{adapt:true,stressExit:false,margin:.6,prob:.58},
 REHBER_SAFETY:{adapt:true,stressExit:true,margin:1.2,prob:.64}
});
function actionDecision(pred,context,state,settings){
 if(!pred.ready)return{target:context.holding?"GOLD":"CASH",why:"NEEDS_MATURED_EPISODES"};
 const downside=context.stress;
 const uncertainty=pred.uncertaintyPct;
 // All inputs are bank-fee-NET prior transaction values: cost is not
 // charged again in expected return threshold, only in realized portfolio.
 const minGain=Math.max(state.buyMargin,.35*uncertainty);
 const buyOpportunity=pred.net14>minGain&&pred.pProfit>settings.prob&&
    pred.tail20> -6&&!downside;
 const isRisk=pred.net4< -1.2&&pred.pProfit<.54||
    pred.net14< -1.1&&pred.tail20< -3.0;
 if(!context.holding&&context.hoursFromSell>=96&&buyOpportunity)
   return {target:"GOLD",why:"MEMORY_NET_ADVANTAGE",minGain};
 if(context.holding&&
    ((downside&&settings.stressExit)||
     (context.hoursHolding>=96&&isRisk)))
   return{target:"CASH",why:downside?"RECOGNIZED_MARKET_SHOCK":"LEARNED_NEGATIVE_OUTCOME",minGain};
 return {target:context.holding?"GOLD":"CASH",why:"NO_CONFIDENT_NET_ADVANTAGE",minGain};
}
function retrainMargin(state,origin,pred,actual,now,settings){
 if(origin.exit14Ts>=now)throw Error("V12_REGRET_USES_FUTURE");
 if(!pred?.ready)return;
 let label="NO_ACTION_ERROR",change=0;
 if(origin.wasCashAtSignal&&origin.proposed==="GOLD"&&actual[1]<0){
   label="FALSE_BUY";change=.06*Math.min(6,-actual[1]);
 }else if(origin.wasCashAtSignal&&origin.proposed==="CASH"&&actual[1]>0){
   label="MISSED_PROFIT";change=-.035*Math.min(6,actual[1]);
 }else if(!origin.wasCashAtSignal&&origin.proposed==="GOLD"&&actual[0]<-1.6){
   label="LATE_SELL";change=.04*Math.min(6,-actual[0]);
 }
 if(settings.adapt)state.buyMargin=clamp(state.buyMargin+change,.2,2.5);
 state.learnedDecisions++;
 state.errorTypes[label]=(state.errorTypes[label]||0)+1;
 state.history.push({origin:origin.at,knownAt:new Date(now).toISOString(),
   label,net4Actual:actual[0],net14Actual:actual[1],
   marginBefore:origin.marginAtSignal,marginAfter:state.buyMargin,
   updated:settings.adapt});
}
function memoryTimeline(ds,opts={}){
 const end=Date.parse(opts.end||"2026-09-30T12:00:00Z");
 const start=Date.parse(opts.start||"2026-02-02T06:00:00Z");
 const initial=opts.initial??119.753917,variant=opts.variant||"REHBER_CORE";
 if(!Object.hasOwn(VARIANTS,variant))throw Error("BAD_REHBER_VARIANT");
 const settings=VARIANTS[variant];
 const memory=E.create();memory.freezeSpecialistLoss=settings.reliabilityAdaptive===false;
 const state={buyMargin:settings.margin,learnedDecisions:0,errorTypes:{},history:[]};
 const all=[...ds.samples].sort((a,b)=>a.exit14Ts-b.exit14Ts);
 const seenBlock=new Set(),completedRegretBlocks=new Set();
 const active=[],saved=[];
 let pointer=0,ounces=0,cash=initial,lastBuy=-Infinity,lastSale=-Infinity,
   pending=null,monthly=[],trades=[],decisions=[],predictions=[],warmups=0;
 for(const row of ds.bank){
  const t=row.ts;
  if(t>end)break;
  // Strict < : a sample at this timestamp cannot use its own outcome.
  while(pointer<all.length&&all[pointer].exit14Ts<t){
   const ep=all[pointer++];
   E.appendMatured(memory,ep,t);
  }
  for(let i=active.length-1;i>=0;i--){
   const item=active[i];
   if(item.ep.exit14Ts>=t)continue;
   active.splice(i,1);
   const actual=item.ep.y;
   E.feedback(memory,item.ep,item.pred,actual,t);
   retrainMargin(state,item.ep,item.pred,actual,t,settings);
  }
  const hr=new Date(row.tt).getUTCHours();
  if(![6,9,12].includes(hr))continue;
  if(t>=start&&pending&&pending.atMs<t){
    if(pending.target==="GOLD"&&!ounces){
     ounces=cash*(1-FEE)/row.p;cash=0;lastBuy=t;
     trades.push({at:row.tt,signalAt:pending.at,side:"BUY",
       reason:pending.why,price:row.p,margin:pending.margin});
    }else if(pending.target==="CASH"&&ounces){
     cash=ounces*row.p*(1-FEE);ounces=0;lastSale=t;
     trades.push({at:row.tt,signalAt:pending.at,side:"SELL",
       reason:pending.why,price:row.p,margin:pending.margin});
    }
    pending=null;
  }
  const nav=cash+ounces*row.c*(1-FEE);
  if(t>=start){
   const mo=new Date(t+3*HR).toISOString().slice(0,7);
   if(monthly.at(-1)?.month!==mo)monthly.push({month:mo,nav,position:ounces?"GOLD":"CASH"});
   else{monthly.at(-1).nav=nav;monthly.at(-1).position=ounces?"GOLD":"CASH";}
  }
  // Signal only at 09:00 Turkish time (UTC 06). This is the first date at
  // which the day's market conditions are considered known.
  if(hr!==6)continue;
  const feat=ds.featuresByOrigin.get(row.tt);
  if(!feat)throw Error("V12_ORIGIN_HAS_NO_CAUSAL_FEATURE_VECTOR");
  const pred=E.forecast(memory,feat,t);
  const stress=row.r4!=null&&row.r4<=-1&&row.nq6!=null&&row.nq6<=-1;
  const context={stress,holding:t>=start&&!!ounces,
    hoursHolding:(t-lastBuy)/HR,
    hoursFromSell:(t-lastSale)/HR};
  // Warmup predictions learn specialists without synthesizing trades before
  // actual evaluation start. Signals in warming period are shadow-only.
  const decision=actionDecision(pred,context,state,settings);
  const ep=ds.byOrigin.get(row.tt);
  if(ep&&!completedRegretBlocks.has(E.blockOf(t))){
    completedRegretBlocks.add(E.blockOf(t));
    active.push({ep:{...ep,wasCashAtSignal:!context.holding,
      proposed:decision.target,marginAtSignal:state.buyMargin},
      pred});
  }
  if(!pred.ready)warmups++;
  if(t>=start){
   const proposed=decision.target,position=ounces?"GOLD":"CASH";
   if(proposed!==position&&!pending)pending={
    target:proposed,at:row.tt,atMs:t,why:decision.why,margin:state.buyMargin};
   decisions.push({asOf:row.tt,regime:stress?"STRESS":"NORMAL",
    position,proposed,reason:decision.why,
    predictedNet14:pred.net14??null,predictedNet4:pred.net4??null,
    pProfit:pred.pProfit??null,nEffective:pred.nEffective,
    uncertaintyPct:pred.uncertaintyPct??null,
    buyMargin:state.buyMargin,analogs:pred.ready?pred.experts?.TREND?.analogs:[]});
   predictions.push({asOf:row.tt,pred});
  }
 }
 const final=monthly.at(-1)?.nav;
 if(!Number.isFinite(final))throw Error("NO_EVALUATION_BANK_ROWS");
 return {version:"V12_REHBER_EPISODIC_LEARNING",variant,
  initial,final,netPct:100*(final/initial-1),trades,monthly,
  sourceRows:ds.records,completedAnalogLabels:memory.maturedEpisodeCount,
  independentEpisodeBlocks:new Set(memory.memory.map(x=>E.blockOf(x.ts))).size,
  predictionDays:decisions.length,warmupDays:warmups,
  learning:{updates:state.learnedDecisions,
    marginEnd:state.buyMargin,mistakes:state.errorTypes,
    recent:state.history.filter(x=>Date.parse(x.knownAt)>=start).slice(-15),
    lensLoss:memory.loss},
  decisions:opts.includeDecisions?decisions:undefined,
  assumptions:{bankFeeEachDirection:FEE,bankTradingHoursTR:[9,12,15],
    asofSignalTR:"09:00",execute:"NEXT_BANK_CHECKPOINT",
    actualBankBidAsk:false,eventFirstprintVerified:0,
    independentBlindValidation:false,automatedBankOrders:false},
  scientificGate:{promote:false,reason:"NO_UNSEEN_PROSPECTIVE_GENERALIZATION_YET"}
 };
}
let cacheDS;
function audit(){
 const ds=cacheDS??(cacheDS=dataset(loadFullRows().rows));
 const periods=[
  {year:"2024",start:"2024-01-02T06:00:00Z",end:"2024-12-31T12:00:00Z",initial:100},
  {year:"2025",start:"2025-01-07T06:00:00Z",end:"2025-12-31T12:00:00Z",initial:100},
  {year:"2026_FEB_SEP",start:"2026-02-02T06:00:00Z",end:"2026-09-30T12:00:00Z",initial:119.753917}
 ];
 const results=[];
 for(const period of periods)for(const variant of Object.keys(VARIANTS)){
  const s=memoryTimeline(ds,{...period,variant});
  results.push({year:period.year,variant,initial:s.initial,final:s.final,
    profitPct:s.netPct,tradeCount:s.trades.length,completedLabels:s.completedAnalogLabels,
    analogBlocks:s.independentEpisodeBlocks,learning:s.learning,trades:s.trades,
    monthly:s.monthly});
 }
 return {version:"V12_REHBER_ORIGINAL_CAUSAL_MEMORY_RESEARCH",
  status:"NO_AUTOMATIC_PROMOTION",data:{rows:ds.records,labeledOrigins:ds.samples.length},
  design:{ANNArchitecture:false,learnableLayers:[
    "episodic_state_memory",
    "specialist_error_weight_update",
    "counterfactual_action_regret_margin"],
    memoryMakesNoFutureQueries:true,commissionIncludedInLabels:true,
    evaluationYearsPreviouslyInspected:true},
  results,scientificGate:{promote:false,liveTradingAuthorized:false,
    independentBlindPeriod:false,bankAskBidMeasured:false,
    macroEvidenceFirstprintConfirmed:0}};
}
module.exports={VARIANTS,actionDecision,retrainMargin,memoryTimeline,audit};
