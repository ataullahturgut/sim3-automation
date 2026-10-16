"use strict";
/**
 * V20 R2: preregistered two independent self-financing shadow portfolios.
 * The R1 risk adviser does not control execution. V18 Double Q remains the
 * default decision source. Evidence is earned from continuous portfolio paths,
 * not cherry-picked one/two-bar switches with 100% round-trip fees each bar.
 *
 * riskMode=alert: risk budgets ONLY reported, never act.
 * riskMode=soft_penalty: bounded, conditional tail-risk Q score adjustment.
 * Risk specialist may override only after persistent positive shadow track
 * record. Not a hard max DD guarantee, backtest approval, or live trading.
 */
const R1=require("./v20_kavis_atlas_repaired");
const Core=require("./v18_kavis_dayaniqlilik");
const V="V20_R2_PARALLEL_SHADOW_PREREG_20261016";
const isNum=x=>typeof x==="number"&&Number.isFinite(x);
const deep=x=>JSON.parse(JSON.stringify(x));
const STATES=["CASH","GOLD"];
const MODES=["alert","soft_penalty"];
const windowSize=32,minEvidence=24,confidence=1.64;
function cfg(o={}){
 const riskMode=o.riskMode??"alert",lambda=o.riskPenaltyLambda??1;
 if(!MODES.includes(riskMode)||!isNum(lambda)||lambda<0||lambda>4)
  throw Error("R2_BAD_RISK_MODE");
 if(riskMode==="soft_penalty"&&
   !(isNum(o.maxDrawdownPct)&&o.maxDrawdownPct>1&&o.maxDrawdownPct<90))
  throw Error("R2_EXPLICIT_BUDGET_REQUIRED");
 return {riskMode,riskPenaltyLambda:lambda,
   maxDrawdownPct:o.maxDrawdownPct??null,
   portfolioWindow:windowSize,minimumEvidence:minEvidence,
   z:confidence};
}
function ledger(initial=100){
 return {position:"CASH",cash:initial,units:0,nav:initial,
  peak:initial,drawdownPct:0,maxDrawdownPct:0,
  feesPaid:0,trades:0,returns:[],lastNAV:initial};
}
function create(opts={}){
 const policy=cfg(opts),capital=opts.initialCapital??100;
 const inner=R1.create({...opts,useRiskPolicy:false,
   enforceEntryRiskBudget:false});
 const baseCore=Core.create(opts.core||{});
 return {version:V,policy,inner,baseCore,
   shadow:{base:ledger(capital),risk:ledger(capital),
    pending:null,relativeReturns:[],confirmedStreak:0,
    lastEvidence:null,completed:0},
   audit:{shadowTradesBase:0,shadowTradesRisk:0,
    warnings:0,softEntryVetoes:0,softExitDecisions:0,
    specialistEvaluations:0,specialistOverrides:0,
    shadowEvidenceBlocks:0}};
}
function family(ob){
 const m=ob.market;
 if(!m||!isNum(m.r4)||!isNum(m.r1)||!isNum(m.r3))
  throw Error("R2_INVALID_REGIME");
 const ev=ob.events??[];
 if(m.r4< -1.5||m.rv>3||m.dd< -5||
   ev.some(e=>e.family==="G05"||e.family==="G06"))return "STRESS";
 if(m.r4>0&&m.r1>0)return "RALLY";
 return "QUIET";
}
function rule(position,regime){
 if(regime==="STRESS")return position==="GOLD"?"SELL":"WAIT";
 if(regime==="RALLY")return position==="CASH"?"BUY":"WAIT";
 return "WAIT";
}
function apply(ledger,action,price,fee){
 if(!isNum(price)||price<=0||!isNum(fee)||fee<0||fee>=.1)
  throw Error("R2_BAD_VERIFIED_PRICE_OR_FEE");
 if(action==="BUY"){
   if(ledger.position!=="CASH")throw Error("R2_DOUBLE_BUY");
   const value=ledger.cash;
   ledger.units=value*(1-fee)/price;ledger.cash=0;
   ledger.feesPaid+=value*fee;ledger.trades++;ledger.position="GOLD";
 }else if(action==="SELL"){
   if(ledger.position!=="GOLD")throw Error("R2_DOUBLE_SELL");
   const gross=ledger.units*price;
   ledger.cash=gross*(1-fee);ledger.units=0;
   ledger.feesPaid+=gross*fee;ledger.trades++;ledger.position="CASH";
 }else if(action!=="WAIT")throw Error("R2_BAD_ACTION");
 const nav=ledger.cash+ledger.units*price*(1-fee);
 if(!isNum(nav)||nav<=0)throw Error("R2_BAD_NAV");
 const one=100*Math.log(nav/ledger.lastNAV);
 ledger.lastNAV=nav;ledger.nav=nav;
 ledger.returns.push(one);
 if(ledger.returns.length>4096)ledger.returns.shift();
 ledger.peak=Math.max(ledger.peak,nav);
 ledger.drawdownPct=100*(1-nav/ledger.peak);
 ledger.maxDrawdownPct=Math.max(ledger.maxDrawdownPct,ledger.drawdownPct);
 return one;
}
function evidence(data){
 if(data.length<minEvidence)return {ready:false,n:data.length,mean:null,lower:null,ess:null};
 const x=data.slice(-windowSize),n=x.length,
   avg=x.reduce((a,b)=>a+b,0)/n,
   var0=x.reduce((a,b)=>a+(b-avg)**2,0)/n;
 let cov=0;for(let i=1;i<n;i++)cov+=(x[i]-avg)*(x[i-1]-avg);
 const corr=var0>1e-12?Math.max(0,Math.min(.95,cov/(n-1)/var0)):0;
 // Positive serial correlation reduces effective N. No formal CI claim.
 const ess=Math.max(2,n*(1-corr)/(1+corr));
 const std=Math.sqrt(Math.max(.01,var0));
 const lower=avg-confidence*std/Math.sqrt(ess);
 return {ready:true,n,ess,mean:avg,lower,
   positive:lower>0};
}
function reconcile(inner,proposed,why){
 const choice=proposed==="WAIT"?"KEEP":"SWITCH";
 if(!inner.core.pending)throw Error("R2_NO_PENDING_CORE");
 inner.core.pending.choice=choice;
 inner.core.pending.reason=why;
 return proposed;
}
function decisionOf(s,ob){
 if(!s||s.version!==V||s.shadow.pending)
  throw Error("R2_BAD_STATE_OR_PENDING");
 if(ob?.position!==s.inner.portfolio.position)throw Error("R2_POSITION_MISMATCH");
 const fork=restore(save(s));
 const baseObs={...ob,position:fork.shadow.base.position};
 const r=R1.signal(fork.inner,ob);
 const b=Core.signal(fork.baseCore,baseObs);
 const regime=family(ob),advisor=rule(ob.position,regime);
 const proposedShadow=rule(fork.shadow.risk.position,regime);
 let act=r.baseAction,reason="V18_DOUBLE_Q",
   tail=R1.estimate(fork.inner,regime),penalty=0;
 const proof=fork.shadow.lastEvidence;
 const allowShadow=fork.shadow.confirmedStreak>=2&&
     proof?.ready===true&&proof.lower>0;
 if(fork.policy.riskMode==="soft_penalty"){
  if(tail.ready){
   const gap=Math.max(0,tail.upper-fork.inner.config.maxTailLossPct);
   penalty=Math.min(4,fork.policy.riskPenaltyLambda*gap*
       (15/fork.policy.maxDrawdownPct));
  }
  // A bounded risk-adjusted goal score, rather than a NAV peak
  // absorbing-state veto. Strong Q advantage can STILL admit a BUY.
  if(ob.position==="CASH"&&act==="BUY"&&r.baseAdvantage-penalty<=0){
    act="WAIT";reason="SOFT_TAIL_RISK_ENTRY";fork.audit.softEntryVetoes++;
  }else if(ob.position==="GOLD"&&act==="WAIT"&&
           r.baseAdvantage+penalty>0&&penalty>0&&allowShadow){
    act="SELL";reason="PROVEN_SOFT_RISK_EXIT";fork.audit.softExitDecisions++;
  }
  if(allowShadow&&advisor!==act){
    // Only after a complete fee-net, history-based expert comparison.
    // Advice is position-valid and never forced by old NAV underwater.
    act=advisor;reason="SHADOW_EXPERT_PROVEN";
    fork.audit.specialistOverrides++;
  }
 }
 reconcile(fork.inner,act,reason);
 const pending={regime,advisor,ruleAction:proposedShadow,
    baseAction:b.action,actualAction:act,asof:r.at,proof};
 fork.shadow.pending=pending;
 Object.assign(s,fork);
 return {version:V,at:r.at,action:act,baseAction:r.baseAction,
   specialistAction:advisor,provisionalRiskAction:proposedShadow,
   reason,conditionalTailUpper:tail.upper,feeNetShadowEvidence:proof,
   shadowConfirmed:allowShadow,penalty,ordersSent:0,
   riskMode:s.policy.riskMode,
   noHardDrawdownGuarantee:true};
}
function complete(s,q){
 if(!s||s.version!==V)throw Error("R2_BAD_VERSION");
 const c=restore(save(s));
 const a=R1.quote(c.inner,q);
 const b=Core.quote(c.baseCore,q);
 if(!a.fill){
  if(b.fill)throw Error("R2_INCONSISTENT_SHADOW_FILL");
  if(a.base?.expired)c.shadow.pending=null;
  Object.assign(s,c);
  return {fill:null,base:a,ordersSent:0};
 }
 if(!b.fill||!c.shadow.pending)throw Error("R2_SHADOW_FILL_REQUIRED");
 const price=q.price,fee=c.inner.core.feeKnowledge.lastKnown;
 const x=apply(c.shadow.base,b.fill.suggestedAction,price,fee);
 const y=apply(c.shadow.risk,c.shadow.pending.ruleAction,price,fee);
 c.audit.shadowTradesBase=c.shadow.base.trades;
 c.audit.shadowTradesRisk=c.shadow.risk.trades;
 const delta=y-x;
 c.shadow.relativeReturns.push(delta);
 if(c.shadow.relativeReturns.length>windowSize)
   c.shadow.relativeReturns.shift();
 const e=evidence(c.shadow.relativeReturns);
 if(e.ready&&e.lower>0)c.shadow.confirmedStreak++;
 else c.shadow.confirmedStreak=0;
 c.shadow.lastEvidence=e;c.shadow.completed++;
 c.audit.specialistEvaluations++;
 if(c.policy.maxDrawdownPct!==null&&
    a.portfolio.currentDrawdownPct>c.policy.maxDrawdownPct)c.audit.warnings++;
 c.shadow.pending=null;
 Object.assign(s,c);
 return {fill:a.fill,portfolio:a.portfolio,
  shadow:{base:deep(s.shadow.base),risk:deep(s.shadow.risk),
    evidence:e,confirmedStreak:s.shadow.confirmedStreak},
  ordersSent:0,breachIsWarningOnly:true,
  riskMode:s.policy.riskMode};
}
function save(s){return deep(s);}
function restore(v){
 const s=deep(typeof v==="string"?JSON.parse(v):v);
 if(s.version!==V)throw Error("R2_INVALID_CHECKPOINT_VERSION");
 s.policy=cfg(s.policy);
 s.inner=R1.restore(s.inner);
 s.baseCore=Core.restore(s.baseCore);
 if(!s.shadow||!s.audit||!Array.isArray(s.shadow.relativeReturns)||
   s.shadow.relativeReturns.length>windowSize||
   s.shadow.relativeReturns.some(v=>!isNum(v))||
   !Number.isInteger(s.shadow.confirmedStreak)||
   s.shadow.confirmedStreak<0||
   s.shadow.pending&&!["CASH","GOLD"].includes(s.inner.portfolio.position))
    throw Error("R2_CORRUPT_SHADOW_STATE");
 for(const x of [s.shadow.base,s.shadow.risk]){
  if(!x||!STATES.includes(x.position)||
   !isNum(x.cash)||x.cash<0||!isNum(x.units)||x.units<0||
   x.position==="CASH"&&x.units!==0||
   x.position==="GOLD"&&x.cash!==0||
   !isNum(x.nav)||x.nav<=0||!isNum(x.peak)||x.peak<x.nav||
   !isNum(x.lastNAV)||x.lastNAV<=0||
   !Number.isInteger(x.trades)||x.trades<0||
   !isNum(x.feesPaid)||x.feesPaid<0||
   !Array.isArray(x.returns)||x.returns.length>4096||
   x.returns.some(v=>!isNum(v)))
    throw Error("R2_CORRUPT_LEDGER");
 }
 return s;
}
module.exports={VERSION:V,create,signal:decisionOf,quote:complete,
  save,restore,evidence,apply,rule};
