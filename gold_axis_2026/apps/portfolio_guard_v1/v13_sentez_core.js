"use strict";
/**
 * SENTEZ V13: original hybrid inspired by nonlinear ANN, Sugeno ANFIS,
 * and recurrent gated-state memories (NOT a full trained LSTM).
 *
 * 1) Pre-period trained ANN predicts fee-net 14-day returns.
 * 2) A recursive gated 3-timescale state carries regime evidence.
 * 3) Six adaptive Sugeno consequents map present state to 14/56-day fee-net labels.
 * 4) Experts' 14/56-day weights update ONLY from strictly matured outcomes.
 *
 * No model selection on 2026, no live trading, no future intrabar fills.
 */
const ANN=require("./v11_ann_mlp");
const {dataset,chronologicalTraining}=require("./v11_ann_research");
const {loadFullRows}=require("./v8_regret_engine");
const HR=3600000,DAY=24*HR,FEE=.008;
const FEATURE_COUNT=8,RULES=["UP","DOWN","STRESS","RECOVERY","RANGE","CARRY"];
const MIN_HISTORY=90;
const clamp=(a,lo,hi)=>Math.max(lo,Math.min(hi,a));
const sigmoid=x=>1/(1+Math.exp(-clamp(x,-20,20)));
const tanh=x=>Math.tanh(clamp(x,-12,12));
function softmax(v){
 const mx=Math.max(...v),e=v.map(x=>Math.exp(x-mx)),s=e.reduce((a,b)=>a+b,0);
 return e.map(x=>x/s);
}
function gatedState(old,feat){
 // LSTM-inspired gated recurrent dynamics: preserve previous state in
 // calm regimes and update aggressively after shocks. The gate behavior
 // is part of the defined policy, not falsely called a trained LSTM.
 const x1=clamp(feat[1]/6,-2,2),x3=clamp(feat[2]/10,-2,2),
  rv=clamp(feat[3]/3,0,4),shock=clamp(-feat[0]/3,0,3),
  nq=feat[10]?clamp(feat[8]/5,-2,2):0;
 const gateSlow=sigmoid(2.2-.55*rv-.8*shock);
 const gateFast=sigmoid(.5-.35*rv-.5*shock);
 const candidate=tanh(.55*x3+.30*x1+.15*nq);
 const trend=clamp(old.trend*gateSlow+(1-gateSlow)*candidate,-1,1);
 const stress=tanh(.78*old.stress+.65*shock+.15*rv- .18);
 const recovery=tanh(.7*old.recovery+(1-gateFast)*
   (x1-.55*x3)-.15*stress);
 return {trend,stress,recovery,gateSlow,gateFast};
}
function member(r,f,g){
 const t1=clamp(f[1]/6,-2,2),t3=clamp(f[2]/10,-2,2),
   vol=clamp(f[3]/3,0,3),dd=clamp(f[7]/6,-2,1),
   nq=f[10]?clamp(f[8]/5,-2,2):0;
 const x=[t1,t3,vol,dd,nq,g.trend,g.stress,g.recovery];
 const centers=[
   [.5,.6,.4,0,.2,.6,-.3,0],
   [-.6,-.6,.8,-.8,-.2,-.6,.5,-.2],
   [-1,-.6,1.2,-1.1,-1, -.5,1,.0],
   [.3,-.15,.7,-.4,.1,.1,.3,.7],
   [0,0,.25,-.1,0,0,0,0],
   [.4,1,.6,-.2,.2,.9,0,.0]];
 const dist=centers.map(c=>x.reduce((s,z,i)=>{
   const width=i===6?1.2:1.1;
   return s+((z-c[i])/width)**2;
 },0)/x.length);
 const w=softmax(dist.map(d=>-2*d));
 return {x,w,dist};
}
function create(){
 return {
   gated:{trend:0,stress:0,recovery:0},
   theta14:Array.from({length:6},()=>Array(FEATURE_COUNT+1).fill(0)),
   theta56:Array.from({length:6},()=>Array(FEATURE_COUNT+1).fill(0)),
   loss:{a14:{n:0,ema:9},f14:{n:0,ema:9},f56:{n:0,ema:18},g56:{n:0,ema:18}},
   residual:{count14:0,mae14:4,count56:0,mae56:6},
   labelsApplied14:0,labelsApplied56:0
 };
}
function fuzzyPredict(weights,rule,vec){
 const x=[1,...vec];
 return rule.reduce((sum,t,i)=>{
  return sum+weights[i]*t.reduce((s,v,j)=>s+v*x[j],0);
 },0);
}
function updateConsequents(theta,modelMember,target,pred,learningRate){
 const error=clamp(target-pred,-25,25),vec=[1,...modelMember.x];
 const norm=1+vec.reduce((s,v)=>s+v*v,0);
 for(let i=0;i<RULES.length;i++){
  const w=modelMember.w[i],rate=learningRate*w/norm;
  for(let j=0;j<vec.length;j++){
   theta[i][j]=clamp(theta[i][j]+rate*(error*vec[j]-
       .0001*theta[i][j]),-20,20);
  }
 }
}
function expertWeights(model,keys){
 let total=0;const weights={};
 for(const key of keys){
  const l=model.loss[key];
  const w=Math.exp(-Math.min(50,l.ema)/(keys.length===2?30:30));
  weights[key]=w;total+=w;
 }
 for(const key of keys)weights[key]/=total;
 return weights;
}
function predict(model,features,network,opts={}){
 // The no-memory control uses contemporaneous, non-recurrent features.
 // This preserves a genuinely executable policy rather than forcing CASH
 // merely because the recurrent state was deleted.
 const g=opts.disableGate?{
   trend:clamp(features[2]/10,-1,1),
   stress:clamp(-features[0]/3+features[3]/6,-1,1),
   recovery:clamp(features[1]/6-features[2]/10,-1,1)
 }:model.gated,m=member(null,features,g);
 const f14=fuzzyPredict(m.w,model.theta14,m.x);
 const f56=fuzzyPredict(m.w,model.theta56,m.x);
 // True pre-cutoff ANN head. No if not trained from >90 matured labels.
 let a14=null;
 if(network&&!opts.disableANN){
   a14=ANN.predict(network,features).net14;
 }
 const g56=clamp(14*g.trend+5*g.recovery-6*g.stress,-20,20);
 const weights14=expertWeights(model,a14==null?["f14"]:["a14","f14"]);
 const weights56=expertWeights(model,["f56","g56"]);
 const net14=a14==null?f14:weights14.a14*a14+weights14.f14*f14;
 const net56=opts.disableLong?null:
   (opts.disableFuzzy?g56:weights56.f56*f56+weights56.g56*g56);
 const short=opts.disableFuzzy?(a14??0):net14;
 return {net14:short,net56,f14,a14,f56,g56,weights14,weights56,
  regime:g,
  fuzzyWeights:m.w,member:m,
  uncertainty14:model.residual.mae14,uncertainty56:model.residual.mae56,
  n14:model.labelsApplied14,n56:model.labelsApplied56};
}
function applyOutcome(model,old,net,horizon,disableFuzzy=false){
 if(!(old.exitTs<net.now))throw Error("SENTEZ_OUTCOME_NOT_YET_KNOWN");
 const real=old.target;
 const losses=horizon===14?[["a14",old.forecast.a14],["f14",old.forecast.f14]]:
  [["f56",old.forecast.f56],["g56",old.forecast.g56]];
 for(const [key,prior] of losses){
  if(prior==null)continue;
  const l=model.loss[key],err=clamp(prior-real,-35,35);
  l.ema=l.n===0?err*err:.95*l.ema+.05*err*err;
  l.n++;
 }
 const residual=model.residual;
 if(horizon===14){
  residual.mae14=residual.count14===0?Math.abs(real-old.forecast.net14):
    .98*residual.mae14+.02*Math.abs(real-old.forecast.net14);
  residual.count14++;
  if(!disableFuzzy)updateConsequents(model.theta14,old.forecast.member,real,
     old.forecast.f14,.35);
  model.labelsApplied14++;
 }else{
  residual.mae56=residual.count56===0?Math.abs(real-old.forecast.net56):
    .95*residual.mae56+.05*Math.abs(real-old.forecast.net56);
  residual.count56++;
  if(!disableFuzzy)updateConsequents(model.theta56,old.forecast.member,real,
     old.forecast.f56,.28);
  model.labelsApplied56++;
 }
}
function addExtendedLabels(ds){
 const bank=ds.bank,samples=[],all=ds.byOrigin;
 for(const [utc,f] of ds.featuresByOrigin.entries()){
  const startTime=Date.parse(utc);
  const entryIndex=upperBound(bank,startTime);
  if(entryIndex>=bank.length)continue;
  const entry=bank[entryIndex];
  if(entry.ts-startTime>72*HR)continue;
  const exit14=findAtOrAfter(bank,entry.ts+14*DAY),
    exit56=findAtOrAfter(bank,entry.ts+56*DAY);
  const y14=exit14&&exit14.ts-(entry.ts+14*DAY)<=78*HR?
    100*((1-FEE)**2*exit14.p/entry.p-1):null;
  const y56=exit56&&exit56.ts-(entry.ts+56*DAY)<=78*HR?
    100*((1-FEE)**2*exit56.p/entry.p-1):null;
  samples.push({at:utc,ts:startTime,features:f,entry:entry.tt,
    exit14:exit14?.tt||null,exit14Ts:y14===null?null:exit14.ts,
    exit56:exit56?.tt||null,exit56Ts:y56===null?null:exit56.ts,
    y14,y56});
 }
 return {bank,samples,byOrigin:new Map(samples.map(s=>[s.at,s])),
   featuresByOrigin:ds.featuresByOrigin};
}
function upperBound(bank,time){
 let lo=0,hi=bank.length;
 while(lo<hi){let mid=(lo+hi)>>1;if(bank[mid].ts<=time)lo=mid+1;else hi=mid;}
 return lo;
}
function findAtOrAfter(bank,time){
 let lo=0,hi=bank.length;
 while(lo<hi){let mid=(lo+hi)>>1;if(bank[mid].ts<time)lo=mid+1;else hi=mid;}
 return bank[lo]||null;
}
// Models are trained by calendar-year as-of cutoffs ONLY, no evaluation-year
// examples until both target prices have matured. A pool of 2023 origins is
// sufficient for training a real neural network for 2024 onwards.
const NETWORKS=new WeakMap();
function frozenANN(ds,year){
 if(year<2024)return null;
 let memo=NETWORKS.get(ds);if(!memo){memo=new Map();NETWORKS.set(ds,memo);}
 if(memo.has(year))return memo.get(year);
 const cutoff=year+"-01-01T06:00:00Z";
 const train=chronologicalTraining(ds,cutoff);
 const net=train.length>=MIN_HISTORY?
    ANN.fit(train,{seed:17,epochs:70,lr:.006}):null;
 memo.set(year,net);return net;
}
function decision(pred,hold,position,opts){
 const cash=position==="CASH";
 const v56=pred.net56;
 const strength56=v56==null?0:v56;
 const confirmedBull=pred.regime.trend>-.05;
 const stress=pred.regime.stress>.72;
 // All predictions are already full roundtrip transaction-FEE-NET.
 // Hysteresis discourages 1.6% roundtrips on weak edges.
 const enoughHistory=pred.n14>=24&&(v56==null||pred.n56>=8);
 const longThreshold=opts.uncertainty?Math.max(1.8,.40*pred.uncertainty56):1.8;
 const wantGold=v56==null?
   enoughHistory&&pred.net14>Math.max(1.8,.35*pred.uncertainty14)&&confirmedBull:
   enoughHistory&&((
    strength56>longThreshold&&confirmedBull&&pred.net14>-.8)||
    (strength56>longThreshold+2.5&&pred.net14>-.35));
 const sell=v56==null? (stress||pred.net14< -1.2):
    (stress&&pred.net14<1.5||
    (strength56< -2&&pred.net14< -1.0));
 if(cash){
  if(wantGold&&hold.hoursSinceExit>=72&&!stress)return{position:"GOLD",reason:"MULTIHORIZON_CONFIRMED_NET_EDGE"};
  return {position:"CASH",reason:!enoughHistory?"WARMUP":"NO_FEE_NET_ADVANTAGE"};
 }
 if(sell && (hold.hoursHeld>=96 ||stress))return{position:"CASH",reason:stress?"RECURSIVE_STRESS_MEMORY":"TWO_HORIZON_RISK"};
 return {position:"GOLD",reason:"LONG_TREND_CONTINUATION"};
}
module.exports={ANN,RULES,FEATURE_COUNT,FEE,HR,DAY,create,gatedState,member,softmax,
 fuzzyPredict,updateConsequents,expertWeights,predict,applyOutcome,
 addExtendedLabels,frozenANN,decision,loadFullRows,dataset,chronologicalTraining};
