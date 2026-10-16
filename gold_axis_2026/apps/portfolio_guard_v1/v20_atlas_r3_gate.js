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
const V="V20_R3_BLOCK_GATE_PREREG_20261016";
const isNum=x=>typeof x==="number"&&Number.isFinite(x);
const deep=x=>JSON.parse(JSON.stringify(x));
const STATES=["CASH","GOLD"];
const MODES=["alert"],GATES=["off","gated"];
const BLOCK=16,MIN_BLOCKS=8,KEEP_HISTORY=8192,MIN_SAMPLES=BLOCK*MIN_BLOCKS;
const Z=1.64,LAMBDA=0,ETA=0;
function cfg(o={}){
 const riskMode=o.riskMode??"alert",shadowGate=o.shadowGate??"off",
   threshold=o.gateThreshold??null,limit=o.maxDrawdownPct??null;
 if(!MODES.includes(riskMode))throw Error("R3_CONSTRAINED_R4_ONLY");
 if(!GATES.includes(shadowGate))throw Error("R3_INVALID_GATE_MODE");
 if(limit!==null&&(!isNum(limit)||limit<=1||limit>=90))
   throw Error("R3_INVALID_ALERT_LIMIT");
 if(shadowGate==="gated"&&(!isNum(threshold)||threshold<0||threshold>12))
   throw Error("R3_GATE_NOT_CALIBRATED");
 if(threshold!==null&&(!isNum(threshold)||threshold<0||threshold>12))
   throw Error("R3_INVALID_THRESHOLD");
 return {riskMode,shadowGate,gateThreshold:threshold,
   maxDrawdownPct:limit,
   riskPenaltyLambda:LAMBDA,dualAscentEta:ETA,
   block:BLOCK,minBlocks:MIN_BLOCKS,z:Z};
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
    pending:null,relativeReturns:[],acceptedIndices:[],confirmedStreak:0,
    lastEvidence:null,gateOpen:false,completed:0,eligibleCompleted:0},
   audit:{shadowTradesBase:0,shadowTradesRisk:0,
    warnings:0,softEntryVetoes:0,softExitDecisions:0,
    specialistEvaluations:0,specialistOverrides:0,
    shadowEvidenceBlocks:0,gateOpens:0,gateCloses:0,gateTicks:0}};
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
function blockEvidence(rel){
 const nB=Math.floor(rel.length/BLOCK);
 if(nB<MIN_BLOCKS)return {ready:false,nBlocks:nB,t:0,blockSums:[]};
 const blocks=[];
 for(let b=nB-MIN_BLOCKS;b<nB;b++){
  let s=0;for(let j=b*BLOCK;j<(b+1)*BLOCK;j++)s+=rel[j];
  blocks.push(s);
 }
 const mean=blocks.reduce((a,b)=>a+b,0)/MIN_BLOCKS;
 const v=blocks.reduce((a,b)=>a+(b-mean)**2,0)/(MIN_BLOCKS-1);
 const sd=Math.sqrt(v);
 const t=sd<1e-9?(mean>0?12:mean<0?-12:0):
   Math.max(-12,Math.min(12,mean/(sd/Math.sqrt(MIN_BLOCKS)+1e-9)));
 return {ready:true,nBlocks:nB,t,mean,sd,blockSums:blocks,
   lastTwoNegative:blocks.at(-1)<0&&blocks.at(-2)<0};
}
function reconstruct(rel,T){
 let open=false,opens=0,closes=0,prevQualified=false,streak=0,evidence=null;
 const points=[];
 for(let n=MIN_SAMPLES;n<=rel.length;n+=BLOCK){
  const e=blockEvidence(rel.slice(0,n)),qualified=T!==null&&e.t>=T;
  const next= open?
    !(e.t<0||e.lastTwoNegative):
    (prevQualified&&qualified);
  if(next&&!open)opens++;
  if(!next&&open)closes++;
  open=next;prevQualified=qualified;
  streak=qualified?streak+1:0;
  evidence=e;
  points.push({n,t:e.t,blockSum:e.blockSums.at(-1),gateOpen:open});
 }
 return {gateOpen:open,confirmedStreak:streak,lastEvidence:evidence,
  gates:points,opens,closes,maxPairT:points.length<2?null:
    Math.max(...points.slice(1).map((e,i)=>Math.min(points[i].t,e.t)))};
}
function evidence(data){return blockEvidence(data);}
function reconcile(inner,proposed,why){
 const choice=proposed==="WAIT"?"KEEP":"SWITCH";
 if(!inner.core.pending)throw Error("R2_NO_PENDING_CORE");
 inner.core.pending.choice=choice;
 inner.core.pending.reason=why;
 return proposed;
}
function positionAfter(position,action){
 if(action==="WAIT")return position;
 if(action==="BUY")return "GOLD";
 if(action==="SELL")return "CASH";
 throw Error("R3_INVALID_ACTION");
}
function decisionOf(s,ob){
 if(!s||s.version!==V||s.shadow.pending)throw Error("R3_BAD_PENDING");
 if(ob?.position!==s.inner.portfolio.position)throw Error("R3_POSITION_MISMATCH");
 const fork=restore(save(s));
 const baseObs={...ob,position:fork.shadow.base.position};
 const b=Core.signal(fork.baseCore,baseObs);
 const r=R1.signal(fork.inner,ob),regime=family(ob);
 const ruleAction=rule(fork.shadow.risk.position,regime);
 const target=positionAfter(fork.shadow.risk.position,ruleAction);
 const proof=fork.shadow.lastEvidence;
 const gateActive=fork.policy.shadowGate==="gated"&&fork.shadow.gateOpen;
 let act=r.baseAction,reason="V18_DOUBLE_Q";
 if(gateActive){
   const aligned=ob.position===target?"WAIT":target==="GOLD"?"BUY":"SELL";
   if(aligned!==act){
     act=aligned;reason="R3_SHADOW_TARGET_ALIGN";
     fork.audit.specialistOverrides++;
   }
 }
 reconcile(fork.inner,act,reason);
 fork.shadow.pending={asof:r.at,regime,ruleAction,
   ruleTarget:target,gateWasOpen:gateActive,baseAction:b.action,actualAction:act};
 Object.assign(s,fork);
 return {version:V,at:r.at,action:act,baseAction:r.baseAction,
   shadowGate:s.policy.shadowGate,riskMode:s.policy.riskMode,
   riskAlertOnly:true,proof,gateActive,shadowTarget:target,
   pendingShadowAction:ruleAction,reason,ordersSent:0};
}
function complete(s,q){
 if(!s||s.version!==V)throw Error("R3_BAD_VERSION");
 const c=restore(save(s));
 const a=R1.quote(c.inner,q),b=Core.quote(c.baseCore,q);
 if(!a.fill){
  if(b.fill)throw Error("R3_INCONSISTENT_SHADOW_FILL");
  if(a.base?.expired)c.shadow.pending=null;
  Object.assign(s,c);
  return {fill:null,base:a,ordersSent:0};
 }
 if(!b.fill||!c.shadow.pending)throw Error("R3_SHADOW_FILL_REQUIRED");
 const price=q.price,fee=c.inner.core.feeKnowledge.lastKnown;
 const x=apply(c.shadow.base,b.fill.suggestedAction,price,fee);
 const y=apply(c.shadow.risk,c.shadow.pending.ruleAction,price,fee);
 const old=c.shadow.gateOpen;
 if(c.shadow.pending.gateWasOpen &&
   c.inner.portfolio.position!==c.shadow.risk.position)
   throw Error("R3_SHADOW_ALIGNMENT_FAILED");
 c.audit.shadowTradesBase=c.shadow.base.trades;
 c.audit.shadowTradesRisk=c.shadow.risk.trades;
 // Only matured, valid adjacent bank checkpoints count. First quote
 // is legitimate initialization (includes only real shadow entry fee).
 const valid=c.shadow.completed===0||
   (a.baseFeedback?.accepted===true&&b.update?.accepted===true);
 if(valid){
   const delta=y-x;
   c.shadow.relativeReturns.push(delta);
   c.shadow.acceptedIndices.push(c.shadow.base.returns.length-1);
   if(c.shadow.relativeReturns.length>KEEP_HISTORY){
     c.shadow.relativeReturns.shift();c.shadow.acceptedIndices.shift();
   }
   c.shadow.eligibleCompleted++;
 }else{
   // Never silently bridge stale/asof-invalid checkpoint into the
   // evidence stream. Block eligibility restarts after a data gap.
   c.shadow.relativeReturns=[];c.shadow.acceptedIndices=[];
 }
 const e=reconstruct(c.shadow.relativeReturns,c.policy.gateThreshold);
 c.shadow.gateOpen=e.gateOpen;
 c.shadow.confirmedStreak=e.confirmedStreak;
 c.shadow.lastEvidence=e.lastEvidence;
 c.audit.gateTicks=e.gates.length;
 if(c.shadow.gateOpen&&!old)c.audit.gateOpens++;
 if(!c.shadow.gateOpen&&old)c.audit.gateCloses++;
 c.shadow.completed++;c.audit.specialistEvaluations++;
 if(c.policy.maxDrawdownPct!==null&&
   a.portfolio.currentDrawdownPct>c.policy.maxDrawdownPct)c.audit.warnings++;
 const gateWasOpen=c.shadow.pending.gateWasOpen;
 c.shadow.pending=null;
 Object.assign(s,c);
 return {fill:a.fill,portfolio:a.portfolio,ordersSent:0,gateWasOpen,
   gateOpen:s.shadow.gateOpen,blockEvidence:s.shadow.lastEvidence,
   shadow:{base:deep(s.shadow.base),risk:deep(s.shadow.risk)}};
}
function save(s){return deep(s);}
function restore(v){
 const s=deep(typeof v==="string"?JSON.parse(v):v);
 if(s?.version!==V)throw Error("R3_INVALID_CHECKPOINT_VERSION");
 s.policy=cfg(s.policy);
 s.inner=R1.restore(s.inner);s.baseCore=Core.restore(s.baseCore);
 const sh=s.shadow,au=s.audit;
 if(!sh||!au||!Array.isArray(sh.relativeReturns)||
   !Array.isArray(sh.acceptedIndices)||
   sh.relativeReturns.length!==sh.acceptedIndices.length||
   sh.relativeReturns.length>KEEP_HISTORY||
   sh.relativeReturns.some(v=>!isNum(v))||
   sh.acceptedIndices.some((v,i)=>!Number.isInteger(v)||v<0||
     (i>0&&v<=sh.acceptedIndices[i-1]))||
   !Number.isInteger(sh.completed)||sh.completed<0||
   !Number.isInteger(sh.eligibleCompleted)||sh.eligibleCompleted<0||
   !Object.values(au).every(v=>Number.isInteger(v)&&v>=0)||
   (sh.pending!==null&&(!sh.pending||
       typeof sh.pending.asof!=="string"||
       !["WAIT","BUY","SELL"].includes(sh.pending.ruleAction)||
       !["WAIT","BUY","SELL"].includes(sh.pending.actualAction)||
       !STATES.includes(sh.pending.ruleTarget)||
       !STATES.includes(s.inner.portfolio.position)||
       typeof sh.pending.gateWasOpen!=="boolean"||
       !["STRESS","RALLY","QUIET"].includes(sh.pending.regime)))||
   (!!sh.pending)!=(!!s.inner.pendingContext)||
   (!!sh.pending)!=(!!s.baseCore.pending))
   throw Error("R3_CORRUPT_SHADOW_STATE");
 for(const x of [sh.base,sh.risk]){
  if(!x||!STATES.includes(x.position)||
   !isNum(x.cash)||x.cash<0||!isNum(x.units)||x.units<0||
   x.position==="CASH"&&x.units!==0||
   x.position==="GOLD"&&x.cash!==0||
   !isNum(x.nav)||x.nav<=0||!isNum(x.peak)||x.peak<x.nav||
   !isNum(x.lastNAV)||x.lastNAV<=0||
   !Number.isInteger(x.trades)||x.trades<0||
   !isNum(x.feesPaid)||x.feesPaid<0||
   !Array.isArray(x.returns)||x.returns.length>KEEP_HISTORY||
   x.returns.some(v=>!isNum(v)))
   throw Error("R3_CORRUPT_LEDGER");
 }
 // Verify evidence against the two independent ledgers, not untrusted
 // lastEvidence/gateOpen/confirmedStreak. Reconstruct all gates anew.
 if(sh.acceptedIndices.some((ix,j)=>
   ix>=sh.base.returns.length||ix>=sh.risk.returns.length||
   Math.abs(sh.relativeReturns[j]-
      (sh.risk.returns[ix]-sh.base.returns[ix]))>1e-8))
    throw Error("R3_FORGED_RELATIVE_RETURNS");
 const r=reconstruct(sh.relativeReturns,s.policy.gateThreshold);
 sh.lastEvidence=r.lastEvidence;
 sh.gateOpen=r.gateOpen;
 sh.confirmedStreak=r.confirmedStreak;
 return s;
}
module.exports={VERSION:V,create,signal:decisionOf,quote:complete,
 save,restore,evidence,blockEvidence,reconstruct,apply,rule,positionAfter};
