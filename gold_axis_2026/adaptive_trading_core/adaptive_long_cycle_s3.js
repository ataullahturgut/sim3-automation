"use strict";
/**
 * M3/M4/M5 inside the existing S1-S2-S3 mathematical CORE. Research only.
 * 14 and 56 CALENDAR DAY horizons follow the old SENTEZ finding, not optimized
 * against Jan2023. Labels enter learning only at/after target maturity.
 * Samples: 14d anchors >=14d apart; 56d anchors >=28d apart.
 * The 56d labels can still overlap; effectiveN is at most ceil(n/2).
 * The initial LONG criterion has no scientific profitability validation.
 */
const VERSION="KAVIS_M3_M4_LONG_CYCLE_RESEARCH_V1_20261016";
const DAY=86400000,FEE=.008,HORIZONS=[14,56];
const clone=x=>JSON.parse(JSON.stringify(x));
const clamp=(x,a,b)=>Math.min(b,Math.max(a,x));
const xs=g=>[1,g.trend,g.stress,clamp(g.drawdown/10,0,1)];
const dot=(w,x)=>w.reduce((sum,v,i)=>sum+v*x[i],0);
const finite=n=>typeof n==="number"&&Number.isFinite(n);
function stamp(date){const v=Date.parse(date+"T22:00:00Z");if(!Number.isFinite(v)||!(/^\d{4}-\d{2}-\d{2}$/.test(date)))throw Error("LONG_BAD_DATE");return v;}
function plus(t,n){return new Date(t+n*DAY).toISOString().slice(0,10);}
function create(){return {version:VERSION,last:null,pending:[],originDates:{14:null,56:null},
  cohorts:{},expertLoss:{
   global:{14:{n:0,ema:0},56:{n:0,ema:0}},
   state:{14:{n:0,ema:0},56:{n:0,ema:0}},
   gated:{14:{n:0,ema:0},56:{n:0,ema:0}}},
  gatedExperts:{
   14:{w:[0,0,0,0],g2:[1,1,1,1],n:0},
   56:{w:[0,0,0,0],g2:[1,1,1,1],n:0}},
  gated:{trend:0,stress:0,peak:0,drawdown:0},audit:{sessions:0,origin14:0,origin56:0,
    mature14:0,mature56:0,censored:0,missedUp:0,avoidedLoss:0,
    falseHold:0,validPredictions:0}};}
function key(state,h){return state+"#"+h;}
function estimate(s,state,h){
 const c=s.cohorts[key(state,h)],n=c?.n??0;
 const eff=c?.independentN??0,mean=n?c.mean:0;
 const variance=eff>1?c.independentM2/(eff-1):null;
 const stderr=variance===null?null:Math.sqrt(Math.max(0,variance)/eff);
 return {n,effectiveN:eff,mean:eff>=2?mean:null,stderr:eff>=2?stderr:null,
  positive:c?.positive??0,lastMaturedAt:c?.lastMaturedAt??null};
}
function combine(s,state,h){
 const g=estimate(s,"ALL",h),a=estimate(s,state,h),
   ge=s.expertLoss.global[h],se=s.expertLoss.state[h],
   learnt=s.gatedExperts[h],trained=learnt.n>=3,
   gatedPrediction=trained?dot(learnt.w,xs(s.gated)):null;
 const eligible=a.effectiveN>=3;
 if(g.effectiveN<3)return {ready:false,horizonDays:h,global:g,conditional:a,
   gatedPrediction,meanNetPct:null,stderrPct:null,conditionalWeight:0,
   gatedWeight:0};
 const wg=1/(1+Math.sqrt(Math.max(.1,ge.ema))),
   ws=eligible?1/(1+Math.sqrt(Math.max(.1,se.ema))):0,
   we=trained?1/(1+Math.sqrt(Math.max(.1,s.expertLoss.gated[h].ema))):0,
   den=wg+ws+we,conditionalWeight=ws/den,gatedWeight=we/den;
 return {ready:true,horizonDays:h,global:g,conditional:a,
   gatedPrediction,meanNetPct:g.mean*(wg/den)+(eligible?a.mean:0)*conditionalWeight+
     (trained?gatedPrediction:0)*gatedWeight,
   stderrPct:g.stderr*(1-gatedWeight),
   conditionalWeight,gatedWeight,
   note:"OVERLAPPING_LABELS_LONG_HORIZON_SHADOW"};
}
function updateGated(s,h,features,realizedNet){
 const a=s.gatedExperts[h],pred=dot(a.w,features),
   err=clamp(realizedNet-pred,-25,25);
 for(let i=0;i<features.length;i++){
   const grad=features[i],scale=1/Math.sqrt(a.g2[i]);
   a.w[i]=clamp(a.w[i]+.14*err*grad*scale,-40,40);
   a.g2[i]+=grad*grad;
 }
 a.n++;
}
function predict(s,state){
 if(s.version!==VERSION)throw Error("LONG_VERSION");
 const byHorizon=HORIZONS.map(h=>combine(s,state,h));
 if(byHorizon.every(x=>x.ready))s.audit.validPredictions++;
 return {state,trend:s.gated.trend,stress:s.gated.stress,
   drawdown:s.gated.drawdown,byHorizon,
   provenance:"MATURED_PRIOR_SESSIONS_NOT_CAUSAL_MACRO",scienceGate:"NOT_PROVEN"};
}
function record(s,state,h,net,originTs,date){
 const k=key(state,h),c=s.cohorts[k]??(s.cohorts[k]={
  n:0,mean:0,m2:0,independentN:0,independentMean:0,
  independentM2:0,lastIndependentOriginMs:null,positive:0,lastMaturedAt:null});
 c.n++;const delta=net-c.mean;c.mean+=delta/c.n;c.m2+=delta*(net-c.mean);
 if(c.lastIndependentOriginMs===null||originTs-c.lastIndependentOriginMs>=h*DAY){
  c.independentN++;const d=net-c.independentMean;
  c.independentMean+=d/c.independentN;
  c.independentM2+=d*(net-c.independentMean);
  c.lastIndependentOriginMs=originTs;
 }
 if(net>0)c.positive++;c.lastMaturedAt=date;
}
function feedback(s,expert,h,pred,net){
 if(pred===null||!finite(pred))return;
 const a=s.expertLoss[expert][h],loss=(pred-net)**2;
 a.ema=a.n===0?loss:.95*a.ema+.05*loss;a.n++;
}
function observe(s,{session,sourceId,price,phase,direction=0,availableAt,
    shadowHolding="CASH",shadowProposal="KEEP"}){
 if(s.version!==VERSION)throw Error("LONG_VERSION");
 const t=stamp(session);
 if(typeof sourceId!=="string"||!sourceId||!finite(price)||price<=0||
   typeof availableAt!=="string"||!Number.isFinite(Date.parse(availableAt))||
   Date.parse(availableAt)>t||![-1,0,1].includes(direction))
   throw Error("LONG_BAD_SESSION");
 if(s.last&&t<=s.last.t)throw Error("LONG_NONMONOTONIC_SESSION");
 if(s.last&&s.last.sourceId!==sourceId){
   s.audit.censored+=s.pending.length;s.pending=[];
   s.originDates={14:null,56:null};
   s.gated={trend:0,stress:0,peak:0,drawdown:0};
 }
 // As-of close: mature previous labels before using them for any forecast.
 const remaining=[];
 for(const p of s.pending){
  if(session<p.due){remaining.push(p);continue;}
  // The first daily session within 4 calendar days after scheduled target
  // is accepted (weekend and 1-day holiday). Otherwise censor.
  if(t-stamp(p.due)>4*DAY){s.audit.censored++;continue;}
  const net=100*(Math.log(price/p.price)+2*Math.log(1-FEE));
  record(s,"ALL",p.h,net,p.originTs,session);
  record(s,p.state,p.h,net,p.originTs,session);
  if(p.forecast){
   feedback(s,"global",p.h,p.forecast.global.mean,net);
   feedback(s,"state",p.h,p.forecast.conditional.mean,net);
   feedback(s,"gated",p.h,p.forecast.gatedPrediction,net);
  }
  updateGated(s,p.h,p.originFeatures,net);
  if(p.h===14)s.audit.mature14++;else s.audit.mature56++;
  if(p.shadowHolding==="CASH"&&p.shadowProposal!=="BUY"){
   if(net>0)s.audit.missedUp++;else s.audit.avoidedLoss++;
  }else if(p.shadowHolding==="GOLD"&&net<0)s.audit.falseHold++;
 }
 s.pending=remaining;
 // LSTM-inspired slow trend persistence, not a trained LSTM and no future data.
 if(s.last&&s.last.sourceId===sourceId){
  const ret=Math.log(price/s.last.price);
  const shock=Math.min(1,Math.abs(ret)/.04);
  const gate=.94-.34*shock;
  s.gated.trend=gate*s.gated.trend+(1-gate)*Math.tanh(ret*30);
  s.gated.stress=.85*s.gated.stress+.15*shock;
 }
 s.gated.peak=Math.max(s.gated.peak,price);
 s.gated.drawdown=s.gated.peak>0?100*(1-price/s.gated.peak):0;
 const coarse=(direction===1?"UP":direction===-1?"DOWN":"NEUTRAL");
 const state=coarse+(s.gated.trend>0.1?"_PERSIST_UP":s.gated.trend<-.1?
   "_PERSIST_DOWN":"_UNCERTAIN");
 // Without a sufficient GLOBAL learned label, don't create false state alpha.
 const snapshot=predict(s,state);
 for(const h of HORIZONS){
  const prev=s.originDates[h],minGap=(h===14?14:28)*DAY;
  if(prev!==null&&t-prev<minGap)continue;
  const f=snapshot.byHorizon.find(v=>v.horizonDays===h);
  s.pending.push({state,h,price,sourceId,originTs:t,
    due:plus(t,h),forecast:f,originFeatures:xs(s.gated),
    shadowHolding,shadowProposal});
  s.originDates[h]=t;
  if(h===14)s.audit.origin14++;else s.audit.origin56++;
 }
 s.last={t,session,price,sourceId,state};s.audit.sessions++;
 return {asof:new Date(t).toISOString(),state,matured:s.audit.mature14+s.audit.mature56,
  pending:s.pending.length,forecast:snapshot,tradeAllowed:false};
}
function action(s,holding,{minGlobalEffective=3}={}){
 const state=s.last?.state??"NEUTRAL_UNCERTAIN",f=predict(s,state),
 short=f.byHorizon.find(x=>x.horizonDays===14),
 long=f.byHorizon.find(x=>x.horizonDays===56);
 if(!long.ready||long.global.effectiveN<minGlobalEffective||
    !short.ready)return{action:"ABSTAIN",reason:"LONG_MATURED_SUPPORT_INSUFFICIENT",forecast:f};
 // The fee is already charged twice in outcomes, never charged as a third
 // signal penalty. Require a positive lower range to enter; bearish
 // portfolio switches need sufficient evidence of holding loss.
 const lo=long.meanNetPct-.5*long.stderrPct;
 const shortRisk=short.meanNetPct+.5*short.stderrPct;
 const act=holding==="CASH"?(lo>0&&f.trend>-.05?"BUY":"KEEP"):
   (shortRisk< -2.2&&f.trend<0?"SELL":"KEEP");
 return{action:act,reason:act==="BUY"?"LONG56_MATURED_NET_ADVANTAGE":
   act==="SELL"?"SHORT14_MATURED_DOWNSIDE":
   "LONG_TERM_POSITION_CONTINUATION_OR_WEAK_EDGE",forecast:f};
}
function summary(s){return {version:VERSION,trainedOn:"COMPLETED_SESSIONS_ONLY",
  audit:clone(s.audit),gated:clone(s.gated),expertLoss:clone(s.expertLoss),
  gatedExperts:Object.fromEntries(Object.entries(s.gatedExperts).map(([k,v])=>[k,
    {n:v.n,weights:v.w}])),
  cohorts:Object.fromEntries(Object.entries(s.cohorts).map(([k,v])=>[k,
   {n:v.n,effectiveN:v.independentN,meanNetPct:v.mean,
    lastMaturedAt:v.lastMaturedAt}])),
  pendingLabels:s.pending.length,tradeAllowed:false,
  scienceGate:"NOT_PROVEN_NO_TRUE_BLIND_OR_BANK_EXECUTION"};}
function restore(v){const s=clone(v);
 if(s.version!==VERSION||!Array.isArray(s.pending)||!s.cohorts||!s.audit||
    !s.expertLoss||!s.gated||!s.gatedExperts)throw Error("LONG_BAD_CHECKPOINT");
 return s;}
module.exports={VERSION,HORIZONS,create,observe,predict,action,summary,restore};
