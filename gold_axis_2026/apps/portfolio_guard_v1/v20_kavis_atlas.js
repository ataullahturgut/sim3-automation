"use strict";
/**
 * V19 KAVIS-SIPER: robust-goal sequential action controller.
 * V18 Double-Q is the ONLY learned expected-value policy.
 * This module adds an as-of, path-dependent goal/risk supervisor:
 *  (1) trusted input / safe execution
 *  (2) realized liquidation-NAV drawdown and empirically learned
 *      conditional one-interval loss CVaR
 *  (3) risk-adjusted Q advantage and abstention
 *  (4) turnover is penalized ONCE inside V18 Q reward.
 * No actual orders, no guarantee of a maximum drawdown.
 * Historical 2023-2026 XAU data must not be imported in this module.
 */
const Core=require("./v18_kavis_dayaniqlilik");
const VERSION="V20_KAVIS_ATLAS_REGRET_GATED_20261016";
const DAY=Core.DAY,HR=Core.HR;
const finite=x=>typeof x==="number"&&Number.isFinite(x);
const max=(x,l,h)=>Math.min(h,Math.max(l,x));
const deep=x=>JSON.parse(JSON.stringify(x));
function config(o={}){
 const c={
   initialCapital:o.initialCapital??100,
   maxDrawdownPct:o.maxDrawdownPct??null,
   maxTailLossPct:o.maxTailLossPct??6,
   alpha:o.alpha??.90,
   minTailObservations:o.minTailObservations??20,
   minConditionalObservations:o.minConditionalObservations??8,
   tailWindow:o.tailWindow??128,
   ambiguityScale:o.ambiguityScale??.35,
   riskPenalty:o.riskPenalty??.65,
   stopBufferPct:o.stopBufferPct??1.5,
   recoveryObservations:o.recoveryObservations??2,
   useRiskPolicy:o.useRiskPolicy??true,
   riskAdvisorMinLabels:o.riskAdvisorMinLabels??16,
   advisorDecay:o.advisorDecay??.94,
   advisorConfidence:o.advisorConfidence??.35
 };
 if(!finite(c.initialCapital)||c.initialCapital<=0||c.initialCapital>1e12||
    c.maxDrawdownPct!==null&&(!finite(c.maxDrawdownPct)||c.maxDrawdownPct<=1||c.maxDrawdownPct>=90)||
    !finite(c.maxTailLossPct)||c.maxTailLossPct<=.25||c.maxTailLossPct>=70||
    !finite(c.alpha)||c.alpha<.75||c.alpha>=.99||
    !Number.isInteger(c.minTailObservations)||c.minTailObservations<8||c.minTailObservations>1000||
    !Number.isInteger(c.minConditionalObservations)||c.minConditionalObservations<4||
    c.minConditionalObservations>c.minTailObservations||
    !Number.isInteger(c.tailWindow)||c.tailWindow<32||c.tailWindow>4096||
    !finite(c.ambiguityScale)||c.ambiguityScale<0||c.ambiguityScale>3||
    !finite(c.riskPenalty)||c.riskPenalty<0||c.riskPenalty>5||
    !finite(c.stopBufferPct)||c.stopBufferPct<0||c.stopBufferPct>=10||
    !Number.isInteger(c.recoveryObservations)||c.recoveryObservations<0||
    c.recoveryObservations>30||typeof c.useRiskPolicy!=="boolean"||
    !Number.isInteger(c.riskAdvisorMinLabels)||c.riskAdvisorMinLabels<8||
    c.riskAdvisorMinLabels>500||!finite(c.advisorDecay)||c.advisorDecay<.7||
    c.advisorDecay>=1||!finite(c.advisorConfidence)||c.advisorConfidence<0||
    c.advisorConfidence>3)
     throw Error("V19_INVALID_RISK_GOALS");
 return c;
}
function create(options={}){
 const cfg=config(options);
 return {version:VERSION,config:cfg,core:Core.create(options.core||{}),
  portfolio:{position:"CASH",cash:cfg.initialCapital,units:0,
    nav:cfg.initialCapital,peak:cfg.initialCapital,
    drawdownPct:0,maxDrawdownPct:0,trades:0,feeDollars:0,
    realizedCheckpointCount:0},
  risk:{all:[],buckets:{STRESS:[],RALLY:[],QUIET:[]},
    advisor:Object.fromEntries(["STRESS","RALLY","QUIET"].map(k=>
      [k,{n:0,mean:0,var:4,lastDelta:0,positive:0,negative:0}])),
    lastFill:null,learnedReturns:0,
    tailMisses:0,recoveryCount:0,afterForcedExit:false},
  pendingContext:null,
  audit:{forcedExits:0,blockedEntries:0,riskAbstains:0,
    normalDecisions:0,postCrashGapWarnings:0,regimeReturnLabels:0,
    advisorConsidered:0,advisorActivated:0,advisorRejected:0,advisorMatured:0}
 };
}
function bucket(ob){
 const m=ob.market;
 if(!m||!finite(m.r4)||!finite(m.r1)||!finite(m.r3))
   throw Error("V19_BAD_MARKET_REGIME");
 const events=ob.events??[];
 if(!Array.isArray(events))throw Error("V19_BAD_EVENT_ARRAY");
 if(m.r4< -1.5|| (finite(m.rv)&&m.rv>3)||
    (finite(m.dd)&&m.dd< -5)||
    events.some(e=>e?.family==="G05"||e?.family==="G06"))
  return "STRESS";
 if(m.r4>0&&m.r1>0)return "RALLY";
 return "QUIET";
}
function riskTail(values,alpha){
 if(values.length===0)return {cvar:null,mean:null,vol:null};
 const a=[...values].sort((x,y)=>y-x),
   k=Math.max(1,Math.ceil((1-alpha)*a.length));
 const cvar=a.slice(0,k).reduce((s,v)=>s+v,0)/k;
 const avg=a.reduce((s,v)=>s+v,0)/a.length;
 const variance=a.reduce((s,v)=>s+(v-avg)*(v-avg),0)/a.length;
 return {cvar,mean:avg,vol:Math.sqrt(variance)};
}
function estimate(s,regime){
 const risk=s.risk,c=s.config,global=risk.all;
 if(global.length<c.minTailObservations)
  return {ready:false,regime,n:global.length,conditional:false,
    cvar:null,upper:null,mean:null};
 const local=risk.buckets[regime],useLocal=local.length>=c.minConditionalObservations;
 const samples=useLocal?local:global;
 const t=riskTail(samples,c.alpha);
 // Empirical conditional CVaR is one-step tail loss of GOLD.
 // Confidence penalty is a heuristic ambiguity cushion, NOT a
 // guaranteed statistical coverage interval or path-CVaR bound.
 const upper=t.cvar+c.ambiguityScale*t.vol/
   Math.sqrt(Math.max(1,Math.ceil((1-c.alpha)*samples.length)));
 return {ready:true,regime,n:samples.length,conditional:useLocal,
    cvar:t.cvar,upper,mean:t.mean,vol:t.vol};
}
function quoteState(s){
 return {capital:s.portfolio.nav,peak:s.portfolio.peak,
  currentDrawdownPct:s.portfolio.drawdownPct,
  maxDrawdownPct:s.portfolio.maxDrawdownPct,
  position:s.portfolio.position,feesPaidDollars:s.portfolio.feeDollars,
  trades:s.portfolio.trades};
}
function signal(s,ob){
 if(!s||s.version!==VERSION)throw Error("V19_INCOMPATIBLE_STATE");
 if(!ob||ob.position!==s.portfolio.position)
  throw Error("V19_POSITION_DISAGREEMENT");
 if(s.pendingContext!==null)throw Error("V19_PENDING_SIGNAL");
 const which=bucket(ob),tail=estimate(s,which),
   dd=s.portfolio.drawdownPct,config=s.config,p=ob.position;
 // Risk calculations inspect only completed, accepted checkpoint labels.
 // Even if a severe REAL crash is observed later, it is unavailable here.
 const adverse=(ob.market.r4<0||ob.market.r1<0||which==="STRESS");
 const recovery=ob.market.r4>0&&ob.market.r1>0&&which!=="STRESS";
 const pressure=tail.ready?Math.max(0,tail.upper-config.maxTailLossPct):0;
 const adjustedRisk=tail.ready?config.riskPenalty*pressure:0;
 const projected=dd+(tail.ready?tail.upper:0);
 const hardLoss=config.maxDrawdownPct!==null&&dd>=config.maxDrawdownPct;
 const budgetAtRisk=config.maxDrawdownPct!==null&&tail.ready&&adverse&&
   projected>=config.maxDrawdownPct-config.stopBufferPct&&
   tail.upper>config.maxTailLossPct;
 // Path-dependent drawdown is a constraint while GOLD is carried.
 // Once CASH, wealth cannot rebound without buying again: keeping
 // the old drawdown as a permanent ENTRY ban creates a mathematical
 // absorbing-state deadlock. CASH uses *prospective regime risk* and
 // independently observed recovery, NOT its historical underwater NAV.
 const exitGuard= config.useRiskPolicy&&p==="GOLD"&&(hardLoss||budgetAtRisk);
 const entryGuard=config.useRiskPolicy&&p==="CASH"&&
   which==="STRESS"&&adverse&&tail.ready&&
   tail.upper>config.maxTailLossPct;
 // Compute base advice in a cloned state first. Rejected inputs
 // do not partially mutate the parent learning engine.
 const fork=Core.restore(Core.save(s.core));
 const base=Core.signal(fork,ob);
 let proposed=base.action,reason="DOUBLE_Q",riskEdge=base.actionGap;
 if(config.useRiskPolicy){
  if(p==="GOLD"){
   riskEdge+=adjustedRisk;
   if(exitGuard){proposed="SELL";reason=hardLoss?"DRAW_DOWN_GUARD":"TAIL_BUDGET_GUARD";}
   else if(base.readiness){
     proposed=riskEdge>0?"SELL":"WAIT";
     reason=proposed==="SELL"?"RISK_ADJUSTED_EXIT":"RISK_ADJUSTED_HOLD";
   }
  }else{
   riskEdge-=adjustedRisk;
   if(entryGuard){proposed="WAIT";reason="RISK_BUDGET_BLOCK";}
   else if(s.risk.afterForcedExit&&!recovery){proposed="WAIT";reason="RECOVERY_NOT_CONFIRMED";}
   else if(s.risk.afterForcedExit&&s.risk.recoveryCount<config.recoveryObservations){
     proposed="WAIT";reason="RECOVERY_OBSERVATIONS";
   }else if(riskEdge<=0){proposed="WAIT";reason="AMBIGUOUS_ENTRY";}
  }
 }
 if(proposed!=="WAIT"&&!base.readiness&&!hardLoss)proposed="WAIT";
 const choice=proposed==="WAIT"?"KEEP":"SWITCH";
 fork.pending.choice=choice;
 fork.pending.reason=reason;
 s.core=fork;
 s.pendingContext={bucket:which,position:p,asof:base.at,forced:
   proposed==="SELL"&&reason!=="DOUBLE_Q"&&reason!=="RISK_ADJUSTED_EXIT"};
 if(proposed==="SELL"&&(reason.startsWith("TAIL_")||reason==="DRAW_DOWN_GUARD"))
  s.audit.forcedExits++;
 if(p==="CASH"&&base.action==="BUY"&&proposed==="WAIT")s.audit.blockedEntries++;
 if(base.action!==proposed)s.audit.riskAbstains++;else s.audit.normalDecisions++;
 return {version:VERSION,at:base.at,id:base.id,action:proposed,
  reason,baseAction:base.action,position:p,expectedPosition:
    proposed==="WAIT"?p:p==="CASH"?"GOLD":"CASH",
  baseAdvantage:base.actionGap,riskAdjustedAdvantage:riskEdge,
  tailEstimate:tail,drawdownPct:dd,projectedOneIntervalLossPct:projected,
  hardLoss,guardHot:p==="GOLD"?exitGuard:entryGuard,
  exitGuard,entryGuard,learnedIntervals:s.core.learned,
  ordersSent:0,noLiveOrders:true,notValidatedFinancialForecast:true};
}
function appendLoss(a,v,maxLen){
 a.push(v);if(a.length>maxLen)a.shift();
}
function quote(s,o){
 if(!s||s.version!==VERSION)throw Error("V19_INCOMPATIBLE_STATE");
 if(!s.pendingContext){
  const result=Core.quote(s.core,o);
  if(result.fill)throw Error("V19_UNEXPECTED_UNSUPERVISED_FILL");
  return {base:result,fill:null,portfolio:quoteState(s),ordersSent:0};
 }
 // V18 enforces datetime/fee/extreme-quote corroboration.
 const result=Core.quote(s.core,o);
 if(!result.fill){
   if(result.expired)s.pendingContext=null;
   return {base:result,fill:null,portfolio:quoteState(s),ordersSent:0};
 }
 const context=s.pendingContext,p=s.portfolio,c=s.config,r=s.risk;
 const entryPrice=o.price,f=result.fill,fee=f.feeLegIfSwitched;
 if(!finite(entryPrice)||entryPrice<=0||!finite(fee)||fee<0||fee>=.1)
  throw Error("V19_BAD_VERIFIED_FILL");
 // Learn only as of this completed checkpoint, from the previous
 // accepted checkpoint's frozen conditional regime.
 if(r.lastFill){
  const goldLog=100*(Math.log(entryPrice)-Math.log(r.lastFill.price));
  const loss=Math.max(0,-goldLog);
  appendLoss(r.all,loss,c.tailWindow);
  appendLoss(r.buckets[r.lastFill.bucket],loss,c.tailWindow);
  r.learnedReturns++;s.audit.regimeReturnLabels++;
  if(loss>c.maxTailLossPct)r.tailMisses++;
 }
 if(f.suggestedAction==="BUY"){
  if(p.position!=="CASH")throw Error("V19_DOUBLE_BUY");
  const spend=p.cash;
  p.units=spend*(1-fee)/entryPrice;p.cash=0;
  p.feeDollars+=spend*fee;p.trades++;
 }else if(f.suggestedAction==="SELL"){
  if(p.position!=="GOLD")throw Error("V19_DOUBLE_SELL");
  const proceeds=p.units*entryPrice;
  p.cash=proceeds*(1-fee);p.units=0;
  p.feeDollars+=proceeds*fee;p.trades++;
 }
 p.position=f.positionAfter;
 if(p.position!==s.core.virtualPosition)throw Error("V19_POSITION_SYNC_FAILURE");
 const markFee=s.core.feeKnowledge.lastKnown;
 p.nav=p.cash+p.units*entryPrice*(1-markFee);
 p.peak=Math.max(p.peak,p.nav);
 p.drawdownPct=100*(1-p.nav/p.peak);
 p.maxDrawdownPct=Math.max(p.maxDrawdownPct,p.drawdownPct);
 p.realizedCheckpointCount++;
 if(context.forced&&f.suggestedAction==="SELL"){
  r.afterForcedExit=true;r.recoveryCount=0;
 }else if(r.afterForcedExit&&p.position==="CASH"){
  r.recoveryCount+=(context.bucket==="RALLY"?1:0);
 }else if(f.suggestedAction==="BUY"){
  r.afterForcedExit=false;r.recoveryCount=0;
 }
 if(p.drawdownPct>c.maxDrawdownPct)s.audit.postCrashGapWarnings++;
 r.lastFill={price:entryPrice,at:f.at,bucket:context.bucket};
 s.pendingContext=null;
 return {version:VERSION,fill:f,baseFeedback:result.update,
   portfolio:quoteState(s),tail:estimate(s,context.bucket),
   ordersSent:0,gapDrawdownBreached:p.drawdownPct>c.maxDrawdownPct,
   riskSupervisorCannotGuaranteeNoGapLoss:true};
}
function save(s){return deep(s);}
function restore(payload){
 const raw=typeof payload==="string"?JSON.parse(payload):payload;
 if(!raw||raw.version!==VERSION)throw Error("V19_BAD_CHECKPOINT_VERSION");
 const s=deep(raw);s.config=config(s.config);
 s.core=Core.restore(s.core);
 const p=s.portfolio,r=s.risk;
 if(!p||!r||!s.audit||!["CASH","GOLD"].includes(p.position)||
    s.core.virtualPosition!==null&&p.position!==s.core.virtualPosition||
    !finite(p.cash)||p.cash<0||!finite(p.units)||p.units<0||
    p.position==="CASH"&&p.units!==0||p.position==="GOLD"&&p.cash!==0||
    !finite(p.nav)||p.nav<=0||!finite(p.peak)||p.peak<p.nav||
    !finite(p.drawdownPct)||p.drawdownPct<0||p.drawdownPct>100||
    !finite(p.maxDrawdownPct)||p.maxDrawdownPct<p.drawdownPct||
    !finite(p.feeDollars)||p.feeDollars<0||
    !Number.isInteger(p.trades)||p.trades<0||
    !Array.isArray(r.all)||!r.buckets||
    !["STRESS","RALLY","QUIET"].every(k=>Array.isArray(r.buckets[k]))||
    ![r.all,...Object.values(r.buckets)].every(a=>a.length<=s.config.tailWindow&&
       a.every(v=>finite(v)&&v>=0))||
    !Number.isInteger(r.learnedReturns)||r.learnedReturns<0||
    !Number.isInteger(r.recoveryCount)||r.recoveryCount<0||
    typeof r.afterForcedExit!=="boolean"||
    (s.pendingContext!==null&&!["CASH","GOLD"].includes(s.pendingContext.position))||
    (!!s.pendingContext)!=(!!s.core.pending))
    throw Error("V19_CORRUPT_PORTFOLIO_OR_RISK");
 return s;
}
module.exports={VERSION,create,signal,quote,save,restore,riskTail,estimate};
